from __future__ import annotations
from typing import Optional, Dict, Any
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT,  connection as psycopg2_connection
from src.config import settings


def _connect(database: Optional[str] = None) -> psycopg2_connection:
    """Единая точка подключения к БД."""
    return psycopg2.connect(
        host=settings.db_host,
        port=settings.db_port,
        dbname=database or settings.db_name,
        user=settings.db_user,
        password=settings.db_password,
    )


def create_database_if_not_exists() -> None:
    """Создать базу, если ещё нет (подключаемся к системной postgres)."""
    con = psycopg2.connect(
        host=settings.db_host,
        port=settings.db_port,
        dbname="postgres",
        user=settings.db_user,
        password=settings.db_password,
    )
    con.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cur = con.cursor()
    cur.execute("SELECT 1 FROM pg_database WHERE datname = %s;", (settings.db_name,))
    exists = cur.fetchone() is not None
    if not exists:
        cur.execute(f'CREATE DATABASE "{settings.db_name}";')
    cur.close()
    con.close()


def create_tables() -> None:
    """Создать таблицы companies и vacancies."""
    con = _connect()
    cur = con.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS companies (
            employer_id     BIGINT PRIMARY KEY,
            name            VARCHAR(255) NOT NULL,
            area            VARCHAR(255),
            open_vacancies  INT,
            url             TEXT
        );
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS vacancies (
            vacancy_id       BIGINT PRIMARY KEY,
            company_id       BIGINT NOT NULL REFERENCES companies(employer_id) ON DELETE CASCADE,
            title            VARCHAR(500) NOT NULL,
            url              TEXT NOT NULL,
            salary_from      NUMERIC,
            salary_to        NUMERIC,
            salary_currency  VARCHAR(16),
            salary_avg       NUMERIC,
            published_at     TIMESTAMP
        );
    """)
    con.commit()
    cur.close()
    con.close()


def upsert_company(item: Dict[str, Any]) -> None:
    """Вставка/обновление компании по employer_id."""
    con = _connect()
    cur = con.cursor()
    cur.execute(
        """
        INSERT INTO companies (employer_id, name, area, open_vacancies, url)
        VALUES (%s, %s, %s, %s, %s)
        ON CONFLICT (employer_id) DO UPDATE
          SET name=EXCLUDED.name,
              area=EXCLUDED.area,
              open_vacancies=EXCLUDED.open_vacancies,
              url=EXCLUDED.url;
        """,
        (
            item.get("id"),
            item.get("name"),
            item.get("area"),
            item.get("open_vacancies"),
            item.get("alternate_url") or item.get("url"),
        ),
    )
    con.commit()
    cur.close()
    con.close()


def upsert_vacancy(item: Dict[str, Any]) -> None:
    """Вставка/обновление вакансии по vacancy_id."""
    con = _connect()
    cur = con.cursor()
    cur.execute(
        """
        INSERT INTO vacancies
          (vacancy_id, company_id, title, url,
           salary_from, salary_to, salary_currency, salary_avg, published_at)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
        ON CONFLICT (vacancy_id) DO UPDATE
          SET company_id=EXCLUDED.company_id,
              title=EXCLUDED.title,
              url=EXCLUDED.url,
              salary_from=EXCLUDED.salary_from,
              salary_to=EXCLUDED.salary_to,
              salary_currency=EXCLUDED.salary_currency,
              salary_avg=EXCLUDED.salary_avg,
              published_at=EXCLUDED.published_at;
        """,
        (
            item.get("id"),
            item.get("company_id"),
            item.get("title"),
            item.get("url"),
            item.get("salary_from"),
            item.get("salary_to"),
            item.get("salary_currency"),
            item.get("salary_avg"),
            item.get("published_at"),
        ),
    )
    con.commit()
    cur.close()
    con.close()
