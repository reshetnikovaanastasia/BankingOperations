import json
import logging
import os
from datetime import datetime, time

import pandas as pd
import requests
from dotenv import load_dotenv

from config import PATH_TO_LOGGER, PATH_TO_USER_SETTINGS

logger = logging.getLogger(__name__)
file_handler = logging.FileHandler(PATH_TO_LOGGER / __name__)
file_formatter = logging.Formatter("{asctime} {levelname}: {message}", style="{")
file_handler.setFormatter(file_formatter)
logger.addHandler(file_handler)
logger.setLevel(logging.INFO)

load_dotenv()
API_KEY = os.getenv("API_KEY")


def load_user_settings():
    """Загружает пользовательские настройки из файла user_settings.json"""
    logger.info("Загрузка пользовательских настроек")
    with open(PATH_TO_USER_SETTINGS, "r", encoding="utf-8") as f:
        settings = json.load(f)
        return {
            "user_currencies": settings.get("user_currencies", ["USD", "EUR"]),
            "user_stocks": settings.get("user_stocks", ["AAPL", "AMZN", "GOOGL"]),
        }


def greeting():
    "Приветствие в зависимости от текущего времени"
    logger.info("Определение времени суток в данный момент времени")
    now = datetime.now().time()
    if time(hour=4) <= now <= time(hour=11):
        return "Доброе утро"
    elif time(hour=11) < now <= time(hour=16):
        return "Добрый день"
    elif time(hour=16) < now <= time(hour=23):
        return "Добрый вечер"
    else:
        return "Доброй ночи"


def read_excel(path):
    """Чтение из excel файла"""
    logger.info("Чтение из excel файла")
    df = pd.read_excel(path)
    df["Дата операции"] = pd.to_datetime(df["Дата операции"], dayfirst=True)
    return df


def get_operations_with_range(operations_df, date_end):
    """Вывод операций в заданном временном промежутке
    Данные для анализа и вывода на веб-страницах — это данные с начала месяца, на который выпадает входящая дата,
    по входящую дату."""
    first_date = datetime.strptime(date_end, "%Y-%m-%d %H:%M:%S").strftime("%Y-%m-01 00:00:00")
    df_filter = operations_df[
        (operations_df["Дата операции"] >= first_date) & (operations_df["Дата операции"] <= date_end)
    ]
    logger.info("Вывод операций")
    return df_filter


def get_cards(operations_df):
    """Выдаёт по каждой карте:
    последние 4 цифры карты;
    общая сумма расходов;
    кешбэк (1 рубль на каждые 100 рублей)."""
    operations_df = operations_df.copy()
    logger.info("Выполняется поиск расходов")
    operations_df = operations_df[operations_df["Сумма платежа"] < 0]
    operations_df["Номер карты"] = operations_df["Номер карты"].apply(lambda x: x[1:])
    total_df = operations_df[["Номер карты", "Сумма операции", "Кэшбэк"]].groupby("Номер карты").sum().reset_index()
    total_df.rename(
        columns={"Номер карты": "last_digits", "Сумма операции": "total_spent", "Кэшбэк": "cashback"}, inplace=True
    )
    return total_df.to_dict("records")


def get_top_transactions(operаtions_range):
    """Выводит Топ-5 транзакций по сумме платежа"""
    operations_df = operаtions_range.copy()
    operations_df["Дата операции"] = operations_df["Дата операции"].apply(lambda x: x.strftime("%d.%m.%Y"))
    logger.info("Выполняется фильтрация по суммам платежей")
    sorted_transactions = operations_df.sort_values(by="Сумма операции с округлением", ascending=False).head()
    transactions_df = sorted_transactions[["Дата операции", "Сумма платежа", "Категория", "Описание"]]
    transactions_total_df = transactions_df.copy()
    transactions_total_df.rename(
        columns={
            "Дата операции": "date",
            "Сумма платежа": "amount",
            "Категория": "category",
            "Описание": "description",
        },
        inplace=True,
    )
    return transactions_total_df.to_dict("records")


def get_currency_rates():
    """Возвращает актуальные курсы валют"""
    payload = {}
    cur_data = load_user_settings()
    currency = cur_data["user_currencies"]
    cur_dict = {}
    currency_list = []
    headers = {"apikey": API_KEY}
    for i in currency:
        logger.info("Выполняется запрос-стоимость валюты")
        url = f"https://api.apilayer.com/exchangerates_data/convert?to=RUB&from={i}&amount=1"
        response = requests.request("GET", url, headers=headers, data=payload)
        data = response.json()
        cur_dict["currency"] = i
        cur_dict["rate"] = round(float(data["result"]), 2)
        currency_list.append(cur_dict)
        cur_dict = {}
    return currency_list


def get_stock_prices():
    """Возвращает актуальные курсы акций"""
    stock_prices = []
    stock_data = load_user_settings()
    user_stocks = stock_data["user_stocks"]
    for stock in user_stocks:
        logger.info("Выполняется запрос-стоимость акции")
        url = f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={stock}&apikey={API_KEY}"
        response = requests.get(url, timeout=10)
        data = response.json()
        quote = data.get("Global Quote", {})
        price = quote.get("05. price")
        if price is not None:
            stock_prices.append({"stock": stock, "price": round(float(price), 2)})
        else:
            stock_prices.append({"stock": stock, "price": None})
    return stock_prices
