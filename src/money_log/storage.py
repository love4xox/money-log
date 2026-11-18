"""F3: 지출을 CSV에 저장하고, 날짜순으로 불러오며 삭제한다.

Expense는 models에 두고, 테스트가 storage에서 import할 수 있게 여기서도 내보낸다.
"""

import csv
from datetime import date
from pathlib import Path

from money_log.models import Expense

__all__ = ["Expense", "delete_expense", "load_expenses", "save_expense"]

_COLUMNS = ("date", "item", "amount", "category")


def save_expense(expense: Expense, path: Path) -> None:
    """path의 CSV 끝에 지출 한 건을 추가한다. 파일이 없으면 헤더와 함께 만든다."""
    path = Path(path)
    new_file = not path.exists() or path.stat().st_size == 0
    with path.open("a", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        if new_file:
            writer.writerow(_COLUMNS)
        writer.writerow(
            [
                expense.date.isoformat(),
                expense.item,
                expense.amount,
                expense.category,
            ]
        )


def load_expenses(path: Path) -> list[Expense]:
    """CSV를 읽어 날짜 오름차순으로 돌려준다. 같은 날은 파일에 저장된 순서.

    파일이 없거나 비어 있으면 빈 목록.
    """
    path = Path(path)
    if not path.is_file() or path.stat().st_size == 0:
        return []

    expenses: list[Expense] = []
    with path.open(encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if not row or not row.get("date"):
                continue
            expenses.append(
                Expense(
                    date.fromisoformat(row["date"]),
                    row["item"],
                    int(row["amount"]),
                    row["category"],
                )
            )

    expenses.sort(key=lambda expense: expense.date)
    return expenses


def delete_expense(index: int, path: Path) -> Expense:
    """날짜순 정렬 기준 1번부터 시작하는 번호(index)의 지출을 삭제하고 돌려준다."""
    expenses = load_expenses(path)
    if index < 1 or index > len(expenses):
        raise IndexError(f"삭제할 번호가 올바르지 않습니다: {index}")

    deleted = expenses.pop(index - 1)
    path = Path(path)
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(_COLUMNS)
        for expense in expenses:
            writer.writerow(
                [
                    expense.date.isoformat(),
                    expense.item,
                    expense.amount,
                    expense.category,
                ]
            )
    return deleted