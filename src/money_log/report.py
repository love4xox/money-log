"""F4: 기준 월의 카테고리별 합계 및 월별 예산 비교."""

from dataclasses import dataclass
from typing import Optional

from money_log.classifier import CATEGORIES
from money_log.models import Expense


@dataclass
class MonthReport:
    """카테고리별 합계(categories), 총합(total), 선택적 월 예산 정보."""

    categories: dict[str, int]
    total: int
    budget: Optional[int] = None
    remaining: Optional[int] = None
    is_over_budget: bool = False


def monthly_report(
    expenses: list[Expense],
    year: int,
    month: int,
    budget: Optional[int] = None,
) -> MonthReport:
    """year년 month월 지출을 합산하고, budget이 주어지면 잔액과 초과 여부를 계산한다."""
    if budget is not None and budget <= 0:
        raise ValueError(f"예산은 0보다 커야 합니다: {budget}")

    categories = {category: 0 for category in CATEGORIES}
    for expense in expenses:
        if expense.date.year == year and expense.date.month == month:
            categories[expense.category] += expense.amount

    total = sum(categories.values())
    if budget is None:
        return MonthReport(categories, total)

    remaining = budget - total
    return MonthReport(
        categories=categories,
        total=total,
        budget=budget,
        remaining=remaining,
        is_over_budget=total > budget,
    )