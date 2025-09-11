from __future__ import annotations
import argparse
from src.view import cmd_init_db, cmd_load_data, cmd_menu, print_help


def main() -> None:
    parser = argparse.ArgumentParser(prog="Vacancy-Vault")
    parser.add_argument(
        "command",
        nargs="?",                      # аргумент необязательный
        choices=["init-db", "load-data", "menu"],
        help="Команда: init-db | load-data | menu",
    )
    args = parser.parse_args()

    cmd = args.command or "menu"       # если не передали команду, идём в меню

    if cmd == "init-db":
        cmd_init_db()
    elif cmd == "load-data":
        cmd_load_data()
    elif cmd == "menu":
        cmd_menu()
    else:
        print_help()


if __name__ == "__main__":
    main()
