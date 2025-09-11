from __future__ import annotations
from _pytest.monkeypatch import MonkeyPatch
from _pytest.capture import CaptureFixture
from typing import List, Tuple
import builtins
import src.view as view


def test_cmd_menu_option_1_prints_counts(monkeypatch: MonkeyPatch, capsys: CaptureFixture[str]) -> None:
    class FakeMgr:
        def __init__(self) -> None:
            self._opened = True
            self._calls = {"all": 0, "avg": 0, "higher": 0, "kw": 0}

        def close(self) -> None:
            self._opened = False

        def get_companies_and_vacancies_count(self) -> List[Tuple[str, int]]:
            assert self._opened
            return [("ACorp", 2)]

        def get_all_vacancies(self) -> List[Tuple[str, str, float | None, str]]:
            # используем self → инспектор не предлагает static
            assert self._opened
            self._calls["all"] += 1
            return []

        def get_avg_salary(self) -> float | None:
            assert self._opened
            self._calls["avg"] += 1
            return None

        def get_vacancies_with_higher_salary(self) -> List[Tuple[str, str, float, str]]:
            assert self._opened
            self._calls["higher"] += 1
            return []

        def get_vacancies_with_keyword(self, kw: str) -> List[Tuple[str, str, float | None, str]]:
            assert self._opened
            self._calls["kw"] += 1
            _ = kw.lower()  # «используем» параметр
            return []

    monkeypatch.setattr(view, "DBManager", FakeMgr)

    inputs = iter(["1", "0"])  # показать пункт 1, затем выход
    monkeypatch.setattr(builtins, "input", lambda _: next(inputs))

    view.cmd_menu()
    out = capsys.readouterr().out
    assert "ACorp: 2" in out
