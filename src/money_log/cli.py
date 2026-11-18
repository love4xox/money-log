"""터미널에서 쓰는 입구: add / list / report."""

from datetime import date
from pathlib import Path
from typing import Optional

from money_log.classifier import CATEGORIES, Ask, classify
from money_log.models import Expense
from money_log.parser import ParseError, parse_line
from money_log.report import monthly_report
from money_log.storage import load_expenses, save_expense

USAGE = """사용법:
  add 커피 4500       지출 한 줄 기록
  list                날짜순 목록
  report [YYYY-MM]    월별 카테고리 합계 (기본: 이번 달)"""


def main(
    argv: list[str],
    *,
    path: Path,
    today: date,
    ask: Optional[Ask] = None,
) -> int:
    """명령을 실행하고 종료 코드(0 성공, 1 실패)를 돌려준다."""
    if not argv:
        print(USAGE)
        return 1

    command, rest = argv[0], argv[1:]
    if command == "add":
        return _add(rest, path, today, ask)
    if command == "list":
        return _list(path)
    if command == "report":
        return _report(rest, path, today)

    print(f"알 수 없는 명령: {command}")
    print(USAGE)
    return 1


def _add(words: list[str], path: Path, today: date, ask: Optional[Ask]) -> int:
    try:
        item, amount = parse_line(" ".join(words))
    except ParseError as error:
        print(f"입력 오류: {error}")
        return 1

    category = classify(item, ask)
    save_expense(Expense(today, item, amount, category), path)
    print(f"저장: {today} {item} {amount:,}원 [{category}]")
    return 0


def _list(path: Path) -> int:
    expenses = load_expenses(path)
    if not expenses:
        print("기록된 지출이 없습니다.")
        return 0

    for expense in expenses:
        print(f"{expense.date}  {expense.item}  {expense.amount:,}원  [{expense.category}]")
    return 0


def _report(args: list[str], path: Path, today: date) -> int:
    year, month = today.year, today.month
    if args:
        try:
            year_text, month_text = args[0].split("-")
            year, month = int(year_text), int(month_text)
            date(year, month, 1)
        except ValueError:
            print("월 형식이 올바르지 않습니다. 예: 2026-11")
            return 1

    report = monthly_report(load_expenses(path), year, month)
    print(f"{year}년 {month}월")
    for category in CATEGORIES:
        print(f"  {category}: {report.categories[category]:,}원")
    print(f"  합계: {report.total:,}원")
    return 0