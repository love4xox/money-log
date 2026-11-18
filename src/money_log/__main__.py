"""python -m money_log 로 실행하는 진입점."""

import sys
from datetime import date
from pathlib import Path

from money_log.classifier import make_gemini_ask
from money_log.cli import main

if __name__ == "__main__":
    try:
        ask = make_gemini_ask()
    except Exception:
        ask = None  # 키가 없거나 문제가 있으면 모든 지출이 "기타"로 저장된다
    sys.exit(
        main(
            sys.argv[1:],
            path=Path("data/expenses.csv"),
            today=date.today(),
            ask=ask,
        )
    )