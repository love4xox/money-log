"""F4: 기준 월의 카테고리별 합계 및 월별 예산 비교."""

from datetime import date

import pytest

from money_log.classifier import CATEGORIES
from money_log.models import Expense
from money_log.report import MonthReport, monthly_report


def _zeros():
    return {category: 0 for category in CATEGORIES}


def test_sums_only_the_given_month_including_boundaries():
    # 기준 월은 2026년 11월. 1일과 말일은 포함하고, 바로 옆 달은 빼야 한다.
    expenses = [
        Expense(date(2026, 10, 31), "택시", 10000, "교통"),
        Expense(date(2026, 11, 1), "김밥", 3500, "식비"),
        Expense(date(2026, 11, 18), "커피", 4500, "카페"),
        Expense(date(2026, 11, 18), "라떼", 5000, "카페"),
        Expense(date(2026, 11, 30), "버스", 1500, "교통"),
        Expense(date(2026, 12, 1), "노트", 2000, "쇼핑"),
    ]

    report = monthly_report(expenses, 2026, 11)

    assert report == MonthReport(
        {
            "식비": 3500,
            "카페": 9500,
            "교통": 1500,
            "쇼핑": 0,
            "기타": 0,
        },
        14500,
    )


def test_previous_year_same_month_is_excluded():
    # 달만 같고 해가 다르면 2026년 11월 합계에 넣지 않는다.
    expenses = [
        Expense(date(2025, 11, 18), "커피", 4500, "카페"),
        Expense(date(2026, 11, 2), "김밥", 3500, "식비"),
    ]

    report = monthly_report(expenses, 2026, 11)

    assert report.categories["카페"] == 0
    assert report.categories["식비"] == 3500
    assert report.total == 3500


def test_all_categories_shown_and_total_matches():
    expenses = [
        Expense(date(2026, 11, 3), "간식", 2000, "기타"),
    ]

    report = monthly_report(expenses, 2026, 11)

    assert list(report.categories) == list(CATEGORIES)
    assert report.categories["기타"] == 2000
    assert report.categories["식비"] == 0
    assert report.categories["카페"] == 0
    assert report.categories["교통"] == 0
    assert report.categories["쇼핑"] == 0
    assert report.total == 2000
    assert report.total == sum(report.categories.values())


def test_uses_injected_month_not_today():
    # 오늘이 2026-11-18이어도, 넘긴 달이 10월이면 11월 지출은 빠진다.
    expenses = [
        Expense(date(2026, 11, 18), "커피", 4500, "카페"),
        Expense(date(2026, 10, 5), "김밥", 3500, "식비"),
    ]

    report = monthly_report(expenses, 2026, 10)

    assert report.categories["식비"] == 3500
    assert report.categories["카페"] == 0
    assert report.total == 3500


def test_month_with_no_expenses():
    expenses = [
        Expense(date(2026, 11, 18), "커피", 4500, "카페"),
    ]

    report = monthly_report(expenses, 2026, 8)

    assert report == MonthReport(_zeros(), 0)


def test_empty_input_is_all_zeros():
    report = monthly_report([], 2026, 11)

    assert report == MonthReport(_zeros(), 0)


def test_budget_under_limit():
    expenses = [
        Expense(date(2026, 11, 1), "김밥", 3500, "식비"),
        Expense(date(2026, 11, 18), "커피", 4500, "카페"),
    ]

    report = monthly_report(expenses, 2026, 11, budget=20000)

    assert report.total == 8000
    assert report.budget == 20000
    assert report.remaining == 12000
    assert report.is_over_budget is False


def test_budget_exact_match_is_not_over():
    expenses = [
        Expense(date(2026, 11, 1), "점심", 10000, "식비"),
    ]

    report = monthly_report(expenses, 2026, 11, budget=10000)

    assert report.remaining == 0
    assert report.is_over_budget is False


def test_budget_exceeded_sets_warning_and_negative_remaining():
    expenses = [
        Expense(date(2026, 11, 1), "택시", 15000, "교통"),
        Expense(date(2026, 11, 2), "점심", 10000, "식비"),
    ]

    report = monthly_report(expenses, 2026, 11, budget=20000)

    assert report.total == 25000
    assert report.budget == 20000
    assert report.remaining == -5000
    assert report.is_over_budget is True


def test_budget_must_be_positive():
    with pytest.raises(ValueError):
        monthly_report([], 2026, 11, budget=0)

    with pytest.raises(ValueError):
        monthly_report([], 2026, 11, budget=-5000)