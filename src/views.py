import requests
from src.utils import (greeting, read_excel, get_operations_with_range, get_cards, get_top_transactions,
                       get_currency_rates, get_stock_prices)
from config import PATH_TO_OPERATIONS
import json


def main_page(date):
    answer = {}
    answer["greeting"] = greeting()
    data_df = read_excel(PATH_TO_OPERATIONS)
    oparations_range = get_operations_with_range(data_df, date)
    answer["cards"] = get_cards(oparations_range)
    answer["top_transactions"] = get_top_transactions(oparations_range)
    answer["currency_rates"] = get_currency_rates()
    answer["stock_prices"] = get_stock_prices()

    return json.dumps(answer, ensure_ascii=False, indent=4)


print(main_page("2021-12-12 12:12:12"))
