from __future__ import annotations
from typing import Dict, Any, List, Optional
from time import sleep
from src.api_client import HHClient
from src.db import upsert_company, upsert_vacancy
from src.utils import midpoint_salary
from src.config import settings

# Тесты могут подменить это значение. В проде обычно пусто.
EMPLOYER_IDS: List[int] = []


def _effective_employer_ids() -> List[int]:
    """Список employer_id: сначала пробуем локальную переменную,
    если она пустая,то берём из .env (settings.employer_ids)."""
    ids = EMPLOYER_IDS or settings.employer_ids
    # приведение к int и фильтр мусора
    return [int(x) for x in ids if str(x).strip()]


def _normalize_company(emp: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "id": int(emp["id"]),
        "name": emp.get("name") or "",
        "area": (emp.get("area") or {}).get("name"),
        "open_vacancies": emp.get("open_vacancies"),
        "alternate_url": emp.get("alternate_url") or emp.get("url"),
    }


def _normalize_vacancy(v: Dict[str, Any], fallback_employer_id: int) -> Dict[str, Any]:
    # employer_id может быть в объекте employer, а может отсутствовать тогда берём fallback
    raw_emp_id: Optional[str | int] = (v.get("employer") or {}).get("id") or fallback_employer_id
    employer_id: Optional[int] = int(raw_emp_id) if raw_emp_id is not None else None

    title = v.get("name") or v.get("profession") or v.get("title") or ""

    sal = v.get("salary") or {}
    s_from = sal.get("from")
    s_to = sal.get("to")
    curr = sal.get("currency")

    return {
        "id": int(v["id"]),
        "company_id": employer_id,
        "title": title,
        "url": v.get("alternate_url") or v.get("url"),
        "salary_from": s_from,
        "salary_to": s_to,
        "salary_currency": curr,
        "salary_avg": midpoint_salary(s_from, s_to),
        "published_at": v.get("published_at"),
    }


def load_companies_and_vacancies() -> None:
    ids = _effective_employer_ids()
    if not ids:
        print("Нет employer_id. Укажите их в .env (EMPLOYER_IDS=41862,42600,...) или задайте etl.EMPLOYER_IDS в коде.")
        return

    client = HHClient()
    for emp_id in ids:
        # 1) Работодатель
        emp = client.get_employer(emp_id)
        upsert_company(_normalize_company(emp))

        # 2) Его вакансии (постранично)
        for v in client.iter_vacancies_by_employer(emp_id):
            item = _normalize_vacancy(v, emp_id)
            if item["company_id"] is None:
                # странный случай — пропустим
                continue
            upsert_vacancy(item)

        # limit API
        sleep(0.15)
