from __future__ import annotations
from typing import List, Dict, Any, Iterable
from dataclasses import replace
from _pytest.monkeypatch import MonkeyPatch
import src.etl as etl_module
from src.config import settings


class _FakeHH:
    """Мини-клиент HH: 1 работодатель → 1 вакансия."""
    def __init__(self, per_page: int = 100) -> None:
        self.per_page = per_page

    def get_employer(self, employer_id: int) -> Dict[str, Any]:
        # Используем self, чтобы IDE не предлагала staticmethod
        assert self.per_page > 0
        return {
            "id": str(employer_id),
            "name": f"FakeCo {employer_id}",
            "area": {"name": "Ekaterinburg"},
            "open_vacancies": 1,
            "alternate_url": f"https://hh.ru/employer/{employer_id}",
        }

    def iter_vacancies_by_employer(self, employer_id: int) -> Iterable[Dict[str, Any]]:
        assert self.per_page >= 1
        yield {
            "id": f"{employer_id}001",
            "name": "Dev",
            "employer": {"id": str(employer_id)},
            "alternate_url": f"https://hh.ru/vacancy/{employer_id}001",
            "salary": {"from": 100000, "to": 120000, "currency": "RUR"},
            "published_at": "2024-02-01T12:00:00+03:00",
        }


def test_load_uses_settings_if_ids_empty(monkeypatch: MonkeyPatch) -> None:
    """EMPLOYER_IDS пуст → берём ids из settings.employer_ids."""
    # 1) EMPLOYER_IDS делаем пустым
    monkeypatch.setattr(etl_module, "EMPLOYER_IDS", [], raising=True)
    # 2) Подменяем settings в самом модуле etl новым экземпляром
    patched_settings = replace(settings, employer_ids=(111,))
    monkeypatch.setattr(etl_module, "settings", patched_settings, raising=True)
    # 3) Подменяем клиент и перехватываем апсерты
    monkeypatch.setattr(etl_module, "HHClient", lambda: _FakeHH())

    collected_companies: List[Dict[str, Any]] = []
    collected_vacancies: List[Dict[str, Any]] = []
    monkeypatch.setattr(etl_module, "upsert_company", lambda item: collected_companies.append(item))
    monkeypatch.setattr(etl_module, "upsert_vacancy", lambda item: collected_vacancies.append(item))

    etl_module.load_companies_and_vacancies()

    assert [c["id"] for c in collected_companies] == [111]
    assert [v["company_id"] for v in collected_vacancies] == [111]


def test_load_prefers_ids_over_settings(monkeypatch: MonkeyPatch) -> None:
    """Если заданы и EMPLOYER_IDS, и settings — приоритет у EMPLOYER_IDS."""
    monkeypatch.setattr(etl_module, "EMPLOYER_IDS", [222], raising=True)
    patched_settings = replace(settings, employer_ids=(111,))
    monkeypatch.setattr(etl_module, "settings", patched_settings, raising=True)
    monkeypatch.setattr(etl_module, "HHClient", lambda: _FakeHH())

    collected_companies: List[Dict[str, Any]] = []
    collected_vacancies: List[Dict[str, Any]] = []
    monkeypatch.setattr(etl_module, "upsert_company", lambda item: collected_companies.append(item))
    monkeypatch.setattr(etl_module, "upsert_vacancy", lambda item: collected_vacancies.append(item))

    etl_module.load_companies_and_vacancies()

    assert [c["id"] for c in collected_companies] == [222]
    assert [v["company_id"] for v in collected_vacancies] == [222]


def test_load_no_ids_prints_and_skips(monkeypatch: MonkeyPatch, capsys) -> None:
    """Если оба источника пустые — выводим предупреждение и ничего не сохраняем."""
    monkeypatch.setattr(etl_module, "EMPLOYER_IDS", [], raising=True)
    patched_settings = replace(settings, employer_ids=())
    monkeypatch.setattr(etl_module, "settings", patched_settings, raising=True)

    # Не должны дойти до HTTP-клиента, но на всякий случай подменим.
    monkeypatch.setattr(etl_module, "HHClient", lambda: _FakeHH())

    calls = {"company": 0, "vacancy": 0}
    monkeypatch.setattr(etl_module, "upsert_company", lambda item: calls.__setitem__("company", calls["company"] + 1))
    monkeypatch.setattr(etl_module, "upsert_vacancy", lambda item: calls.__setitem__("vacancy", calls["vacancy"] + 1))

    etl_module.load_companies_and_vacancies()
    out = capsys.readouterr().out

    assert "Нет employer_id" in out
    assert calls["company"] == 0 and calls["vacancy"] == 0
