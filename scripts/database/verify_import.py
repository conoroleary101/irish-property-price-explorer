import os
import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

DB_PATH = Path(os.environ.get("DATABASE", "property.db"))
if not DB_PATH.is_absolute():
    DB_PATH = ROOT / DB_PATH

# Expected values for the verified 23 October 2026 dataset
EXPECTED = {
    "Total records": 814413,
    "Full-market-price records": 772923,
    "Flagged records": 41490,
    "NULL Eircodes": 558595,
    "NULL property sizes": 761567,
}

QUERIES = {
    "Total records":
        "SELECT COUNT(*) FROM sales",
    "Full-market-price records":
        "SELECT COUNT(*) FROM sales WHERE not_full_market_price = 0",
    "Flagged records":
        "SELECT COUNT(*) FROM sales WHERE not_full_market_price = 1",
    "NULL Eircodes":
        "SELECT COUNT(*) FROM sales WHERE eircode IS NULL",
    "NULL property sizes":
        "SELECT COUNT(*) FROM sales WHERE property_size_description IS NULL",
}


def main():
    if not DB_PATH.is_file():
        raise FileNotFoundError(DB_PATH)

    connection = sqlite3.connect(DB_PATH)

    try:
        results = {}

        for label, query in QUERIES.items():
            results[label] = connection.execute(query).fetchone()[0]

        indexes = {
            row[1]
            for row in connection.execute("PRAGMA index_list(sales)")
        }

        print("DATABASE VERIFICATION\n")

        passed = True

        for label, actual in results.items():
            expected = EXPECTED[label]
            match = actual == expected
            passed &= match

            print(
                f"{label}: {actual} "
                f"(expected {expected}) - "
                f"{'PASS' if match else 'FAIL'}"
            )

        required_indexes = {
            "idx_sales_county",
            "idx_sales_date"
        }

        indexes_valid = required_indexes <= indexes
        passed &= indexes_valid

        print(
            f"Required indexes: "
            f"{'PASS' if indexes_valid else 'FAIL'}"
        )

        print("\nSample records:")

        for row in connection.execute(
            "SELECT date_of_sale, address, county, price "
            "FROM sales ORDER BY id LIMIT 3"
        ):
            print(row)

        print(
            "\nOverall verification:",
            "PASS" if passed else "FAIL"
        )

        if not passed:
            raise SystemExit(1)

    finally:
        connection.close()


if __name__ == "__main__":
    main()
