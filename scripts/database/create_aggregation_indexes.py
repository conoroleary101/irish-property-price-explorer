import os
import sqlite3
import time
from contextlib import closing
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

DB_PATH = Path(os.environ.get("DATABASE", "property.db"))
if not DB_PATH.is_absolute():
    DB_PATH = ROOT / DB_PATH

INDEXES = {
    "idx_sales_market_price": """
        CREATE INDEX IF NOT EXISTS idx_sales_market_price
        ON sales(price)
        WHERE not_full_market_price = 0
    """,
    "idx_sales_market_type_price": """
        CREATE INDEX IF NOT EXISTS idx_sales_market_type_price
        ON sales(description_of_property, price)
        WHERE not_full_market_price = 0
    """,
    "idx_sales_market_county_price": """
    CREATE INDEX IF NOT EXISTS idx_sales_market_county_price
    ON sales(county, price)
    WHERE not_full_market_price = 0
    """,
}


def main():
    if not DB_PATH.is_file():
        raise FileNotFoundError(DB_PATH)

    print("Database:", DB_PATH)

    with closing(sqlite3.connect(DB_PATH)) as db:
        with db:
            for name, sql in INDEXES.items():
                start = time.perf_counter()
                db.execute(sql)
                elapsed = time.perf_counter() - start
                print(f"{name}: OK ({elapsed:.2f}s)")

            # Update SQLite query planner statistics.
            db.execute("ANALYZE")

        print("\nAvailable indexes:")
        for row in db.execute("PRAGMA index_list(sales)"):
            print(row[1])

    print("\nIndex setup complete.")


if __name__ == "__main__":
    main()
