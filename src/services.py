import json
import logging

import pandas as pd

from config import PATH_TO_OPERATIONS, PATH_TO_LOGGER

logger = logging.getLogger(__name__)
file_handler = logging.FileHandler(PATH_TO_LOGGER / __file__)
file_formatter = logging.Formatter("{asctime} {levelname}: {message}", style="{")
file_handler.setFormatter(file_formatter)
logger.addHandler(file_handler)
logger.setLevel(logging.INFO)


def simple_search(search_query):
    """Пользователь передает строку для поиска, возвращается JSON-ответ со всеми транзакциями,
    содержащими запрос в описании или категории."""
    data_df = pd.read_excel(PATH_TO_OPERATIONS)
    search_lower = search_query.lower()
    mask = data_df["Описание"].astype(str).str.lower().str.contains(search_lower, na=False) | data_df[
        "Категория"
    ].astype(str).str.lower().str.contains(search_lower, na=False)
    found_operations = data_df[mask]
    if found_operations.empty:
        logger.warning("Отсутствует запрос в описании или категории")
        return []
    d = found_operations.to_dict("records")
    logger.info("Вывод ответа программы")
    return json.dumps(d, ensure_ascii=False, indent=2)
