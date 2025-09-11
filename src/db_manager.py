from __future__ import annotations
from typing import List, Tuple, Optional
import psycopg2
from types import TracebackType
from src.config import settings


class DBManager:
    """Работа с БД PostgreSQL (чтение/запросы)."""

    def __init__(self) -> None:
        self.conn = psycopg2.connect(
            host=settings.db_host,
            port=settings.db_port,
            dbname=settings.db_name,
            user=settings.db_user,
            password=settings.db_password,
        )
        self.conn.autocommit = True

    # этот метод добавила
    def close(self) -> None:
        """Закрывает соединение с БД."""
        if self.conn:
            self.conn.close()

    # (опционально) чтобы можно было писать: with DBManager() as mgr:
    def __enter__(self) -> "DBManager":
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None:
        self.close()

    # Методы по заднию
    def get_companies_and_vacancies_count(self) -> List[Tuple[str, int]]:
        """Список компаний и количество вакансий у каждой."""
        with self.conn.cursor() as cur:
            cur.execute(
                """
                SELECT c.name, COUNT(v.vacancy_id) AS vacancies_count
                FROM companies c
                LEFT JOIN vacancies v ON v.company_id = c.employer_id
                GROUP BY c.employer_id, c.name
                ORDER BY vacancies_count DESC, c.name;
                """
            )
            return cur.fetchall()

    def get_all_vacancies(self) -> List[Tuple[str, str, Optional[float], str]]:
        """Все вакансии: компания, название, средняя з/п, ссылка."""
        with self.conn.cursor() as cur:
            cur.execute(
                """
                SELECT c.name, v.title, v.salary_avg, v.url
                FROM vacancies v
                JOIN companies c ON c.employer_id = v.company_id
                ORDER BY c.name, v.title;
                """
            )
            return cur.fetchall()

    def get_avg_salary(self) -> Optional[float]:
        """Средняя зарплата по всем вакансиям (по salary_avg)."""
        with self.conn.cursor() as cur:
            cur.execute("SELECT AVG(salary_avg) FROM vacancies WHERE salary_avg IS NOT NULL;")
            row = cur.fetchone()
            return row[0] if row else None

    def get_vacancies_with_higher_salary(self) -> List[Tuple[str, str, float, str]]:
        """Вакансии с зарплатой выше средней."""
        with self.conn.cursor() as cur:
            cur.execute(
                """
                WITH avg_salary AS (
                    SELECT AVG(salary_avg) AS avg_val
                    FROM vacancies
                    WHERE salary_avg IS NOT NULL
                )
                SELECT c.name, v.title, v.salary_avg, v.url
                FROM vacancies v
                JOIN companies c ON c.employer_id = v.company_id, avg_salary a
                WHERE v.salary_avg IS NOT NULL AND v.salary_avg > a.avg_val
                ORDER BY v.salary_avg DESC;
                """
            )
            return cur.fetchall()

    def get_vacancies_with_keyword(self, keyword: str) -> List[Tuple[str, str, Optional[float], str]]:
        """Вакансии, где в названии есть keyword (LIKE, без регистра)."""
        pattern = f"%{keyword.lower()}%"
        with self.conn.cursor() as cur:
            cur.execute(
                """
                SELECT c.name, v.title, v.salary_avg, v.url
                FROM vacancies v
                JOIN companies c ON c.employer_id = v.company_id
                WHERE LOWER(v.title) LIKE %s
                ORDER BY c.name, v.title;
                """,
                (pattern,),
            )
            return cur.fetchall()
