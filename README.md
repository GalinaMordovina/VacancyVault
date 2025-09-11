# VacancyVault

Сбор, хранение и просмотр вакансий с hh.ru по списку выбранных работодателей.

## Стек
Python 3.12 · PostgreSQL · requests · psycopg2 · pytest · flake8 · mypy

## Установка

### 1) Клонирование и окружение
```
git clone https://github.com/<your-username>/VacancyVault.git
cd VacancyVault
python -m venv .venv

# Windows:
.venv\Scripts\activate

# Linux/macOS:
source .venv/bin/activate
pip install -r requirements.txt
```
### 2) Настройки (.env)

Создайте файл `.env` в корне пример ключей и формата в `.env.example`

### 3) Инициализация и загрузка данных
```
# создание БД (если нет) и таблиц
python main.py init-db

# загрузка работодателей и вакансий с HH
python main.py load-data
```

### 4) Просмотр данных (меню)
```
python main.py menu
```

В меню доступны:
 - Компании и количество вакансий
 - Все вакансии (компания, вакансия, зарплата, ссылка)
 - Средняя зарплата
 - Вакансии с зарплатой выше средней
 - Поиск вакансий по ключевому слову

### 5) Тесты и качество кода
```
# тесты
pytest --cov=src

# стиль
flake8

# типы
mypy
```

### 6) Архитектура
 - src/api_client.py - HTTP-клиент HH (get_employer, iter_vacancies_by_employer)
 - src/etl.py - загрузка и нормализация данных, расчёт средней зарплаты
 - src/db.py - создание БД/таблиц, upsert компаний/вакансий
 - src/db_manager.py - SQL-методы из ТЗ (JOIN/AVG/фильтры)
 - src/view.py - CLI/меню
 - src/utils.py - мелкие утилиты (например, midpoint_salary)
 - src/files.py - экспорт в CSV
 
### Автор

[GalinaMordovina](https://github.com/GalinaMordovina)  
Email: [glukoloid@gmail.com](mailto:glukoloid@gmail.com)