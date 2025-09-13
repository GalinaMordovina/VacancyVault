from __future__ import annotations
from typing import Optional


def midpoint_salary(salary_from: Optional[float], salary_to: Optional[float]) -> Optional[float]:
    """
    Возвращает среднее из вилки зарплаты:
    - если задана только одна граница - возвращает её;
    - если обе None — None;
    - иначе среднее арифметическое.
    """
    if salary_from is None and salary_to is None:
        return None
    if salary_from is None and salary_to is not None:
        return salary_to
    if salary_to is None and salary_from is not None:
        return salary_from

    # здесь обе границы заданы (не None) - подстрахуем сузителем типов для mypy
    assert salary_from is not None and salary_to is not None
    return (salary_from + salary_to) / 2.0
