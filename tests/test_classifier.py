"""F2: 항목 → 카테고리 분류 테스트.

실제 Gemini는 부르지 않는다. classify()에 '질문을 받아 답을 돌려주는 함수(ask)'를
넘기는 구조라서, 테스트에서는 가짜 ask를 넘긴다.
"""

import pytest

from money_log.classifier import CATEGORIES, DEFAULT_CATEGORY, classify, make_gemini_ask


def fake_ask(answer):
    """항상 같은 답을 돌려주는 가짜 Gemini."""
    return lambda prompt: answer


def failing_ask(error):
    """항상 예외를 던지는 가짜 Gemini."""

    def ask(prompt):
        raise error

    return ask


def test_categories():
    assert CATEGORIES == ("식비", "카페", "교통", "쇼핑", "기타")
    assert DEFAULT_CATEGORY == "기타"


# ---------- 정상 응답 ----------

@pytest.mark.parametrize("category", ["식비", "카페", "교통", "쇼핑", "기타"])
def test_valid_answer_is_used(category):
    assert classify("아무거나", fake_ask(category)) == category


@pytest.mark.parametrize("answer", ["  카페\n", "'카페'", "카페."])
def test_answer_is_trimmed(answer):
    assert classify("커피", fake_ask(answer)) == "카페"


# ---------- 실패하면 전부 "기타" ----------

@pytest.mark.parametrize("answer", ["음식", "", "카페, 식비", "This is 카페", None])
def test_unknown_answer_falls_back(answer):
    assert classify("커피", fake_ask(answer)) == "기타"


@pytest.mark.parametrize("error", [RuntimeError("API 오류"), TimeoutError("시간 초과")])
def test_error_falls_back(error):
    assert classify("커피", failing_ask(error)) == "기타"


def test_no_ask_falls_back():
    # API 키가 없어서 ask를 못 만든 경우
    assert classify("커피", None) == "기타"


def test_empty_item_does_not_call_ask():
    called = []

    def ask(prompt):
        called.append(prompt)
        return "카페"

    assert classify("   ", ask) == "기타"
    assert called == []


# ---------- Gemini에 보내는 질문 ----------

def test_prompt_contains_item_and_all_categories():
    sent = []

    def ask(prompt):
        sent.append(prompt)
        return "카페"

    classify("아이스 아메리카노", ask)

    assert len(sent) == 1
    assert "아이스 아메리카노" in sent[0]
    for category in CATEGORIES:
        assert category in sent[0]


# ---------- Gemini 연결 ----------

def test_make_gemini_ask_without_key_returns_none(monkeypatch):
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    assert make_gemini_ask() is None
