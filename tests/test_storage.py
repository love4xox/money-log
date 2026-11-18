"""F3: 지출을 CSV에 저장하고, 날짜순 목록으로 불러오기.

storage가 제공할 것 (구현은 아직 없음):
- Expense(date, item, amount, category)
- save_expense(expense, path): path의 CSV에 한 건 추가. 파일이 없으면 만든다.
- load_expenses(path): 날짜 오름차순, 같은 날은 저장된 순서.
  파일이 없거나 비어 있으면 빈 목록.

경로는 호출하는 쪽이 넘긴다. 테스트는 tmp_path만 써서 data/를 건드리지 않는다.
"""

import csv
from datetime import date

from money_log.storage import Expense, load_expenses, save_expense


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
    # 저장 순서는 날짜순이 아니다.
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
    # 같은 날 "택시"를 "김밥"보다 먼저 넣는다.
    # 항목 이름순이면 김밥이 앞이라, 입력 순과 구분된다.
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
