import json
from unittest.mock import MagicMock, patch

from src.views import main_page


def test_main_page_success_complete_mock():
    """Тест успешного выполнения главной функции с полным моком"""
    test_date = "2023-10-15 12:00:00"

    with (
        patch("src.utils.greeting") as mock_greeting,
        patch("src.utils.read_excel") as mock_read_excel,
        patch("src.utils.get_operations_with_range") as mock_get_operations,
        patch("src.utils.get_cards") as mock_get_cards,
        patch("src.utils.get_top_transactions") as mock_get_top,
        patch("src.utils.get_currency_rates") as mock_get_currency,
        patch("src.utils.get_stock_prices") as mock_get_stocks,
        patch("src.utils.load_user_settings") as mock_load_settings,
        patch("src.utils.requests.request") as mock_requests,
    ):
        # Настройка моков для всех функций
        mock_greeting.return_value = "Добрый вечер!"

        mock_df = MagicMock()
        mock_read_excel.return_value = mock_df

        mock_operations_range = MagicMock()
        mock_get_operations.return_value = mock_operations_range

        mock_get_cards.return_value = [{"last_digits": "1234", "total_spent": -5000, "cashback": 50}]

        mock_get_top.return_value = [
            {"date": "15.10.2023", "amount": -10000, "category": "Еда", "description": "Ресторан"}
        ]

        # Настройка моков для get_currency_rates
        mock_load_settings.return_value = {
            "user_currencies": ["USD", "EUR"],
            "user_stocks": ["AAPL", "GOOGL"]
        }
        mock_requests.return_value = MagicMock(json=lambda: {"result": 90.50})
        mock_get_currency.return_value = [{"currency": "USD", "rate": 90.50}]

        # Настройка моков для get_stock_prices
        mock_get_stocks.return_value = [{"stock": "AAPL", "price": 150.25}]

        # Вызов функции
        result = main_page(test_date)

        # Проверка результата
        result_dict = json.loads(result)

        assert "greeting" in result_dict
        assert "cards" in result_dict
        assert "top_transactions" in result_dict
        assert "currency_rates" in result_dict
        assert "stock_prices" in result_dict
