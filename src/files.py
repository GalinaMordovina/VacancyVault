from __future__ import annotations
import csv
import os
from typing import Iterable, Sequence, Any


def export_to_csv(rows: Iterable[Sequence[Any]], headers: Sequence[str], path: str) -> None:
    """Простой экспорт в CSV (создаёт каталоги при необходимости)."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        writer.writerows(rows)
