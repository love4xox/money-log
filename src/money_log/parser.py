"""F1: 한 줄 입력("커피 4,500원")을 (항목, 금액)으로 나눈다."""

import re

# "4500" 또는 "4,500" / "12,000" (쉼표는 세 자리마다만 허용)
_PLAIN_NUMBER = re.compile(r"\d+|\d{1,3}(?:,\d{3})+")

# "만", "3만", "1만5천", "5천", "1만2000" 처럼 만/천 단위가 섞인 금액
_KOREAN_UNITS = re.compile(r"(?:(\d*)만)?(?:(\d*)천)?(\d*)")


class ParseError(ValueError):
    """입력 줄이나 금액을 해석할 수 없을 때."""


def parse_amount(token: str) -> int:
    """금액 토큰 하나를 정수(원)로 바꾼다. 0 이하이거나 해석 불가면 ParseError."""
    text = token.strip()
    if text.endswith("원"):
        text = text[:-1]
    if not text:
        raise ParseError(f"금액이 비어 있습니다: {token!r}")

    if _PLAIN_NUMBER.fullmatch(text):
        amount = int(text.replace(",", ""))
    else:
        amount = _parse_korean_units(text, token)

    if amount <= 0:
        raise ParseError(f"금액은 0보다 커야 합니다: {token!r}")
    return amount


def _parse_korean_units(text: str, original: str) -> int:
    match = _KOREAN_UNITS.fullmatch(text)
    if not match or ("만" not in text and "천" not in text):
        raise ParseError(f"금액을 해석할 수 없습니다: {original!r}")

    man, cheon, rest = match.groups()
    amount = 0
    if "만" in text:
        amount += int(man or 1) * 10_000
    if "천" in text:
        amount += int(cheon or 1) * 1_000
    if rest:
        amount += int(rest)
    return amount


def parse_line(line: str) -> tuple[str, int]:
    """'점심 김밥 3,500원' → ('점심 김밥', 3500). 마지막 토큰이 금액이다."""
    tokens = line.split()
    if len(tokens) < 2:
        raise ParseError(f"'항목 금액' 형식으로 입력해 주세요: {line!r}")

    *item_tokens, amount_token = tokens
    return " ".join(item_tokens), parse_amount(amount_token)
