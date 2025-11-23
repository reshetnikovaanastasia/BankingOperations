import json
import logging

from config import PATH_TO_OPERATIONS,PATH_TO_LOGGER
from src.utils import (get_cards, get_currency_rates, get_operations_with_range, get_stock_prices,
                       get_top_transactions, greeting, read_excel)

logger = logging.getLogger(__name__)
file_handler = logging.FileHandler(PATH_TO_LOGGER /  __name__)
file_formatter = logging.Formatter("{asctime} {levelname}: {message}", style="{")
file_handler.setFormatter(file_formatter)
logger.addHandler(file_handler)
logger.setLevel(logging.INFO)


def main_page(date):
    """Набор функций (greeting, read_excel, get_operations_with_range, get_cards, get_top_transactions,
    get_currency_rates, get_stock_prices) в главной функции, принимающей на вход строку
    с датой и временем в формате YYYY-MM-DD HH:MM:SS и возвращающую JSON-ответ со следующими данными:
    из функций"""
    logger.info("Запуск череды функций страницы 'Главная'")
    answer = {}
    answer["greeting"] = greeting()
    data_df = read_excel(PATH_TO_OPERATIONS)
    oparations_range = get_operations_with_range(data_df, date)
    answer["cards"] = get_cards(oparations_range)
    answer["top_transactions"] = get_top_transactions(oparations_range)
    answer["currency_rates"] = get_currency_rates()
    answer["stock_prices"] = get_stock_prices()

    return json.dumps(answer, ensure_ascii=False, indent=4)
