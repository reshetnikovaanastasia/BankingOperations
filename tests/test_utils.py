from datetime import datetime
from unittest.mock import MagicMock, mock_open, patch

import pandas as pd
from freezegun import freeze_time

from config import PATH_TO_USER_SETTINGS
from src.utils import (get_cards, get_currency_rates, get_operations_with_range, get_stock_prices,
                       get_top_transactions, greeting, load_user_settings, read_excel)


def test_load_user_settings_success():
    """Тест успешной загрузки настроек"""
    with (
        patch(
            "builtins.open",
            mock_open(read_data='{"user_currencies": ["USD", "EUR", "GBP"], "user_stocks": ["AAPL", "TSLA"]}'),
        ) as mock_file,
        patch("json.load") as mock_json_load,
    ):
        mock_json_load.return_value = {"user_currencies": ["USD", "EUR", "GBP"], "user_stocks": ["AAPL", "TSLA"]}

        result = load_user_settings()

        mock_file.assert_called_once_with(PATH_TO_USER_SETTINGS, "r", encoding="utf-8")
        mock_json_load.assert_called_once()

        expected_result = {"user_currencies": ["USD", "EUR", "GBP"], "user_stocks": ["AAPL", "TSLA"]}
        assert result == expected_result


def test_greeting():
    with freeze_time("2025-07-05 00:05:12"):
        assert greeting() == "Доброй ночи"
    with freeze_time("2025-07-05 08:05:12"):
        assert greeting() == "Доброе утро"
    with freeze_time("2025-07-05 12:05:12"):
        assert greeting() == "Добрый день"
    with freeze_time("2025-07-05 17:05:12"):
        assert greeting() == "Добрый вечер"


def test_read_excel_success():
    """Тест успешного чтения Excel файла"""
    with patch("pandas.read_excel") as mock_read_excel:
        test_data = {"Дата операции": ["01.01.2023", "15.03.2023"], "Сумма": [1000, 2000]}
        mock_read_excel.return_value = pd.DataFrame(test_data)

        result = read_excel("test_path.xlsx")

        mock_read_excel.assert_called_once_with("test_path.xlsx")
        assert pd.api.types.is_datetime64_any_dtype(result["Дата операции"])
        assert result["Дата операции"].iloc[0] == datetime(2023, 1, 1)
        assert result["Дата операции"].iloc[1] == datetime(2023, 3, 15)


def test_get_operations_with_range(sample_operations_df):
    result = get_operations_with_range(sample_operations_df, "2023-10-31 23:59:59")

    assert len(result) == 3
    expected_dates = ["2023-10-01 10:00:00", "2023-10-15 14:30:00", "2023-10-31 23:59:59"]
    for expected_date in expected_dates:
        assert any(result["Дата операции"] == pd.to_datetime(expected_date))


def test_get_cards(sample_df):
    result = get_cards(sample_df)

    assert len(result) == 3
    assert isinstance(result, list)

    card_1234 = next(item for item in result if item["last_digits"] == "1234")
    assert card_1234["total_spent"] == -2500
    assert card_1234["cashback"] == 25


def test_returns_top_5_transactions(sample_operations_df2):
    result = get_top_transactions(sample_operations_df2)

    assert len(result) == 5
    assert isinstance(result, list)


def test_sorted_by_amount_descending(sample_operations_df2):
    result = get_top_transactions(sample_operations_df2)

    amounts = [transaction["amount"] for transaction in result]
    assert amounts == sorted(amounts)


def test_correct_top_transactions(sample_operations_df2):
    result = get_top_transactions(sample_operations_df2)

    assert result[0]["amount"] == -20000
    assert result[0]["category"] == "Развлечения"
    assert result[0]["description"] == "Концерт"


def test_date_format_conversion(sample_operations_df2):
    result = get_top_transactions(sample_operations_df2)

    for transaction in result:
        assert "." in transaction["date"]
        parts = transaction["date"].split(".")
        assert len(parts) == 3
        assert len(parts[0]) == 2  # день
        assert len(parts[1]) == 2  # месяц
        assert len(parts[2]) == 4  # год


def test_result_structure(sample_operations_df2):
    """Тест структуры возвращаемых данных"""
    result = get_top_transactions(sample_operations_df2)

    for transaction in result:
        assert all(key in transaction for key in ["date", "amount", "category", "description"])
        assert isinstance(transaction["date"], str)
        assert isinstance(transaction["amount"], (int, float))
        assert isinstance(transaction["category"], str)
        assert isinstance(transaction["description"], str)


def test_successful_currency_rates(mock_user_settings, mock_requests):
    """Тест успешного получения курсов валют"""
    # Настраиваем мок responses
    mock_responses = [
        MagicMock(json=lambda: {"result": 90.50}),  # USD to RUB
        MagicMock(json=lambda: {"result": 100.25}),  # EUR to RUB
        MagicMock(json=lambda: {"result": 115.75}),  # GBP to RUB
    ]
    mock_requests.side_effect = mock_responses

    result = get_currency_rates()

    expected_result = [
        {"currency": "USD", "rate": 90.50},
        {"currency": "EUR", "rate": 100.25},
        {"currency": "GBP", "rate": 115.75},
    ]

    assert result == expected_result
    assert len(result) == 3


def test_get_stock_prices(mock_user_settings, mock_requests2):
    """Тест успешного получения цен акций"""
    # Настраиваем мок responses
    mock_responses = [
        MagicMock(json=lambda: {"Global Quote": {"05. price": "150.25"}}),  # AAPL
        MagicMock(json=lambda: {"Global Quote": {"05. price": "2800.75"}}),  # AMZN
    ]
    mock_requests2.side_effect = mock_responses

    result = get_stock_prices()

    expected_result = [
        {"stock": "AAPL", "price": 150.25},
        {"stock": "AMZN", "price": 2800.75},
    ]

    assert result == expected_result
    assert len(result) == 2
