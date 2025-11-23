import json
from unittest.mock import patch

import pandas as pd

from src.services import simple_search


def test_simple_search_by_description():
    """Тест поиска по описанию"""
    test_data = {
        "Описание": ["Покупка в магазине", "Оплата такси", "Покупка продуктов", "Кафе"],
        "Категория": ["Супермаркет", "Транспорт", "Супермаркет", "Ресторан"],
        "Сумма": [-1000, -500, -1500, -800],
        "Дата операции": ["2023-10-01", "2023-10-02", "2023-10-03", "2023-10-04"],
    }

    with patch("pandas.read_excel") as mock_read_excel:
        mock_read_excel.return_value = pd.DataFrame(test_data)

        result = simple_search("такси")
        result_data = json.loads(result)

        assert len(result_data) == 1
        assert result_data[0]["Описание"] == "Оплата такси"
        assert result_data[0]["Категория"] == "Транспорт"
