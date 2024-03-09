import os
import time
from pathlib import Path

from adbutils import AdbClient

from config_data.conf import get_my_loggers, conf

logger, *other = get_my_loggers()

BASE_DIR = Path(__file__).resolve().parent

SCREEN_FOLDER = Path(conf.adb.SCREEN_FOLDER)
TARGET_DIR = BASE_DIR / 'atb_screenshots'


def get_file_list(directory, adb_device):
    """
    Получение списка файлов из директории с их размерами
    """
    command = f'ls -l {directory}'
    files_output = adb_device.shell(command)
    files = files_output.splitlines()
    file_list = []
    for file in files:
        if file.startswith('total'):
            continue
        items = file.split()
        if len(items) >= 5:
            file_name = items[-1]
            file_size = int(items[4])
            file_list.append((file_name, file_size))
    return file_list


def main():
    adb_client = AdbClient(host=os.getenv('HOST'), port=5037, socket_timeout=None)
    while True:
        try:
            start = time.perf_counter()
            # adb_client = AdbClient(host="host.docker.internal", port=5037)
            # adb_client = AdbClient(host="127.0.0.1", port=5037)
            adb_client = AdbClient(host=os.getenv('HOST'), port=5037, socket_timeout=1)
            adb_devices = adb_client.device_list()
            PHONES = conf.adb.ATB_PHONES
            ATB_NAMES = conf.adb.ATB_NAMES
            logger.info(f'Подключены устройства: {adb_devices}')
            for adb_device in adb_devices:
                logger.debug(f'Проверяем устройство {adb_device}')
                device_name = adb_device.info.get('serialno')
                logger.debug(f'Прочитано имя: {device_name}')
                if device_name in PHONES:
                    phone_num = PHONES.index(device_name)
                    phone_name = ATB_NAMES[phone_num]
                    logger.info(f'Обнаружен телефон из списка ATB: {phone_name}')
                    try:
                        data = get_file_list(SCREEN_FOLDER.as_posix(), adb_device)
                        logger.info(f'Количество скринов: {len(data)}')
                        logger.debug(str(data))
                        # if data:
                        for one_file in data:
                            # file, size = data[0][0], data[0][1]
                            file, size = one_file[0], one_file[1]
                            file_path = SCREEN_FOLDER / file
                            if size > 0:
                                logger.debug(f'Скачиваем файл {file} {size} кб')
                                file_name = file.replace('.jpg', f'_from_{device_name}.jpg')
                                target_path = TARGET_DIR / file_name
                                downloaded = adb_device.sync.pull(file_path.as_posix(), target_path.as_posix())
                                if downloaded:
                                    logger.debug(f'Удаляем файл {file}: {downloaded}')
                                    adb_device.shell(f'rm {file_path.as_posix()}')

                    except Exception as err:
                        logger.error(err, exc_info=False)
            delta = round(time.perf_counter() - start, 2)
            logger.info(f'Время цикла: {delta}\ndelay{"*" * int(delta)}')
            time.sleep(3)
        except Exception as err:
            logger.info(err)
            logger.error(err, exc_info=True)
            time.sleep(5)


if __name__ == '__main__':
    main()
