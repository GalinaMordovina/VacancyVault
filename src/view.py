from __future__ import annotations
from src.db import create_database_if_not_exists, create_tables
from src.etl import load_companies_and_vacancies
from src.db_manager import DBManager


def cmd_init_db() -> None:
    """Создать БД (если нет) и таблицы."""
    print("Создаю БД (если нет)...")
    create_database_if_not_exists()
    print("Создаю таблицы...")
    create_tables()
    print("Готово.")


def cmd_load_data() -> None:
    """Загрузить компании и вакансии из hh.ru в БД."""
    print("Загружаю данные по работодателям и вакансиям с hh.ru...")
    load_companies_and_vacancies()
    print("Готово.")


MENU = """
Выберите действие:
1) Показать компании и количество вакансий
2) Показать все вакансии (компания, вакансия, зарплата, ссылка)
3) Показать среднюю зарплату
4) Показать вакансии с зарплатой выше средней
5) Поиск вакансий по ключевому слову
0) Выход
> """


def cmd_menu() -> None:
    """Интерактивное меню запросов к БД."""
    mgr = DBManager()
    try:
        while True:
            choice = input(MENU).strip()
            if choice == "1":
                companies = mgr.get_companies_and_vacancies_count()
                if not companies:
                    print("Компании отсутствуют. Выполните: python main.py load-data")
                else:
                    for name, cnt in companies:
                        print(f"{name}: {cnt}")

            elif choice == "2":
                vacancies = mgr.get_all_vacancies()
                if not vacancies:
                    print("Пока нет вакансий в базе. Сначала выполните: python main.py load-data")
                else:
                    for name, title, sal, url in vacancies:
                        s = f"{sal:.0f}" if sal is not None else "—"
                        print(f"{name} | {title} | {s} | {url}")

            elif choice == "3":
                avg = mgr.get_avg_salary()
                print(f"Средняя зарплата: {avg:.0f}" if avg is not None else "Зарплата не указана.")

            elif choice == "4":
                higher = mgr.get_vacancies_with_higher_salary()
                if not higher:
                    print("Нет вакансий выше средней или база пуста.")
                else:
                    for name, title, sal, url in higher:
                        print(f"{name} | {title} | {sal:.0f} | {url}")

            elif choice == "5":
                kw = input("Ключевое слово: ").strip()
                matches = mgr.get_vacancies_with_keyword(kw)
                if not matches:
                    print("Ничего не найдено.")
                else:
                    for name, title, sal, url in matches:
                        s = f"{sal:.0f}" if sal is not None else "—"
                        print(f"{name} | {title} | {s} | {url}")

            elif choice == "0":
                break
            else:
                print("Неизвестный пункт. Повторите.")
    finally:
        mgr.close()


def print_help() -> None:
    """Печать справки по командам CLI."""
    print(
        """Vacancy-Vault CLI
Команды:
  init-db   — создать базу данных (если нет) и таблицы
  load-data — загрузить компании и вакансии из hh.ru
  menu      — интерактивное меню запросов
  help      — показать эту справку
"""
    )


__all__ = [
    "cmd_init_db",
    "cmd_load_data",
    "cmd_menu",
    "print_help",
]
