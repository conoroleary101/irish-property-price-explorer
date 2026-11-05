import csv
import os
import sqlite3
import time
from pathlib import Path

from conversions import clean_price, parse_date


ROOT = Path(__file__).resolve().parents[1]
CSV_PATH = ROOT / "data" / "PPR-ALL.csv"
LOG_PATH = ROOT / "data" / "import_rejections.log"

DB_PATH = Path(os.environ.get("DATABASE", "property.db"))
if not DB_PATH.is_absolute():
    DB_PATH = ROOT / DB_PATH

BATCH_SIZE = 10000

INSERT_SQL = """
INSERT INTO sales (
    date_of_sale, address, county, eircode, price,
    not_full_market_price, vat_exclusive,
    description_of_property, property_size_description
)
VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
"""


def to_flag(value):
    value = value.strip().lower()
    if value not in ("yes", "no"):
        raise ValueError(f"Invalid flag value: {value!r}")
    return 1 if value == "yes" else 0


def main():
    start = time.perf_counter()
    source_rows = 0
    loaded = 0
    rejected = 0
    flagged = 0
    batch = []

    if not CSV_PATH.is_file():
        raise FileNotFoundError(CSV_PATH)

    if not DB_PATH.is_file():
        raise FileNotFoundError(DB_PATH)

    connection = sqlite3.connect(DB_PATH)

    try:
        with CSV_PATH.open(encoding="cp1252", newline="") as file, \
             LOG_PATH.open("w", encoding="utf-8") as log:

            reader = csv.DictReader(file)
            price_column = next(
                column for column in reader.fieldnames
                if column.startswith("Price")
            )

            with connection:
                connection.execute("DELETE FROM sales")

                for line_number, row in enumerate(reader, start=2):
                    source_rows += 1

                    date = parse_date(row["Date of Sale (dd/mm/yyyy)"])
                    price = clean_price(row[price_column])

                    if date is None or price is None:
                        rejected += 1
                        log.write(
                            f"Line {line_number}: "
                            f"date={row['Date of Sale (dd/mm/yyyy)']!r}, "
                            f"price={row[price_column]!r}\n"
                        )
                        continue

                    market_flag = to_flag(row["Not Full Market Price"])
                    vat_flag = to_flag(row["VAT Exclusive"])

                    batch.append((
                        date,
                        row["Address"].strip(),
                        row["County"].strip(),
                        row["Eircode"].strip() or None,
                        price,
                        market_flag,
                        vat_flag,
                        row["Description of Property"].strip() or None,
                        row["Property Size Description"].strip() or None
                    ))

                    flagged += market_flag

                    if len(batch) >= BATCH_SIZE:
                        connection.executemany(INSERT_SQL, batch)
                        loaded += len(batch)
                        batch.clear()

                if batch:
                    connection.executemany(INSERT_SQL, batch)
                    loaded += len(batch)

    finally:
        connection.close()

    elapsed = time.perf_counter() - start

    print("Source rows:", source_rows)
    print("Rows loaded:", loaded)
    print("Not Full Market Price:", flagged)
    print("Rows rejected:", rejected)
    print(f"Import duration: {elapsed:.2f} seconds")

    assert loaded + rejected == source_rows


if __name__ == "__main__":
    main()
