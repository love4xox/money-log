"""가계부에서 쓰는 데이터."""

from dataclasses import dataclass
from datetime import date


@dataclass
class Expense:
    """지출 한 건. date는 날짜, amount는 원 단위 정수."""

    date: date
    item: str
    amount: int
    category: str
