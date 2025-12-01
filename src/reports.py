import json
import logging
from datetime import datetime, timedelta
from typing import Optional

import pandas as pd

from config import PATH_TO_LOGGER, PATH_TO_REPORTS

logger = logging.getLogger(__name__)
file_handler = logging.FileHandler(PATH_TO_LOGGER / __name__)
file_formatter = logging.Formatter("{asctime} {levelname}: {message}", style="{")
file_handler.setFormatter(file_formatter)
logger.addHandler(file_handler)
logger.setLevel(logging.INFO)


def report_to_file(*args, filename: str = None):
    """
    Декоратор для записи результатов функции-отчета в файл

    Args:
        filename (str, optional): Имя файла для сохранения.
                                  Если не указано, генерируется автоматически.
    """

    def decorator(func):
        def wrapper(*args, **kwargs):
            # Вызываем оригинальную функцию
            result = func(*args, **kwargs)

            # Определяем имя файла
            if filename is None:
                file_name = PATH_TO_REPORTS

            # Сохраняем результат в файл
            try:
                if isinstance(result, pd.DataFrame):
                    # Для DataFrame сохраняем в JSON
                    result.to_json(file_name, orient='records', force_ascii=False, indent=2)
                elif isinstance(result, dict) or isinstance(result, list):
                    # Для словарей и списков
                    with open(file_name, 'w', encoding='utf-8') as f:
                        json.dump(result, f, ensure_ascii=False, indent=2)
                print(f"Отчет сохранен в файл: {file_name}")

            except Exception as e:
                print(f"Ошибка при сохранении отчета: {e}")

            return result

        return wrapper

    return decorator


@report_to_file()
def spending_by_category(transactions: pd.DataFrame, category: str, date: Optional[str] = None) -> pd.DataFrame:
    """Функция возвращает траты по заданной категории за последние три месяца (от переданной даты)"""
    if date is None:
        reference_date = datetime.now()
    else:
        try:
            reference_date = datetime.strptime(date, "%Y-%m-%d %H:%M:%S")
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
