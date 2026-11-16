"""F2: 지출 항목을 Gemini로 분류한다. 무엇이든 실패하면 "기타".

구조
- classify(item, ask): ask는 '질문(str)을 받아 답(str)을 돌려주는 함수'.
  테스트에서는 가짜 ask를, 실제로는 make_gemini_ask()가 만든 함수를 넘긴다.
- make_gemini_ask(): .env/환경변수의 GEMINI_API_KEY로 Gemini 호출 함수를 만든다.
  키가 없거나 라이브러리가 없으면 None → classify가 "기타"를 돌려준다.
"""

import os
from typing import Callable, Optional

CATEGORIES = ("식비", "카페", "교통", "쇼핑", "기타")
DEFAULT_CATEGORY = "기타"

DEFAULT_MODEL = "gemini-2.5-flash"
TIMEOUT_MS = 10_000

Ask = Callable[[str], Optional[str]]


def build_prompt(item: str) -> str:
    choices = ", ".join(CATEGORIES)
    return (
        "가계부 지출 항목을 카테고리 하나로 분류해 줘.\n"
        f"카테고리: {choices}\n"
        "카테고리 이름 하나만 답하고 다른 말은 쓰지 마.\n"
        f"항목: {item}"
    )


def classify(item: str, ask: Optional[Ask]) -> str:
    item = item.strip()
    if not item or ask is None:
        return DEFAULT_CATEGORY

    try:
        answer = ask(build_prompt(item))
    except Exception:
        # 네트워크 오류, 시간 초과, 할당량 초과 등 무엇이든 "기타"
        return DEFAULT_CATEGORY

    if not isinstance(answer, str):
        return DEFAULT_CATEGORY

    answer = answer.strip().strip("'\".").strip()
    return answer if answer in CATEGORIES else DEFAULT_CATEGORY


def make_gemini_ask(api_key: Optional[str] = None, model: Optional[str] = None) -> Optional[Ask]:
    api_key = api_key or os.environ.get("GEMINI_API_KEY")
    if not api_key:
        return None

    try:
        from google import genai
        from google.genai import types
    except ImportError:
        return None

    client = genai.Client(
        api_key=api_key,
        http_options=types.HttpOptions(timeout=TIMEOUT_MS),
    )
    model = model or os.environ.get("GEMINI_MODEL", DEFAULT_MODEL)

    def ask(prompt: str) -> Optional[str]:
        response = client.models.generate_content(model=model, contents=prompt)
        return response.text

    return ask
