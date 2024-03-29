import json
import pickle
import time

import requests
from urllib3.exceptions import NewConnectionError

from config_data.conf import get_my_loggers
from config_data.conf import BASE_DIR, conf

path = BASE_DIR / 'atb_screenshots'

logger, err_log, *other = get_my_loggers()

ATB_ENDPOINT = conf.adb.ATB_ENDPOINT
OCR_ENDPOINT = conf.adb.OCR_ENDPOINT
WORKER = conf.adb.WORKER
PHONES = conf.adb.ATB_PHONES
ATB_NAMES = conf.adb.ATB_NAMES


def phone_serial(file):
    """Достает серийные номер из пути изображения"""
    from_part = file.split('_from_')
    if len(from_part) == 2:
        return from_part[1][:-4]
    return 'unknown'


def get_phone_name(serial):
    for num, phone in enumerate(PHONES):
        if serial == phone:
            return ATB_NAMES[num]
    return 'unknown'


def main():
    while True:
        try:
            global_start = time.perf_counter()
            files = list(path.glob('*.jpg'))
            if files:
                logger.info(f'Обнаружены файлов для распознавания:\n{len(files)}')
            else:
                time.sleep(1)
            for file in files:
                try:
                    start = time.perf_counter()
                    size = file.lstat().st_size
                    if size > 300000:
                        logger.debug(f'Удаляем большой файл {file.name}')
                        file.unlink()
                        pass

                    elif size > 0:
                        logger.info(f'Отправляем {file.name, size, bool(size>0)}')
                        with open(file, "rb") as binary:
                            screen = {'image': binary.read()}
                            response = requests.post(OCR_ENDPOINT, data={'name': file.name, 'worker': WORKER, 'oem': '1', 'psm': '7', 'lang': 'eng'}, files=screen, timeout=10)
                            pay = response.reason
                            logger.debug(f'{response.status_code} ({time.perf_counter() - start})')
                            logger.info(f'Результа со скрина: {pay} ({time.perf_counter() - start})')
                        if response.status_code in [200, 201]:
                            # Отправляем платеж
                            # print(file.name)
                            serial = phone_serial(file.name)
                            # logger.info(f'Отправляем скрин с телефона {serial}')
                            # print(serial)
                            response = requests.post(ATB_ENDPOINT, data={'pay': pay,
                                                                         'worker': WORKER,
                                                                         'phone_name': get_phone_name(serial),
                                                                         'type': 'bank1',
                                                                         'name': file.name,
                                                                         }, files=screen, timeout=10)
                            if response.status_code in [200, 201]:
                                file.unlink()
                                logger.info(f'Результат отправлен, Скрин удален')
                        elif response.status_code in [400]:
                            file.unlink()
                            logger.debug(f'Скрин не распознан и удален')
                        elif response.status_code in [502]:
                            logger.info('Ошибка на сервере')
                            time.sleep(5)
                except NewConnectionError:
                    logger.info('Ошибка соединения')
                    time.sleep(5)
                except Exception as err:
                    logger.info(f'Ошибка обработки файла {file.name}: {err}')
                    err_log.error(err, exc_info=True)
                    time.sleep(0.1)

            logger.info(f'Все файлы обработаны. Общее время: {time.perf_counter() - global_start}\n\n')
            time.sleep(0.5)

        except Exception as err:
            time.sleep(1)
            logger.eror(err)
            err_log.error(err, exc_info=True)


if __name__ == '__main__':
    main()
