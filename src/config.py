from __future__ import annotations
import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Settings:
    """
    Settings — неизменяемая (frozen=True) конфигурация приложения:
    читаем значения из окружения, подставляем дефолты.
    """

    # Подключение к PostgreSQL
    db_host: str = os.getenv("DB_HOST", "localhost")
    db_port: int = int(os.getenv("DB_PORT", "5432"))
    db_name: str = os.getenv("DB_NAME", "vacancy_vault")
    db_user: str = os.getenv("DB_USER", "postgres")
    db_password: str = os.getenv("DB_PASSWORD", "postgres")

    # Список employer_ids (через запятую) в кортеж int
    employer_ids: tuple[int, ...] = tuple(
        int(x.strip())
        for x in os.getenv("EMPLOYER_IDS", "").split(",")
        if x.strip().isdigit()
    )

    # User-Agent для запросов к HH API
    user_agent: str = os.getenv("USER_AGENT", "Vacancy-Vault/1.0")


# Единственный экземпляр настроек, импортируем его как: from src.config import settings
settings = Settings()
