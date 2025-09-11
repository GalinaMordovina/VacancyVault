from __future__ import annotations
import psycopg2
import pytest
from src.config import settings
from src.db import create_tables, upsert_company, upsert_vacancy


def _connect():
    return psycopg2.connect(
        host=settings.db_host,
        port=settings.db_port,
        dbname=settings.db_name,
        user=settings.db_user,
        password=settings.db_password,
    )


def test_create_tables_idempotent():
    # Должно отработать несколько раз без ошибок
    create_tables()
    create_tables()


@pytest.mark.usefixtures("clean_tables")
def test_upsert_company_and_vacancy_cascade():
    # Вставляем компанию
    upsert_company({
        "id": 9001,
        "name": "Company X",
        "area": "Moscow",
        "open_vacancies": 1,
        "alternate_url": "https://hh.ru/employer/9001",
    })
    # Обновляем имя той же компании (проверяем ON CONFLICT DO UPDATE)
    upsert_company({
        "id": 9001,
        "name": "Company X NEW",
        "area": "Moscow",
        "open_vacancies": 2,
        "alternate_url": "https://hh.ru/employer/9001",
    })

    # Вставляем вакансию
    upsert_vacancy({
        "id": 99001,
        "company_id": 9001,
        "title": "Python Dev",
        "url": "https://hh.ru/vacancy/99001",
        "salary_from": 100000.0,
        "salary_to": 150000.0,
        "salary_currency": "RUR",
        "salary_avg": 125000.0,
        "published_at": "2024-02-01T10:00:00+03:00",
    })

    # Проверяем, что апдейт имени прошёл и вакансия на месте
    con = _connect()
    with con, con.cursor() as cur:
        cur.execute("SELECT name FROM companies WHERE employer_id=9001;")
        assert cur.fetchone()[0] == "Company X NEW"

        cur.execute("SELECT COUNT(*) FROM vacancies WHERE company_id=9001;")
        assert cur.fetchone()[0] == 1

        # Проверим каскад: удаляем компанию → вакансия должна удалиться
        cur.execute("DELETE FROM companies WHERE employer_id=9001;")
        cur.execute("SELECT COUNT(*) FROM vacancies WHERE company_id=9001;")
        assert cur.fetchone()[0] == 0
    con.close()
