"""F1: 한 줄 입력 → (항목, 금액) 분리 테스트."""

import pytest

from money_log.parser import ParseError, parse_amount, parse_line


# ---------- parse_amount: 금액 토큰 하나 → 정수 ----------

@pytest.mark.parametrize(
    "token, expected",
    [
        ("4500", 4500),
        ("4,500", 4500),
        ("4500원", 4500),
        ("4,500원", 4500),
        ("만원", 10000),
        ("3만원", 30000),
        ("1만5천원", 15000),
        ("5천원", 5000),
        ("12,000원", 12000),
    ],
)
def test_parse_amount_valid(token, expected):
    assert parse_amount(token) == expected


@pytest.mark.parametrize("token", ["abc", "", "원", "0", "0원", "-500", "4,5,0,0"])
def test_parse_amount_invalid(token):
    with pytest.raises(ParseError):
        parse_amount(token)


# ---------- parse_line: 한 줄 전체 → (항목, 금액) ----------

@pytest.mark.parametrize(
    "line, expected",
    [
        ("커피 4500", ("커피", 4500)),
        ("커피 4,500원", ("커피", 4500)),
        ("택시 만원", ("택시", 10000)),
        ("점심 김밥 3,500원", ("점심 김밥", 3500)),
        ("  커피    4500  ", ("커피", 4500)),
    ],
)
def test_parse_line_valid(line, expected):
    assert parse_line(line) == expected


@pytest.mark.parametrize(
    "line",
    [
        "",          # 빈 입력
        "   ",       # 공백만
        "커피",       # 금액 없음
        "4500",      # 항목 없음
        "커피 abc",   # 금액이 숫자가 아님
        "커피 0",     # 0원
    ],
)
def test_parse_line_invalid(line):
    with pytest.raises(ParseError):
        parse_line(line)


def test_parse_error_is_value_error():
    # 화면 쪽에서 ValueError로 한꺼번에 잡을 수 있도록
    assert issubclass(ParseError, ValueError)
