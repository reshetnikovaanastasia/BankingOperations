import pandas as pd

from src.reports import spending_by_category


def create_test_transactions():
    """Создает тестовый DataFrame с транзакциями"""
    return pd.DataFrame(
        {
            "Дата операции": [
                "01.10.2023 10:00:00",
                "15.10.2023 14:30:00",
                "25.10.2023 18:45:00",
                "05.11.2023 09:15:00",
                "20.11.2023 16:20:00",
                "01.12.2023 11:30:00",
                "10.12.2023 13:45:00",
                "20.12.2023 19:00:00",
                "01.01.2024 12:00:00",
                "15.01.2024 17:30:00",
            ],
            "Категория": [
                "Еда",
                "Транспорт",
                "Еда",
                "Развлечения",
                "Еда",
                "Транспорт",
                "Еда",
                "Развлечения",
                "Еда",
                "Транспорт",
            ],
            "Сумма платежа": [-1000, -500, -1500, -2000, -1200, -600, -1800, -2500, -900, -550],
        }
    )


def test_spending_by_category_basic():
    """Тест базовой функциональности - траты по категории"""
    transactions = create_test_transactions()
    date = "2023-12-31 23:59:59"

    result = spending_by_category(transactions, "Еда", date)

    assert not result.empty
    assert "Месяц" in result.columns
    assert "Сумма трат" in result.columns
    assert "Количество операций" in result.columns
    assert "Категория" in result.columns
    assert all(result["Категория"] == "Еда")
