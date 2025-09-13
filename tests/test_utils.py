from __future__ import annotations
from src.utils import midpoint_salary


def test_midpoint_both_none() -> None:
    assert midpoint_salary(None, None) is None


def test_midpoint_only_from() -> None:
    assert midpoint_salary(100.0, None) == 100.0


def test_midpoint_only_to() -> None:
    assert midpoint_salary(None, 150.0) == 150.0


def test_midpoint_both() -> None:
    assert midpoint_salary(100.0, 150.0) == 125.0
