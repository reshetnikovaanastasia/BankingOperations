from datetime import datetime
from unittest.mock import patch

import pandas as pd
import pytest


@pytest.fixture
def sample_operations_df():
    """Фикстура с тестовыми данными операций"""
    test_data = {
        "Дата операции": [
            "2023-10-01 10:00:00",
            "2023-10-15 14:30:00",
            "2023-10-31 23:59:59",
            "2023-09-30 18:00:00",
            "2023-11-01 09:00:00",
        ],
        "Сумма": [1000, 2000, 3000, 4000, 5000],
        "Категория": ["Еда", "Транспорт", "Развлечения", "Еда", "Транспорт"],
    }
    df = pd.DataFrame(test_data)
    df["Дата операции"] = pd.to_datetime(df["Дата операции"])
    return df


@pytest.fixture
def sample_df():
    return pd.DataFrame(
        {
            "Номер карты": ["*1234", "*5678", "*1234", "*9012", "*5678", "*1234"],
            "Сумма платежа": [-1000, -2500, -1500, -500, -2000, 3000],
            "Сумма операции": [-1000, -2500, -1500, -500, -2000, 3000],
            "Кэшбэк": [10, 25, 15, 5, 20, 0],
        }
    )


@pytest.fixture
def sample_operations_df2():
    """Фикстура с тестовыми данными операций"""
    test_data = {
        "Дата операции": [
            datetime(2023, 10, 1, 10, 0, 0),
            datetime(2023, 10, 15, 14, 30, 0),
            datetime(2023, 10, 10, 9, 15, 0),
            datetime(2023, 10, 5, 16, 45, 0),
            datetime(2023, 10, 20, 11, 20, 0),
            datetime(2023, 10, 25, 13, 0, 0),
        ],
        "Сумма операции с округлением": [5000, 15000, 8000, 12000, 3000, 20000],
        "Сумма платежа": [-5000, -15000, -8000, -12000, -3000, -20000],
        "Категория": ["Еда", "Транспорт", "Развлечения", "Еда", "Транспорт", "Развлечения"],
        "Описание": ["Супермаркет", "Такси", "Кино", "Ресторан", "Метро", "Концерт"],
    }
    return pd.DataFrame(test_data)


@pytest.fixture
def mock_user_settings():
    """Мок для пользовательских настроек"""
    with patch("src.utils.load_user_settings") as mock:
        mock.return_value = {"user_currencies": ["USD", "EUR", "GBP"], "user_stocks": ["AAPL", "AMZN"]}
        yield mock


@pytest.fixture
def mock_requests():
    """Мок для requests"""
    with patch("src.utils.requests.request") as mock:
        yield mock


@pytest.fixture
def mock_requests2():
    """Мок для requests.get"""
    with patch("src.utils.requests.get") as mock:
        yield mock
