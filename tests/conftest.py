from __future__ import annotations
import pytest
import psycopg2
from src.config import settings
from src.db import create_database_if_not_exists, create_tables, upsert_company, upsert_vacancy


def _connect():
    return psycopg2.connect(
        host=settings.db_host,
        port=settings.db_port,
        dbname=settings.db_name,
        user=settings.db_user,
        password=settings.db_password,
    )


@pytest.fixture(scope="session", autouse=True)
def bootstrap_db() -> None:
    create_database_if_not_exists()
    create_tables()


@pytest.fixture()
def clean_tables() -> None:
    con = _connect()
    with con, con.cursor() as cur:
        cur.execute("TRUNCATE TABLE vacancies RESTART IDENTITY CASCADE;")
        cur.execute("TRUNCATE TABLE companies RESTART IDENTITY CASCADE;")
    con.close()


@pytest.fixture()
def sample_data(clean_tables) -> None:
    # Имена ровно как ждут тесты
    upsert_company({
        "id": 1,
        "name": "Test A",
        "area": "CityA",
        "open_vacancies": 2,
        "alternate_url": "https://hh.ru/employer/1",
    })
    upsert_company({
        "id": 2,
        "name": "Test B",
        "area": "CityB",
        "open_vacancies": 1,
        "alternate_url": "https://hh.ru/employer/2",
    })

    # Ровно три вакансии с salary_avg: 125000, 80000, 110000
    # → средняя = 105000; у "Test A" две вакансии, у "Test B" одна.
    upsert_vacancy({
        "id": 101,
        "company_id": 1,
        "title": "Python Developer",             # этот будет найден по keyword 'python'
        "url": "https://hh.ru/vacancy/101",
        "salary_from": 100000.0,
        "salary_to": 150000.0,
        "salary_currency": "RUR",
        "salary_avg": 125000.0,
        "published_at": "2024-01-01T10:00:00+03:00",
    })
    upsert_vacancy({
        "id": 102,
        "company_id": 1,
        "title": "QA Engineer",
        "url": "https://hh.ru/vacancy/102",
        "salary_from": 80000.0,
        "salary_to": None,
        "salary_currency": "RUR",
        "salary_avg": 80000.0,
        "published_at": "2024-01-02T10:00:00+03:00",
    })
    upsert_vacancy({
        "id": 201,
        "company_id": 2,
        "title": "Senior Backend",               # без слова 'Python', чтобы в keyword-тесте была одна строка
        "url": "https://hh.ru/vacancy/201",
        "salary_from": 110000.0,
        "salary_to": None,
        "salary_currency": "RUR",
        "salary_avg": 110000.0,
        "published_at": "2024-01-03T10:00:00+03:00",
    })
