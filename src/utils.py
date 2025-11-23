from datetime import datetime, time
import pandas as pd
from config import PATH_TO_OPERATIONS, PATH_TO_USER_SETTINGS
import json
# import logging
import os

import requests
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv('API_KEY')


def load_user_settings():
    """Загружает пользовательские настройки из файла user_settings.json"""
    with open(PATH_TO_USER_SETTINGS, 'r', encoding='utf-8') as f:
        settings = json.load(f)
        return {"user_currencies": settings.get("user_currencies", ["USD", "EUR"]),
                "user_stocks": settings.get("user_stocks", ["AAPL", "AMZN", "GOOGL"])}


def greeting():
    "Приветствие в зависимости от текущего времени"
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
    df = pd.read_excel(path)
    df["Дата операции"] = pd.to_datetime(df["Дата операции"], dayfirst=True)
    return df


def get_operations_with_range(operations_df, date_end):
    first_date = datetime.strptime(date_end, "%Y-%m-%d %H:%M:%S").strftime("%Y-%m-01 00:00:00")
    df_filter = operations_df[
        (operations_df["Дата операции"] >= first_date) & (operations_df["Дата операции"] <= date_end)]
    return df_filter


def get_cards(operations_df):
    operations_df = operations_range.copy()
    operations_df = operations_df[operations_df["Сумма платежа"] < 0]
    operations_df["Номер карты"] = operations_df["Номер карты"].apply(lambda x: x[1:])
    total_df = operations_df[["Номер карты", "Сумма операции", "Кэшбэк"]].groupby("Номер карты").sum().reset_index()
    total_df.rename(columns={"Номер карты": "last_digits", "Сумма операции": "total_spent", "Кэшбэк": "cashback"},
                    inplace=True)
    return total_df.to_dict("records")


def get_top_transactions(operetions_range):
    operations_df = operations_range.copy()
    operations_df["Дата операции"] = operations_df["Дата операции"].apply(lambda x: x.strftime("%d.%m.%Y"))
    sorted_transactions = operations_df.sort_values(by="Сумма операции с округлением", ascending=False).head()
    transactions_df = sorted_transactions[["Дата операции", "Сумма платежа", "Категория", "Описание"]]
    transactions_total_df = transactions_df.copy()
    transactions_total_df.rename(columns={"Дата операции": "date", "Сумма платежа": "amount", "Категория": "category",
                                          "Описание": "description"}, inplace=True)
    return transactions_total_df.to_dict("records")


def get_currency_rates():
    payload = {}
    cur_data = load_user_settings()
    currency = cur_data["user_currencies"]
    cur_dict = {}
    currency_list = []
    headers = {"apikey": API_KEY}
    for i in currency:
        url = f"https://api.apilayer.com/exchangerates_data/convert?to=RUB&from={i}&amount=1"
        response = requests.request("GET", url, headers=headers, data=payload)
        data = response.json()
        cur_dict["currency"] = i
        cur_dict["rate"] = round(float(data['result']), 2)
        currency_list.append(cur_dict)
        cur_dict = {}
    return currency_list


def get_stock_prices():
    stock_prices = []
    stock_data = load_user_settings()
    user_stocks = stock_data["user_stocks"]
    for stock in user_stocks:
        url = f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={stock}&apikey={API_KEY}"
        response = requests.get(url, timeout=10)
        data = response.json()
        quote = data.get("Global Quote", {})
        price = quote.get("05. price")
        stock_prices.append({"stock": stock, "price": round(float(price), 2)})
    return stock_prices
