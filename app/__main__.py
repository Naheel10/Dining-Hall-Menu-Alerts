"""Module CLI entrypoints."""

import argparse

from app import create_app
from app.services.menu_matcher import run_menu_check_for_all_users


def main() -> None:
    parser = argparse.ArgumentParser(description="UW Dining Menu Alerts utilities")
    parser.add_argument("command", choices=["run_menu_check"])
    args = parser.parse_args()

    flask_app = create_app()
    with flask_app.app_context():
        if args.command == "run_menu_check":
            summary = run_menu_check_for_all_users(send_email=True)
            print(summary)


if __name__ == "__main__":
    main()
