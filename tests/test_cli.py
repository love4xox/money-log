"""터미널 입구(add / list / report) 테스트. 실제 data/ 폴더와 API는 쓰지 않는다."""

from datetime import date

from money_log.cli import main
from money_log.storage import load_expenses

TODAY = date(2026, 11, 18)


def fake_ask(_prompt):
    return "카페"


def test_add_saves_expense_with_category(tmp_path, capsys):
    path = tmp_path / "expenses.csv"

    code = main(["add", "커피", "4500"], path=path, today=TODAY, ask=fake_ask)

    assert code == 0
    saved = load_expenses(path)
    assert len(saved) == 1
    assert saved[0].date == TODAY
    assert saved[0].item == "커피"
    assert saved[0].amount == 4500
    assert saved[0].category == "카페"
    assert "저장" in capsys.readouterr().out


def test_add_without_ask_falls_back_to_etc(tmp_path):
    path = tmp_path / "expenses.csv"

    main(["add", "커피", "4500"], path=path, today=TODAY, ask=None)

    assert load_expenses(path)[0].category == "기타"


def test_add_rejects_line_without_amount(tmp_path):
    path = tmp_path / "expenses.csv"

    code = main(["add", "커피"], path=path, today=TODAY, ask=fake_ask)

    assert code == 1
    assert load_expenses(path) == []


def test_list_is_in_date_order(tmp_path, capsys):
    path = tmp_path / "expenses.csv"
    main(["add", "커피", "4500"], path=path, today=date(2026, 11, 20), ask=fake_ask)
    main(["add", "김밥", "3500"], path=path, today=date(2026, 11, 10), ask=fake_ask)
    capsys.readouterr()

    code = main(["list"], path=path, today=TODAY)

    out = capsys.readouterr().out
    assert code == 0
    assert out.index("김밥") < out.index("커피")


def test_list_when_empty(tmp_path, capsys):
    code = main(["list"], path=tmp_path / "expenses.csv", today=TODAY)

    assert code == 0
    assert "기록된 지출이 없습니다" in capsys.readouterr().out


def test_report_defaults_to_this_month(tmp_path, capsys):
    path = tmp_path / "expenses.csv"
    main(["add", "커피", "4500"], path=path, today=TODAY, ask=fake_ask)
    capsys.readouterr()

    code = main(["report"], path=path, today=TODAY)

    out = capsys.readouterr().out
    assert code == 0
    assert "카페: 4,500원" in out
    assert "합계: 4,500원" in out


def test_report_for_given_month_excludes_other_months(tmp_path, capsys):
    path = tmp_path / "expenses.csv"
    main(["add", "커피", "4500"], path=path, today=TODAY, ask=fake_ask)
    capsys.readouterr()

    code = main(["report", "2026-10"], path=path, today=TODAY)

    assert code == 0
    assert "합계: 0원" in capsys.readouterr().out


def test_report_rejects_bad_month_format(tmp_path):
    code = main(["report", "2026/11"], path=tmp_path / "expenses.csv", today=TODAY)

    assert code == 1


def test_unknown_command_fails(tmp_path):
    assert main(["delete"], path=tmp_path / "expenses.csv", today=TODAY) == 1


def test_no_command_fails(tmp_path):
    assert main([], path=tmp_path / "expenses.csv", today=TODAY) == 1

def test_list_shows_numbers(tmp_path, capsys):
    path = tmp_path / "expenses.csv"
    main(["add", "김밥", "3500"], path=path, today=date(2026, 11, 10), ask=fake_ask)
    main(["add", "커피", "4500"], path=path, today=date(2026, 11, 20), ask=fake_ask)
    capsys.readouterr()

    code = main(["list"], path=path, today=TODAY)

    out = capsys.readouterr().out
    assert code == 0
    assert "1." in out and "김밥" in out
    assert "2." in out and "커피" in out


def test_delete_removes_selected_item(tmp_path, capsys):
    path = tmp_path / "expenses.csv"
    main(["add", "김밥", "3500"], path=path, today=date(2026, 11, 10), ask=fake_ask)
    main(["add", "커피", "4500"], path=path, today=date(2026, 11, 20), ask=fake_ask)
    capsys.readouterr()

    code = main(["delete", "1"], path=path, today=TODAY)

    out = capsys.readouterr().out
    assert code == 0
    assert "삭제" in out and "김밥" in out
    remaining = load_expenses(path)
    assert len(remaining) == 1
    assert remaining[0].item == "커피"


def test_delete_rejects_invalid_or_out_of_range_number(tmp_path):
    path = tmp_path / "expenses.csv"
    main(["add", "커피", "4500"], path=path, today=TODAY, ask=fake_ask)

    assert main(["delete", "abc"], path=path, today=TODAY) == 1
    assert main(["delete", "2"], path=path, today=TODAY) == 1

def test_report_with_budget_shows_remaining(tmp_path, capsys):
    path = tmp_path / "expenses.csv"
    main(["add", "커피", "4500"], path=path, today=TODAY, ask=fake_ask)
    capsys.readouterr()

    code = main(["report", "--budget", "20000"], path=path, today=TODAY)

    out = capsys.readouterr().out
    assert code == 0
    assert "예산: 20,000원" in out
    assert "남은 예산: 15,500원" in out


def test_report_with_budget_warns_when_exceeded(tmp_path, capsys):
    path = tmp_path / "expenses.csv"
    main(["add", "커피", "25000"], path=path, today=TODAY, ask=fake_ask)
    capsys.readouterr()

    code = main(["report", "2026-11", "--budget", "20000"], path=path, today=TODAY)

    out = capsys.readouterr().out
    assert code == 0
    assert "예산 초과: 5,000원" in out


def test_report_rejects_invalid_budget(tmp_path):
    path = tmp_path / "expenses.csv"

    assert main(["report", "--budget"], path=path, today=TODAY) == 1
    assert main(["report", "--budget", "0"], path=path, today=TODAY) == 1
    assert main(["report", "--budget", "abc"], path=path, today=TODAY) == 1