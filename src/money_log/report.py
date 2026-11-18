"""F4: 기준 월의 카테고리별 합계."""

from dataclasses import dataclass

from money_log.classifier import CATEGORIES
from money_log.models import Expense


@dataclass
class MonthReport:
    """카테고리별 합계(categories)와 총합(total)."""

    categories: dict[str, int]
    total: int


def monthly_report(expenses: list[Expense], year: int, month: int) -> MonthReport:
    """year년 month월 지출만 카테고리별로 합산한다. 오늘 날짜는 읽지 않는다."""
    categories = {category: 0 for category in CATEGORIES}

    for expense in expenses:
        if expense.date.year == year and expense.date.month == month:
            categories[expense.category] += expense.amount

    return MonthReport(categories, sum(categories.values()))