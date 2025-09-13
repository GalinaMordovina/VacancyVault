from __future__ import annotations
import requests_mock
from src.api_client import HHClient


def test_get_employer_requests_mock() -> None:
    client = HHClient()
    with requests_mock.Mocker() as m:
        m.get("https://api.hh.ru/employers/3529", json={"id": "3529", "name": "Сбер"})
        data = client.get_employer(3529)
    assert data["id"] == "3529"
    assert data["name"] == "Сбер"


def test_iter_vacancies_pagination() -> None:
    client = HHClient(per_page=2)
    with requests_mock.Mocker() as m:
        # page=0
        m.get(
            "https://api.hh.ru/vacancies",
            json={"items": [{"id": "1"}, {"id": "2"}], "pages": 2},
        )
        # page=1
        m.get(
            "https://api.hh.ru/vacancies?employer_id=1&page=1&per_page=2",
            # requests-mock не комбинирует params автоматически, поэтому проще так:
            additional_matcher=lambda req: req.qs == {"employer_id": ["1"], "page": ["1"], "per_page": ["2"]},
            json={"items": [{"id": "3"}], "pages": 2},
        )

        items = list(client.iter_vacancies_by_employer(1))
    ids = [v["id"] for v in items]
    assert ids == ["1", "2", "3"]
