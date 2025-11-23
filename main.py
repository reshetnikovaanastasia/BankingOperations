from config import PATH_TO_OPERATIONS
from src.reports import spending_by_category
from src.services import simple_search
from src.utils import read_excel
from src.views import main_page


def main():
    """Основная логика проекта и связывает функциональности между собой"""
    date = str(input("Введите дату в формате YYYY-MM-DD HH:MM:SS"))
    main_page_data = main_page(date)
    search_query = str(input("Введите строку, которую хотите найти"))
    simple_search_data = simple_search(search_query)
    category = str(input("Введите категорию, по которой хотите узнать траты за последние 3 месяца"))
    date2 = str(input("Введите дату, от которой хотите узнать траты за последние 3 месяца"))
    transactions = read_excel(PATH_TO_OPERATIONS)
    report = spending_by_category(transactions, category, date2)
    return main_page_data, simple_search_data, report
