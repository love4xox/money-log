"""터미널에서 쓰는 입구: add / list / delete / report."""

from datetime import date
from pathlib import Path
from typing import Optional

from money_log.classifier import CATEGORIES, Ask, classify
from money_log.models import Expense
from money_log.parser import ParseError, parse_line
from money_log.report import monthly_report
from money_log.storage import delete_expense, load_expenses, save_expense

USAGE = """사용법:
  add 커피 4500                   지출 한 줄 기록
  list                            날짜순 목록
  delete 번호                     목록 번호로 지출 삭제
  report [YYYY-MM] [--budget N]   월별 카테고리 합계 및 예산 비교"""


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
    if command == "delete":
        return _delete(rest, path)
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

    for idx, expense in enumerate(expenses, start=1):
        print(f"{idx}. {expense.date}  {expense.item}  {expense.amount:,}원  [{expense.category}]")
    return 0


def _delete(args: list[str], path: Path) -> int:
    if len(args) != 1:
        print("삭제할 번호를 하나 입력해 주세요. 예: delete 1")
        return 1

    try:
        index = int(args[0])
        deleted = delete_expense(index, path)
    except (ValueError, IndexError):
        print(f"올바르지 않은 삭제 번호입니다: {args[0]}")
        return 1

    print(f"삭제: {deleted.date} {deleted.item} {deleted.amount:,}원 [{deleted.category}]")
    return 0


def _report(args: list[str], path: Path, today: date) -> int:
    year, month = today.year, today.month
    budget: Optional[int] = None

    idx = 0
    while idx < len(args):
        token = args[idx]
        if token == "--budget":
            if idx + 1 >= len(args):
                print("예산 금액을 입력해 주세요. 예: --budget 300000")
                return 1
            try:
                budget = int(args[idx + 1])
            except ValueError:
                print(f"올바르지 않은 예산 금액입니다: {args[idx + 1]}")
                return 1
            idx += 2
        else:
            try:
                year_text, month_text = token.split("-")
                year, month = int(year_text), int(month_text)
                date(year, month, 1)
            except ValueError:
                print("월 형식이 올바르지 않습니다. 예: 2026-11")
                return 1
            idx += 1

    try:
        report = monthly_report(load_expenses(path), year, month, budget=budget)
    except ValueError as error:
        print(f"예산 오류: {error}")
        return 1

    print(f"{year}년 {month}월")
    for category in CATEGORIES:
        print(f"  {category}: {report.categories[category]:,}원")
    print(f"  합계: {report.total:,}원")

    if report.budget is not None and report.remaining is not None:
        if report.is_over_budget:
            print(f"  예산: {report.budget:,}원 (예산 초과: {abs(report.remaining):,}원!)")
        else:
            print(f"  예산: {report.budget:,}원 (남은 예산: {report.remaining:,}원)")
    return 0