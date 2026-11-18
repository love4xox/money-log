"""Part 2-A: FastAPI 웹 API 테스트. 실제 data/와 Gemini API를 쓰지 않는다."""

from datetime import date

from fastapi.testclient import TestClient

from money_log.web import create_app

TODAY = date(2026, 11, 18)


def fake_ask(_prompt: str) -> str:
    return "카페"


def test_get_expenses_starts_empty(tmp_path):
    app = create_app(path=tmp_path / "expenses.csv", ask=fake_ask, today=TODAY)
    client = TestClient(app)

    res = client.get("/api/expenses")

    assert res.status_code == 200
    assert res.json() == []


def test_post_expense_parses_classifies_and_saves(tmp_path):
    app = create_app(path=tmp_path / "expenses.csv", ask=fake_ask, today=TODAY)
    client = TestClient(app)

    res = client.post("/api/expenses", json={"line": "아이스 아메리카노 4,500원"})

    assert res.status_code == 201
    body = res.json()
    assert body["index"] == 1
    assert body["date"] == "2026-11-18"
    assert body["item"] == "아이스 아메리카노"
    assert body["amount"] == 4500
    assert body["category"] == "카페"


def test_post_expense_rejects_invalid_input(tmp_path):
    app = create_app(path=tmp_path / "expenses.csv", ask=fake_ask, today=TODAY)
    client = TestClient(app)

    res = client.post("/api/expenses", json={"line": "금액없는입력"})

    assert res.status_code == 400
    assert "detail" in res.json()


def test_delete_expense_removes_by_index(tmp_path):
    app = create_app(path=tmp_path / "expenses.csv", ask=fake_ask, today=TODAY)
    client = TestClient(app)
    client.post("/api/expenses", json={"line": "김밥 3500"})
    client.post("/api/expenses", json={"line": "커피 4500"})

    res = client.delete("/api/expenses/1")

    assert res.status_code == 200
    assert res.json()["deleted"]["item"] == "김밥"
    remaining = client.get("/api/expenses").json()
    assert len(remaining) == 1
    assert remaining[0]["item"] == "커피"


def test_get_report_with_optional_budget(tmp_path):
    app = create_app(path=tmp_path / "expenses.csv", ask=fake_ask, today=TODAY)
    client = TestClient(app)
    client.post("/api/expenses", json={"line": "라떼 25000"})

    res = client.get("/api/report", params={"year": 2026, "month": 11, "budget": 20000})

    assert res.status_code == 200
    data = res.json()
    assert data["total"] == 25000
    assert data["categories"]["카페"] == 25000
    assert data["budget"] == 20000
    assert data["remaining"] == -5000
    assert data["is_over_budget"] is True