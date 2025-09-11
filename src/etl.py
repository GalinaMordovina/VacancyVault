from __future__ import annotations
from typing import Dict, Any
from time import sleep

from src.api_client import HHClient
from src.config import settings
from src.db import upsert_company, upsert_vacancy
from src.utils import midpoint_salary


def _normalize_company(emp: Dict[str, Any]) -> Dict[str, Any]:
    """Приводим структуру работодателя к нашей схеме companies."""
    return {
        "id": int(emp["id"]),
        "name": emp.get("name") or "",
        "area": (emp.get("area") or {}).get("name"),
        "open_vacancies": emp.get("open_vacancies"),
        "alternate_url": emp.get("alternate_url") or emp.get("url"),
    }


def _normalize_vacancy(v: Dict[str, Any], fallback_employer_id: int) -> Dict[str, Any]:
    """Приводим структуру вакансии к нашей схеме vacancies."""
    employer_id = (
        (v.get("employer") or {}).get("id")
        or fallback_employer_id
    )
    # HH может отдавать строки id приводим к int
    employer_id = int(employer_id) if employer_id is not None else None

    # Название вакансии в HH хранится в поле 'name'
    title = v.get("name") or v.get("profession") or v.get("title") or ""

    # Зарплата объект salary {from, to, currency} или None
    sal = v.get("salary") or {}
    s_from = sal.get("from")
    s_to = sal.get("to")
    curr = sal.get("currency")

    return {
        "id": int(v["id"]),
        "company_id": employer_id,
        "title": title,  # у нас NOT NULL - пустая строка допустима, но чаще 'name' есть
        "url": v.get("alternate_url") or v.get("url"),
        "salary_from": s_from,
        "salary_to": s_to,
        "salary_currency": curr,
        "salary_avg": midpoint_salary(s_from, s_to),
        "published_at": v.get("published_at"),
    }


def load_companies_and_vacancies() -> None:
    """
    Грузим работодателей из settings.employer_ids и их вакансии.
    Для каждой записи делаем upsert в БД.
    """
    client = HHClient()

    if not settings.employer_ids:
        print("EMPLOYER_IDS пуст - заполните .env")
        return

    for emp_id in settings.employer_ids:
        # 1) Работодатель
        emp = client.get_employer(emp_id)
        upsert_company(_normalize_company(emp))

        # 2) Вакансии работодателя (постранично)
        for v in client.iter_vacancies_by_employer(emp_id):
            item = _normalize_vacancy(v, emp_id)
            # Подстрахуемся: company_id и title должны быть заданы
            if item["company_id"] is None:
                # пропустим такую вакансию, логируем
                print(f"Пропуск вакансии {item['id']}: нет employer_id")
                continue
            if not item["title"]:
                # крайне редкий кейс; пустое значение допустимо, но лучше логировать
                print(f"Вакансия {item['id']} без title — сохраняю пустую строку")
            upsert_vacancy(item)

        # Немного уважаем rate limit API
        sleep(0.2)
