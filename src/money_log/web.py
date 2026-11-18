"""Part 2: 기존 코어 모듈(parser, classifier, storage, report)을 그대로 연결한 FastAPI 서버."""

from datetime import date
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from money_log.classifier import Ask, classify, make_gemini_ask
from money_log.models import Expense
from money_log.parser import ParseError, parse_line
from money_log.report import monthly_report
from money_log.storage import delete_expense, load_expenses, save_expense

_STATIC_DIR = Path(__file__).resolve().parent / "static"
_DEFAULT_DATA_PATH = Path("data") / "expenses.csv"


class ExpenseCreateRequest(BaseModel):
    line: str


def _serialize_expense(index: int, expense: Expense) -> dict:
    return {
        "index": index,
        "date": expense.date.isoformat(),
        "item": expense.item,
        "amount": expense.amount,
        "category": expense.category,
    }


def create_app(
    *,
    path: Optional[Path] = None,
    ask: Optional[Ask] = None,
    today: Optional[date] = None,
) -> FastAPI:
    """테스트와 실제 실행 모두에서 재사용 가능한 FastAPI 앱 팩토리."""
    data_path = Path(path) if path is not None else _DEFAULT_DATA_PATH
    app = FastAPI(title="money-log", description="한 줄로 기록하는 노션 감성 AI 가계부")

    if _STATIC_DIR.is_dir():
        app.mount("/static", StaticFiles(directory=str(_STATIC_DIR)), name="static")

    @app.get("/")
    def index():
        html_path = _STATIC_DIR / "index.html"
        if not html_path.is_file():
            raise HTTPException(status_code=404, detail="index.html 파일을 찾을 수 없습니다.")
        return FileResponse(html_path)

    @app.get("/favicon.ico")
    def favicon():
        icon_path = _STATIC_DIR / "favicon.png"
        if not icon_path.is_file():
            raise HTTPException(status_code=404, detail="favicon.png 파일을 찾을 수 없습니다.")
        return FileResponse(icon_path, media_type="image/png")

    @app.get("/api/expenses")
    def get_expenses():
        expenses = load_expenses(data_path)
        return [_serialize_expense(idx, exp) for idx, exp in enumerate(expenses, start=1)]

    @app.post("/api/expenses", status_code=201)
    def post_expense(payload: ExpenseCreateRequest):
        try:
            item, amount = parse_line(payload.line)
        except ParseError as error:
            raise HTTPException(status_code=400, detail=str(error)) from error

        current_date = today if today is not None else date.today()
        category = classify(item, ask)
        new_expense = Expense(current_date, item, amount, category)

        data_path.parent.mkdir(parents=True, exist_ok=True)
        save_expense(new_expense, data_path)

        expenses = load_expenses(data_path)
        saved_index = next(
            (idx for idx, exp in enumerate(expenses, start=1) if exp == new_expense),
            len(expenses),
        )
        return _serialize_expense(saved_index, new_expense)

    @app.delete("/api/expenses/{index}")
    def remove_expense(index: int):
        try:
            deleted = delete_expense(index, data_path)
        except IndexError as error:
            raise HTTPException(status_code=404, detail=str(error)) from error

        return {"deleted": _serialize_expense(index, deleted)}

    @app.get("/api/report")
    def get_report(
        year: Optional[int] = None,
        month: Optional[int] = None,
        budget: Optional[int] = None,
    ):
        current_date = today if today is not None else date.today()
        target_year = year if year is not None else current_date.year
        target_month = month if month is not None else current_date.month

        try:
            date(target_year, target_month, 1)
            report = monthly_report(
                load_expenses(data_path),
                target_year,
                target_month,
                budget=budget,
            )
        except ValueError as error:
            raise HTTPException(status_code=400, detail=str(error)) from error

        return {
            "year": target_year,
            "month": target_month,
            "categories": report.categories,
            "total": report.total,
            "budget": report.budget,
            "remaining": report.remaining,
            "is_over_budget": report.is_over_budget,
        }

    return app


def _build_default_app() -> FastAPI:
    try:
        from dotenv import load_dotenv

        load_dotenv()
    except ImportError:
        pass
    return create_app(path=_DEFAULT_DATA_PATH, ask=make_gemini_ask())


app = _build_default_app()