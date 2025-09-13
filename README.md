# VacancyVault

Сбор, хранение и просмотр вакансий с hh.ru по списку выбранных работодателей.

## Стек
Python 3.12 · PostgreSQL · requests · psycopg2 · pytest · flake8 · mypy

## Установка

### 1) Клонирование и окружение
```
git clone https://github.com/GalinaMordovina/VacancyVault.git
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

ID компаний (что уже добавлены):
 - Контур **41862** [https://hh.ru/employer/41862](https://hh.ru/employer/41862) Экосистема 70+ продуктов, \~3 млн клиентов. Топ-20 работодателей hh.ru, сильное обучение и рост.
 - NAUMEN **42600** [https://hh.ru/employer/42600](https://hh.ru/employer/42600) Российский вендор корпоративных ИТ-решений, менторство и быстрый рост.
 - JetStyle **4515** [https://hh.ru/employer/4515](https://hh.ru/employer/4515) Digital-продакшн (разработка, UX, VR/AR). Головной офис (Екатеринбург). 
 - Сбер **3529** [https://hh.ru/employer/3529](https://hh.ru/employer/3529) Крупная финтех-экосистема, agile, развитая внутренняя мобильность.      
 - Яндекс **1740** [https://hh.ru/employer/1740](https://hh.ru/employer/1740) Крупнейшая технологическая компания, широкий стек и понятные грейды.  
 - Контур.Банк **817201** [https://hh.ru/employer/817201](https://hh.ru/employer/817201) Финтех внутри экосистемы Контура: интернет-банк и мобайл-банк для МСБ. 
 - Банк Синара **33305** [https://hh.ru/employer/33305](https://hh.ru/employer/33305) Финтех с сильным ИТ-направлением, регулярно открывают роли разработки. 
 - STEPLIFE (ООО «Степлайф») **11973212** [https://hh.ru/employer/11973212](https://hh.ru/employer/11973212) Производство высокотехнологичных протезов, робототехника и бионика.
 - Московское ПрОП **9035505** [https://hh.ru/employer/9035505](https://hh.ru/employer/9035505) Протезно-ортопедическое предприятие, вакансии в Москве.
 - Моторика **1870517** [https://hh.ru/employer/1870517](https://hh.ru/employer/1870517) Компания в сфере протезирования/биотеха; вакансии в Москве. 

Есть возможность подставить свои компании:

Открой `.env` в корне проекта и укажи свои ID (через запятую, без пробелов):
```
EMPLOYER_IDS=41862,42600,4515,3529,1740,817201,33305,11973212,9035505,1870517
```

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