# src/db_manager.py
from __future__ import annotations
from typing import Any, List, Tuple
import psycopg2
from contextlib import contextmanager
from .config import settings

class DBManager:
    """Методы для выборок из БД (psycopg2)."""

    @staticmethod
    @contextmanager
    def _connect():
        """
        Безопасное подключение:
        - открываем conn;
        - внутри блока делаем cursor/execute;
        - на выходе commit/rollback;
        - В ЛЮБОМ случае закрываем conn (finally).
        """
        conn = psycopg2.connect(
            dbname=settings.db_name,
            user=settings.db_user,
            password=settings.db_password,
            host=settings.db_host,
            port=settings.db_port,
        )
        try:
            yield conn            # работа с conn внутри with
            conn.commit()         # явный commit при успехе
        except Exception:
            conn.rollback()       # откат при ошибке
            raise
        finally:
            conn.close()          # закрыть соединение

    # 1) компании и кол-во вакансий
    def get_companies_and_vacancies_count(self) -> List[Tuple[str, int]]:
        sql = """
        SELECT c.name, COUNT(v.id) AS vacancies_count
        FROM companies c
        LEFT JOIN vacancies v ON v.employer_id = c.id
        GROUP BY c.id, c.name
        ORDER BY vacancies_count DESC, c.name;
        """
        with self._connect() as conn:
            with conn.cursor() as cur:
                cur.execute(sql)
                return cur.fetchall()

    # 2) все вакансии
    def get_all_vacancies(self) -> List[Tuple[str, str, Any, Any, str]]:
        sql = """
        SELECT c.name, v.name, v.salary_from, v.salary_to, v.url
        FROM vacancies v
        JOIN companies c ON c.id = v.employer_id
        ORDER BY c.name, v.name;
        """
        with self._connect() as conn:
            with conn.cursor() as cur:
                cur.execute(sql)
                return cur.fetchall()

    # 3) средняя зарплата
    def get_avg_salary(self) -> float | None:
        sql = """
        SELECT AVG((COALESCE(salary_from, salary_to)
                 +  COALESCE(salary_to, salary_from)) / 2.0)
        FROM vacancies
        WHERE salary_from IS NOT NULL OR salary_to IS NOT NULL;
        """
        with self._connect() as conn:
            with conn.cursor() as cur:
                cur.execute(sql)
                row = cur.fetchone()
                return row[0] if row else None

    # 4) выше средней
    def get_vacancies_with_higher_salary(self) -> List[Tuple[str, str, float, str]]:
        sql = """
        WITH avg_sal AS (
          SELECT AVG((COALESCE(salary_from, salary_to)
                   + COALESCE(salary_to, salary_from)) / 2.0) AS a
          FROM vacancies
          WHERE salary_from IS NOT NULL OR salary_to IS NOT NULL
        )
        SELECT c.name,
               v.name,
               ((COALESCE(v.salary_from, v.salary_to)
               +  COALESCE(v.salary_to, v.salary_from)) / 2.0) AS salary_mid,
               v.url
        FROM vacancies v
        JOIN companies c ON c.id = v.employer_id, avg_sal
        WHERE ((COALESCE(v.salary_from, v.salary_to)
              +  COALESCE(v.salary_to, v.salary_from)) / 2.0) > avg_sal.a
        ORDER BY salary_mid DESC, c.name, v.name;
        """
        with self._connect() as conn:
            with conn.cursor() as cur:
                cur.execute(sql)
                return cur.fetchall()

    # 5) поиск по ключу
    def get_vacancies_with_keyword(self, keyword: str) -> List[Tuple[str, str, str]]:
        sql = """
        SELECT c.name, v.name, v.url
        FROM vacancies v
        JOIN companies c ON c.id = v.employer_id
        WHERE LOWER(v.name) LIKE '%' || LOWER(%s) || '%'
        ORDER BY c.name, v.name;
        """
        with self._connect() as conn:
            with conn.cursor() as cur:
                cur.execute(sql, (keyword,))
                return cur.fetchall()
