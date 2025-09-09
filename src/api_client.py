import requests
from typing import Dict, Iterator, Any, cast

BASE_URL = "https://api.hh.ru"

class HHClient:
    """HH API (работодатели и вакансии)."""
    def __init__(self, user_agent: str = "Vacancy-Vault/1.0") -> None:
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": user_agent})

    def get_employer(self, employer_id: int) -> Dict[str, Any]:
        """
        Возвращаем словарь с данными работодателя.
        resp.json() по типам — Any, поэтому явно приводим к Dict[str, Any],
        чтобы mypy не ругался на несовпадение типов.
        """
        resp = self.session.get(f"{BASE_URL}/employers/{employer_id}")
        resp.raise_for_status()
        return resp.json()

    def iter_vacancies_by_employer(
        self, employer_id: int, per_page: int = 100, only_python: bool = True
    ) -> Iterator[Dict[str, Any]]:
        """
        Итерируем по вакансиям работодателя с пагинацией.
        params объявляем как Dict[str, Any], чтобы в одном dict-е
        можно было хранить и числа (page/per_page/employer_id), и строки (text).
        Иначе типизатор выведет слишком узкий тип и будет конфликтовать.
        """
        params: Dict[str, Any] = {"employer_id": employer_id, "per_page": per_page}
        if only_python:
            params["text"] = "Python"

        page = 0
        while True:
            params["page"] = page
            r = self.session.get(f"{BASE_URL}/vacancies", params=params)
            r.raise_for_status()
            data = cast(Dict[str, Any], r.json())
            for item in data.get("items", []):
                yield item
            if page >= int(data.get("pages", 0)) - 1:
                break
            page += 1
