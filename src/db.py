import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from .config import settings
from typing import Any, Dict

# DDL (схема БД): описывает таблицы

# Таблица компаний-работодателей с hh.ru
DDL_COMPANIES = """
CREATE TABLE IF NOT EXISTS companies (
    id BIGINT PRIMARY KEY,
    name TEXT NOT NULL,
    url TEXT,
    area TEXT,
    description TEXT
);
"""

# Таблица вакансий, связанных с компаниями
DDL_VACANCIES = """
CREATE TABLE IF NOT EXISTS vacancies (
    id BIGINT PRIMARY KEY,
    employer_id BIGINT REFERENCES companies(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    salary_from NUMERIC,
    salary_to NUMERIC,
    currency TEXT,
    published_at TIMESTAMPTZ,
    url TEXT,
    area TEXT,
    requirement TEXT,
    responsibility TEXT
);
"""

def create_database_if_not_exists() -> None:
    """
    Подключается к *системной* БД postgres и создаёт рабочую БД settings.db_name,
    если она ещё не существует.

    Почему так:
        - Нельзя создать БД, подключившись к самой создаваемой БД.
        - Поэтому подключаемся к postgres (или другой существующей), проверяем наличие,
          и при необходимости выполняем CREATE DATABASE.
    """
    # Важно: подключаемся к существующей БД 'postgres', а не к settings.db_name
    conn = psycopg2.connect(
        dbname="postgres",
        user=settings.db_user,
        password=settings.db_password,
        host=settings.db_host,
        port=settings.db_port,
    )
    # Для CREATE DATABASE нужен autocommit вне транзакции.
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)

    cur = conn.cursor()
    try:
        # Проверяем, есть ли наша БД
        cur.execute("SELECT 1 FROM pg_database WHERE datname = %s;", (settings.db_name,))
        exists = cur.fetchone()
        if not exists:
            # Экранируем имя БД кавычками на случай «нестандартных» имён
            cur.execute(f'CREATE DATABASE "{settings.db_name}"')
    finally:
        cur.close()
        conn.close()

def create_tables() -> None:
    """
    Подключается к рабочей БД и создаёт таблицы companies и vacancies.
    Вызываем после create_database_if_not_exists().
    """
    conn = psycopg2.connect(
        dbname=settings.db_name,
        user=settings.db_user,
        password=settings.db_password,
        host=settings.db_host,
        port=settings.db_port,
    )
    cur = conn.cursor()
    cur.execute(DDL_COMPANIES)
    cur.execute(DDL_VACANCIES)
    conn.commit()
    cur.close()
    conn.close()


def upsert_company(row: Dict[str, Any]) -> None:
    """
    Вставляет или обновляет запись о компании.
    Ожидаемый словарь row (ключи мы нормализуем в api_client.get_employer()):
      {
        "id": int,
        "name": str | None,
        "url": str | None,
        "area": str | None,
        "description": str | None,
      }

    ON CONFLICT (id) DO UPDATE если компания уже есть, корректно обновим поля.
    """
    conn = psycopg2.connect(
        dbname=settings.db_name,
        user=settings.db_user,
        password=settings.db_password,
        host=settings.db_host,
        port=settings.db_port,
    )
    cur = conn.cursor()
    try:
        cur.execute(
            """
            INSERT INTO companies (id, name, url, area, description)
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (id) DO UPDATE
              SET name = EXCLUDED.name,
                  url = EXCLUDED.url,
                  area = EXCLUDED.area,
                  description = EXCLUDED.description;
            """,
            (
                row["id"],             # обязательно
                row.get("name"),
                row.get("url"),
                row.get("area"),
                row.get("description"),
            ),
        )
        conn.commit()
    finally:
        cur.close()
        conn.close()


def upsert_vacancy(row: Dict[str, Any]) -> None:
    """
    Вставляет или обновляет запись о вакансии.
    Ожидаемый словарь row (ключи нормализуем в api_client.iter_vacancies_by_employer()):
      {
        "id": int,
        "employer_id": int,
        "name": str | None,
        "salary_from": float | None,
        "salary_to": float | None,
        "currency": str | None,
        "published_at": str | datetime | None,   # psycopg2 примет ISO-строку
        "url": str | None,
        "area": str | None,
        "requirement": str | None,
        "responsibility": str | None,
      }

    ON CONFLICT (id) DO UPDATE — если вакансия уже есть, обновим её поля.
    """
    conn = psycopg2.connect(
        dbname=settings.db_name,
        user=settings.db_user,
        password=settings.db_password,
        host=settings.db_host,
        port=settings.db_port,
    )
    cur = conn.cursor()
    try:
        cur.execute(
            """
            INSERT INTO vacancies
              (id, employer_id, name, salary_from, salary_to, currency,
               published_at, url, area, requirement, responsibility)
            VALUES
              (%s, %s, %s, %s, %s, %s,
               %s, %s, %s, %s, %s)
            ON CONFLICT (id) DO UPDATE
              SET employer_id   = EXCLUDED.employer_id,
                  name          = EXCLUDED.name,
                  salary_from   = EXCLUDED.salary_from,
                  salary_to     = EXCLUDED.salary_to,
                  currency      = EXCLUDED.currency,
                  published_at  = EXCLUDED.published_at,
                  url           = EXCLUDED.url,
                  area          = EXCLUDED.area,
                  requirement   = EXCLUDED.requirement,
                  responsibility= EXCLUDED.responsibility;
            """,
            (
                row["id"],                # обязательно
                row["employer_id"],       # обязательно, FK -> companies.id
                row.get("name"),
                row.get("salary_from"),
                row.get("salary_to"),
                row.get("currency"),
                row.get("published_at"),  # ISO-строка/датавремя — psycopg2 распарсит
                row.get("url"),
                row.get("area"),
                row.get("requirement"),
                row.get("responsibility"),
            ),
        )
        conn.commit()
    finally:
        cur.close()
        conn.close()
