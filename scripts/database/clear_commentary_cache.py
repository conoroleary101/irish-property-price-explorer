"""
Clear stored AI commentary without affecting property sales.

Usage:
    python scripts/database/clear_commentary_cache.py

The database is selected through the existing DATABASE configuration.
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from app import create_app
from app.cache import clear_cache


def main():
    app = create_app()

    print("Database:", app.config["DATABASE"])
    print("This will delete cached AI commentary only.")
    confirmation = input("Type CLEAR to continue: ")

    if confirmation != "CLEAR":
        print("Cancelled. No changes made.")
        return

    with app.app_context():
        deleted = clear_cache()

    print(f"Cache cleared. Entries removed: {deleted}")


if __name__ == "__main__":
    main()
