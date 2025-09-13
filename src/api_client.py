from __future__ import annotations
from typing import Dict, Any, Optional, Iterable
import requests
import time

UA = {"User-Agent": "Vacancy-Vault/1.0 (+https://github.com/you/Vacancy-Vault)"}


class HHClient:
    """
    Простой клиент для публичного API hh.ru.

    Что делает:
    - get_employer(employer_id): получить подробную информацию о работодателе;
    - iter_vacancies_by_employer(employer_id): лениво итерировать вакансии работодателя постранично.

    Заметки по API hh.ru:
    - База URL: https://api.hh.ru
    - Эндпоинт работодателя: /employers/{id}
    - Эндпоинт вакансий:     /vacancies?employer_id={id}&page={n}&per_page={m}
    - Параметры пагинации: page (начиная с 0), per_page (обычно до 100)
    - В ответе на /vacancies есть поле "pages" — общее количество страниц.
    """

    BASE = "https://api.hh.ru"

    def __init__(
        self,
        per_page: int = 100,                  # сколько вакансий запрашивать на одной странице
        timeout: int = 30,                    # таймаут сетевых запросов, сек
        sleep_between_requests: float = 0.1,  # пауза между запросами
        retries: int = 2,                     # число повторных попыток при временных ошибках
        only_with_salary: bool = False,       # если True - API вернёт только вакансии с указанной зарплатой
    ) -> None:
        self.per_page = per_page
        self.timeout = timeout
        self.sleep_between_requests = sleep_between_requests
        self.retries = retries
        self.only_with_salary = only_with_salary

        # Session переиспользует TCP-соединения (это быстрее, чем каждый раз requests.get)
        self._session = requests.Session()
        self._session.headers.update(UA)

    # Вспомогательные методы

    def _get(self, path: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        GET-запрос с базовым ретраем.
        - path: относительный путь (например, "/employers/3529")
        - params: query-параметры (?page=..., per_page=..., etc.)
        Возвращает JSON как dict.
        """
        url = f"{self.BASE}{path}"
        last_exc: Optional[BaseException] = None

        for attempt in range(self.retries + 1):
            try:
                resp = self._session.get(url, params=params, timeout=self.timeout)
                if resp.status_code == 429 and attempt < self.retries:
                    time.sleep(1.0 + attempt)
                    continue

                resp.raise_for_status()
                return resp.json()

            except requests.RequestException as exc:
                last_exc = exc
                if attempt < self.retries:
                    time.sleep(0.5 + attempt)
                    continue
                raise

        if last_exc:
            raise last_exc
        return {}

    def get_employer(self, employer_id: int) -> Dict[str, Any]:
        """
        Получить данные о работодателе.
        Важные поля:
          - id (часто строка),
          - name,
          - area.name,
          - open_vacancies,
          - alternate_url.
        """
        data = self._get(f"/employers/{employer_id}")
        if self.sleep_between_requests:
            time.sleep(self.sleep_between_requests)
        return data

    def iter_vacancies_by_employer(self, employer_id: int) -> Iterable[Dict[str, Any]]:
        """
        Итерировать вакансии работодателя постранично (ленивый генератор).
        Возвращает «сырые» dict-элементы из поля items ответа /vacancies.
        """
        page = 0
        while True:
            params: Dict[str, Any] = {
                "employer_id": employer_id,
                "page": page,
                "per_page": self.per_page,
            }
            if self.only_with_salary:
                params["only_with_salary"] = "true"

            data = self._get("/vacancies", params=params)
            items = data.get("items", []) or []
            for v in items:
                yield v

            pages_total = int(data.get("pages", 0))
            if page >= pages_total - 1:
                break

            page += 1
            if self.sleep_between_requests:
                time.sleep(self.sleep_between_requests)
