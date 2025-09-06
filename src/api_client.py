class HHClient:
    """ HH API client (заглушка - реализацию добавлю на следующем шаге)."""
    def __init__(self, user_agent: str = "Vacancy-Vault/1.0") -> None:
        self.user_agent = user_agent

    # реализую позже:
    # def get_employer(self, employer_id: int) -> dict: ...
    # def iter_vacancies_by_employer(self, employer_id: int): ...
