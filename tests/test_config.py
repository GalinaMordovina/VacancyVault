from __future__ import annotations
from _pytest.monkeypatch import MonkeyPatch
import importlib
import os


def test_settings_reads_env(monkeypatch: MonkeyPatch) -> None:
    # Подменяем окружение
    monkeypatch.setenv("DB_HOST", "localhost_test")
    monkeypatch.setenv("DB_PORT", "5433")
    monkeypatch.setenv("DB_NAME", "db_test")
    monkeypatch.setenv("DB_USER", "user_test")
    monkeypatch.setenv("DB_PASSWORD", "pass_test")

    # Перезагружаем модуль, чтобы пересчитать settings
    from src import config as config_module
    importlib.reload(config_module)

    s = config_module.settings
    assert s.db_host == "localhost_test"
    assert s.db_port == 5433 or str(s.db_port) == "5433"  # смотря как типизировали
    assert s.db_name == "db_test"
    assert s.db_user == "user_test"
    assert s.db_password == "pass_test"

    # Возвращаем исходный модуль (чтобы другие тесты не зависели)
    os.environ.pop("DB_HOST", None)
    os.environ.pop("DB_PORT", None)
    os.environ.pop("DB_NAME", None)
    os.environ.pop("DB_USER", None)
    os.environ.pop("DB_PASSWORD", None)
    importlib.reload(config_module)
