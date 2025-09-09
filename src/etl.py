from __future__ import annotations
from typing import Any, Dict
from .config import settings
from .api_client import HHClient
from .db import upsert_company, upsert_vacancy


def _normalize_company(j: Dict[str, Any]) -> Dict[str, Any]:
    """Приводим ответ /employers/{id} к схеме таблицы companies."""
    area = (j.get("area") or {}).get("name")
    return {
        "id": int(j["id"]),
        "name": j.get("name"),
        "url": j.get("alternate_url"),
        "area": area,
        "description": j.get("description"),
    }


def _normalize_vacancy(item: Dict[str, Any], employer_id: int) -> Dict[str, Any]:
    """Приводим элемент из /vacancies к схеме таблицы vacancies."""
    salary = item.get("salary") or {}
    area = (item.get("area") or {}).get("name")
    snippet = item.get("snippet") or {}
    return {
        "id": int(item["id"]),
        "employer_id": employer_id,
        "name": item.get("name"),
        "salary_from": salary.get("from"),
        "salary_to": salary.get("to"),
        "currency": salary.get("currency"),
        "published_at": item.get("published_at"),  # ISO-строка - psycopg2 примет
        "url": item.get("alternate_url"),
        "area": area,
        "requirement": snippet.get("requirement"),
        "responsibility": snippet.get("responsibility"),
    }


def load_companies_and_vacancies(only_python: bool = True) -> None:
    """Основная загрузка: компании + их вакансии."""
    client = HHClient()  # возьмёт USER_AGENT из config по умолчанию
    if not settings.employer_ids:
        raise RuntimeError("EMPLOYER_IDS пуст — заполни .env (минимум 10 id)")

    for emp_id in settings.employer_ids:
        # компания
        company_raw = client.get_employer(emp_id)
        upsert_company(_normalize_company(company_raw))

        # вакансии
        for v in client.iter_vacancies_by_employer(emp_id, only_python=only_python):
            upsert_vacancy(_normalize_vacancy(v, emp_id))
