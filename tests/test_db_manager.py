from __future__ import annotations
import pytest
import psycopg2
from src.config import settings
from src.db import create_tables
from src.db_manager import DBManager


@pytest.fixture
def sample_data() -> None:
    """Готовим минимальные данные для всех тестов DBManager."""
    create_tables()
    con = psycopg2.connect(
        host=settings.db_host,
        port=settings.db_port,
        dbname=settings.db_name,
        user=settings.db_user,
        password=settings.db_password,
    )
    try:
        with con, con.cursor() as cur:
            # чистим и заполняем
            cur.execute("TRUNCATE vacancies, companies RESTART IDENTITY CASCADE;")
            cur.execute(
                """
                INSERT INTO companies (employer_id, name, area, open_vacancies, url) VALUES
                (1, 'Test A', NULL, NULL, 'https://example.com/a'),
                (2, 'Test B', NULL, NULL, 'https://example.com/b');
                """
            )
            # salary_avg подобраны так, чтобы средняя была 105000
            # и выше неё попали 125000 и 110000
            cur.execute(
                """
                INSERT INTO vacancies
                    (vacancy_id, company_id, title, url,
                     salary_from, salary_to, salary_currency, salary_avg, published_at)
                VALUES
                    (101, 1, 'Python Developer', 'https://hh.ru/vacancy/101',
                     NULL, NULL, 'RUR', 125000, '2024-02-01 10:00:00'),
                    (102, 1, 'Data Analyst', 'https://hh.ru/vacancy/102',
                     NULL, NULL, 'RUR', 110000, '2024-02-02 10:00:00'),
                    (201, 2, 'Senior Backend', 'https://hh.ru/vacancy/201',
                     NULL, NULL, 'RUR', 80000,  '2024-02-03 10:00:00');
                """
            )
    finally:
        con.close()


def test_get_companies_and_vacancies_count(sample_data) -> None:
    mgr = DBManager()
    rows = mgr.get_companies_and_vacancies_count()
    # Ожидаем: Test A → 2 вакансии, Test B → 1 вакансия
    as_dict = {name: cnt for name, cnt in rows}
    assert as_dict["Test A"] == 2
    assert as_dict["Test B"] == 1
    mgr.close()


def test_get_all_vacancies(sample_data) -> None:
    mgr = DBManager()
    rows = mgr.get_all_vacancies()
    # Формат: (company_name, title, salary_avg, url)
    assert len(rows) == 3
    any_row = rows[0]
    assert isinstance(any_row[0], str)
    assert isinstance(any_row[1], str)
    # salary_avg может быть None, но у нас все заданы
    assert any_row[2] is not None
    assert any_row[3].startswith("http")
    mgr.close()


def test_get_avg_salary(sample_data) -> None:
    mgr = DBManager()
    # (125000 + 80000 + 110000) / 3 = 105000
    avg = mgr.get_avg_salary()
    assert avg is not None
    assert round(avg) == 105000
    mgr.close()


def test_get_vacancies_with_higher_salary(sample_data) -> None:
    mgr = DBManager()
    rows = mgr.get_vacancies_with_higher_salary()
    # Средняя = 105000, выше неё: 125000 и 110000 → 2 шт
    assert len(rows) == 2
    titles = {t for _, t, _, _ in rows}
    assert "Python Developer" in titles
    assert "Data Analyst" in titles
    mgr.close()


def test_get_vacancies_with_keyword(sample_data) -> None:
    mgr = DBManager()
    rows = mgr.get_vacancies_with_keyword("python")
    # Должен найти "Python Developer" вне зависимости от регистра
    assert len(rows) == 1
    assert rows[0][1] == "Python Developer"
    mgr.close()
