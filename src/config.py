import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()

@dataclass(frozen=True)
class Settings:
    db_host: str = os.getenv("DB_HOST", "localhost")
    db_port: int = int(os.getenv("DB_PORT", "5432"))
    db_name: str = os.getenv("DB_NAME", "vacancy_vault")
    db_user: str = os.getenv("DB_USER", "postgres")
    db_password: str = os.getenv("DB_PASSWORD", "postgres")
    employer_ids: tuple[int, ...] = tuple(
        int(x.strip()) for x in os.getenv("EMPLOYER_IDS", "").split(",") if x.strip().isdigit()
    )

settings = Settings()
