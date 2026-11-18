"""F3: 지출을 CSV에 저장하고, 날짜순 목록으로 불러오기 및 삭제하기."""

import csv
from datetime import date

import pytest

from money_log.storage import Expense, delete_expense, load_expenses, save_expense


def test_save_writes_csv_at_given_path(tmp_path):
    path = tmp_path / "expenses.csv"
    expense = Expense(date(2026, 11, 18), "점심 김밥", 3500, "식비")

    save_expense(expense, path)

    assert path.is_file()
    with path.open(encoding="utf-8", newline="") as f:
        cells = [cell for row in csv.reader(f) for cell in row]
    assert "2026-11-18" in cells
    assert "점심 김밥" in cells
    assert "3500" in cells
    assert "식비" in cells


def test_save_then_load_roundtrip(tmp_path):
    path = tmp_path / "expenses.csv"
    expense = Expense(date(2026, 11, 18), "커피", 4500, "카페")

    save_expense(expense, path)

    assert load_expenses(path) == [expense]


def test_save_appends(tmp_path):
    path = tmp_path / "expenses.csv"
    first = Expense(date(2026, 11, 1), "커피", 4500, "카페")
    second = Expense(date(2026, 11, 2), "버스", 1500, "교통")

    save_expense(first, path)
    save_expense(second, path)

    assert [e.item for e in load_expenses(path)] == ["커피", "버스"]


def test_load_sorts_by_date_ascending(tmp_path):
    path = tmp_path / "expenses.csv"
    for expense in (
        Expense(date(2026, 11, 18), "커피", 4500, "카페"),
        Expense(date(2026, 11, 16), "김밥", 3500, "식비"),
        Expense(date(2026, 11, 17), "노트", 2000, "쇼핑"),
    ):
        save_expense(expense, path)

    assert [e.date for e in load_expenses(path)] == [
        date(2026, 11, 16),
        date(2026, 11, 17),
        date(2026, 11, 18),
    ]


def test_same_day_keeps_input_order(tmp_path):
    path = tmp_path / "expenses.csv"
    for expense in (
        Expense(date(2026, 11, 18), "커피", 4500, "카페"),
        Expense(date(2026, 11, 16), "택시", 10000, "교통"),
        Expense(date(2026, 11, 16), "김밥", 3500, "식비"),
        Expense(date(2026, 11, 18), "버스", 1500, "교통"),
    ):
        save_expense(expense, path)

    assert [(e.date, e.item) for e in load_expenses(path)] == [
        (date(2026, 11, 16), "택시"),
        (date(2026, 11, 16), "김밥"),
        (date(2026, 11, 18), "커피"),
        (date(2026, 11, 18), "버스"),
    ]


def test_load_missing_file_returns_empty(tmp_path):
    path = tmp_path / "missing.csv"

    assert not path.exists()
    assert load_expenses(path) == []


def test_load_empty_file_returns_empty(tmp_path):
    path = tmp_path / "empty.csv"
    path.write_text("", encoding="utf-8")

    assert load_expenses(path) == []


def test_delete_expense_removes_item_and_returns_it(tmp_path):
    path = tmp_path / "expenses.csv"
    save_expense(Expense(date(2026, 11, 2), "점심", 8000, "식비"), path)
    save_expense(Expense(date(2026, 11, 1), "커피", 4500, "카페"), path)
    save_expense(Expense(date(2026, 11, 3), "택시", 15000, "교통"), path)

    deleted = delete_expense(2, path)

    assert deleted == Expense(date(2026, 11, 2), "점심", 8000, "식비")
    remaining = load_expenses(path)
    assert len(remaining) == 2
    assert [e.item for e in remaining] == ["커피", "택시"]


def test_delete_expense_raises_when_out_of_range(tmp_path):
    path = tmp_path / "expenses.csv"
    save_expense(Expense(date(2026, 11, 1), "커피", 4500, "카페"), path)

    with pytest.raises(IndexError):
        delete_expense(0, path)

    with pytest.raises(IndexError):
        delete_expense(2, path)


def test_delete_expense_raises_when_file_missing(tmp_path):
    path = tmp_path / "missing.csv"
    with pytest.raises(IndexError):
        delete_expense(1, path)