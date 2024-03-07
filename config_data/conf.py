import os
from dataclasses import dataclass
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent

"""
format = "%(asctime)s - %(levelname)s - %(funcName)s: %(lineno)d - %(message)s"
"""

LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,

    'formatters': {
        'default_formatter': {
            # 'format': "%(asctime)s - [%(levelname)8s] - %(name)s - (%(filename)s).%(funcName)s(%(lineno)d) - %(message)s"
            'format': "%(asctime)s - %(levelname)s - %(funcName)s: %(lineno)d - %(message)s"
        },
    },

    'handlers': {
        'stream_handler': {
            'class': 'logging.StreamHandler',
            'formatter': 'default_formatter',
        },
        'rotating_file_handler': {
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': f'{BASE_DIR / "logs" / "bot"}.log',
            'backupCount': 10,
            'maxBytes': 10 * 1024 * 1024,
            'mode': 'a',
            'encoding': 'UTF-8',
            'formatter': 'default_formatter',
        },
        'errors_file_handler': {
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': f'{BASE_DIR / "logs" / "errors_bot"}.log',
            'backupCount': 2,
            'maxBytes': 10 * 1024 * 1024,
            'mode': 'a',
            'encoding': 'UTF-8',
            'formatter': 'default_formatter',
        },
    },
    'loggers': {
        'bot_logger': {
            'handlers': ['stream_handler', 'rotating_file_handler'],
            'level': 'INFO',
            'propagate': True
        },
        'errors_logger': {
            'handlers': ['stream_handler', 'errors_file_handler'],
            'level': 'DEBUG',
            'propagate': True
        },
    }
}


# @dataclass
# class Ftp:
#     SCREEN_FOLDER: str
#     FTP_HOST: str
#     FTP_PORT: int
#     FTP_USER: str
#     FTP_PASSWD: str
#     FTP_TIMEOUT: float
#     WORKER: str
#     ENDPOINT: str


@dataclass
class ADB:
    SCREEN_FOLDER: str
    WORKER: str
    M10_ENDPOINT: str
    ATB_ENDPOINT: str
    OCR_ENDPOINT: str
    M10_PHONES: list
    ATB_PHONES: list
    ATB_NAMES: list


@dataclass
class Config:
    # ftp: Ftp
    adb: ADB


def load_config(path=None) -> Config:
    return Config(
        # ftp=Ftp(SCREEN_FOLDER=os.getenv('SCREEN_FOLDER'),
        #                   FTP_HOST=os.getenv('FTP_HOST'),
        #                   FTP_PORT=int(os.getenv('FTP_PORT')),
        #                   FTP_USER=os.getenv('FTP_USER'),
        #                   FTP_PASSWD=os.getenv('FTP_PASSWD'),
        #                   FTP_TIMEOUT=float(os.getenv('FTP_TIMEOUT')),
        #                   WORKER=os.getenv('WORKER'),
        #                   ENDPOINT=os.getenv('ENDPOINT'),
        #                   ),
        adb=ADB(SCREEN_FOLDER=os.getenv('SCREEN_FOLDER'),
                WORKER=os.getenv('WORKER'),
                M10_ENDPOINT=os.getenv('M10_ENDPOINT'),
                ATB_ENDPOINT=os.getenv('ATB_ENDPOINT'),
                OCR_ENDPOINT=os.getenv('OCR_ENDPOINT'),
                M10_PHONES=os.getenv('M10_PHONES').split(','),
                ATB_PHONES=os.getenv('ATB_PHONES').split(','),
                ATB_NAMES=os.getenv('ATB_NAMES').split(','),
                ),
    )


load_dotenv()

conf = load_config()
print(conf)

def get_my_loggers():
    import logging.config
    logging.config.dictConfig(LOGGING_CONFIG)
    return logging.getLogger('bot_logger'), logging.getLogger('errors_logger'), logging.getLogger('table1_logger'),  logging.getLogger('table2_logger')
