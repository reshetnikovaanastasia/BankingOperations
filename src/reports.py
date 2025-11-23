import logging
from datetime import datetime, timedelta
from typing import Optional

import pandas as pd

from config import PATH_TO_LOGGER

logger = logging.getLogger(__name__)
file_handler = logging.FileHandler(PATH_TO_LOGGER / __file__)
file_formatter = logging.Formatter("{asctime} {levelname}: {message}", style="{")
file_handler.setFormatter(file_formatter)
logger.addHandler(file_handler)
logger.setLevel(logging.INFO)


def spending_by_category(transactions: pd.DataFrame, category: str, date: Optional[str] = None) -> pd.DataFrame:
    """Функция возвращает траты по заданной категории за последние три месяца (от переданной даты)"""
    if date is None:
        reference_date = datetime.now()
    else:
        try:
            # reference_date = datetime.strptime(date, "%Y-%m-%d")
            reference_date = datetime.strptime(date, "%Y-%m-%d %H:%M:%S")
            # reference_date = datetime.strptime(date, "%Y.%m.%d %H:%M:%S")
        except ValueError:
            print("Неверный формат даты. Используется текущая дата.")
            reference_date = datetime.now()
    start_date = reference_date - timedelta(days=90)
    # Преобразуем дату операции в datetime, если это еще не сделано
    transactions_copy = transactions.copy()
    transactions_copy["Дата операции"] = pd.to_datetime(
        transactions_copy["Дата операции"], format="%d.%m.%Y %H:%M:%S", errors="coerce"
    )
    category_mask = transactions_copy["Категория"].astype(str).str.contains(category, case=False, na=False)
    date_mask = (transactions_copy["Дата операции"] >= start_date) & (
        transactions_copy["Дата операции"] <= reference_date
    )
    spending_mask = transactions_copy["Сумма платежа"] < 0
    filtered_transactions = transactions_copy[category_mask & date_mask & spending_mask]

    if filtered_transactions.empty:
        return pd.DataFrame()
    # Создаем колонку с месяцем для группировки
    filtered_transactions = filtered_transactions.copy()
    filtered_transactions["Месяц"] = filtered_transactions["Дата операции"].dt.to_period("M")

    # Группируем по месяцам и суммируем траты
    monthly_spending = (
        filtered_transactions.groupby("Месяц")
        .agg({"Сумма платежа": "sum", "Дата операции": "count"})
        .rename(columns={"Сумма платежа": "Сумма трат", "Дата операции": "Количество операций"})
    )

    # Сортируем по месяцам
    logger.info("Выполняется сортировка по месяцам")
    monthly_spending = monthly_spending.sort_index()
    monthly_spending["Категория"] = category
    monthly_spending = monthly_spending.reset_index()
    monthly_spending["Месяц"] = monthly_spending["Месяц"].astype(str)
    monthly_spending["Сумма трат"] = monthly_spending["Сумма трат"].abs()
    logger.info("Вывод ответа программы")

    return monthly_spending
