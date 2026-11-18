"""F3: 지출을 CSV에 저장하고, 날짜순으로 불러온다.

Expense는 models에 두고, 테스트가 storage에서 import할 수 있게 여기서도 내보낸다.
"""

import csv
from datetime import date
from pathlib import Path

from money_log.models import Expense

__all__ = ["Expense", "load_expenses", "save_expense"]

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
