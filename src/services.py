import datetime
import json
import pandas as pd
import logging
from config import PATH_TO_OPERATIONS


def simple_search(search_query):
    """Пользователь передает строку для поиска, возвращается JSON-ответ со всеми транзакциями,
    содержащими запрос в описании или категории."""
    data_df = pd.read_excel(PATH_TO_OPERATIONS)
    search_lower = search_query.lower()
    mask = (
            data_df['Описание'].astype(str).str.lower().str.contains(search_lower, na=False) |
            data_df['Категория'].astype(str).str.lower().str.contains(search_lower, na=False)
    )
    found_operations = data_df[mask]
    if found_operations.empty:
        return []
    d = found_operations.to_dict('records')
    return json.dumps(d, ensure_ascii=False, indent=2)


print(simple_search("СитиДрайв"))
