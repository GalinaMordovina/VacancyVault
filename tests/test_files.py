from __future__ import annotations
import csv
from pathlib import Path
from src.files import export_to_csv


def test_export_to_csv_creates_dirs_and_writes_content(tmp_path: Path) -> None:
    # Дано: данные с не-ASCII и запятыми, плюс заголовки
    rows = [
        ["ACorp", "Dev", 100000],
        ["Бета", "QA, junior", 50000],  # запятая в ячейке → проверим CSV-квотинг
    ]
    headers = ["company", "title", "salary"]

    # Куда пишем: вложенный путь, каталоги не существуют
    out_path = tmp_path / "nested" / "reports" / "vacancies.csv"

    # Действие
    export_to_csv(rows, headers, str(out_path))

    # Проверки: файл создан
    assert out_path.exists()

    # Содержимое соответствует ожидаемому (UTF-8, корректные кавычки/запятые)
    with out_path.open("r", newline="", encoding="utf-8") as f:
        content = list(csv.reader(f))

    expected = [headers] + [[str(c) for c in r] for r in rows]
    assert content == expected
