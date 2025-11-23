import logging

from config import PATH_TO_LOGGER


def get_logger(filename):
    """Получение логера для записи логов в файл"""
    logger = logging.getLogger(__name__)

    file_handler = logging.FileHandler(PATH_TO_LOGGER / filename)

    file_formatter = logging.Formatter("{asctime} {levelname}: {message}", style="{")
    file_handler.setFormatter(file_formatter)

    logger.addHandler(file_handler)
    logger.setLevel(logging.INFO)
    return logger
