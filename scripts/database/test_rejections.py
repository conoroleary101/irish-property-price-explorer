import csv
import sqlite3
import sys
import tempfile
from pathlib import Path
from contextlib import closing

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

import load_data


def main():
    with tempfile.TemporaryDirectory() as directory:
        folder = Path(directory)
        csv_path = folder / "PPR-ALL.csv"
        db_path = folder / "test.db"
        log_path = folder / "import_rejections.log"

        headers = [
            "Date of Sale (dd/mm/yyyy)",
            "Address",
            "County",
            "Eircode",
            "Price (\u20ac)",
            "Not Full Market Price",
            "VAT Exclusive",
            "Description of Property",
            "Property Size Description",
        ]

        records = [
            ["01/01/2024", "Valid House", "Cork", "",
             "€250,000.00", "Yes", "No", "Second-Hand", ""],
            ["31/02/2024", "Invalid Date", "Dublin", "",
             "€300,000.00", "No", "No", "Second-Hand", ""],
            ["02/01/2024", "Invalid Price", "Galway", "",
             "bad-price", "No", "No", "Second-Hand", ""],
        ]

        with csv_path.open(
            "w", encoding="cp1252", newline=""
        ) as file:
            writer = csv.writer(file)
            writer.writerow(headers)
            writer.writerows(records)

        schema = (
            ROOT / "scripts" / "schema.sql"
        ).read_text(encoding="utf-8")

        with closing(sqlite3.connect(db_path)) as db:
            db.executescript(schema)

        load_data.CSV_PATH = csv_path
        load_data.DB_PATH = db_path
        load_data.LOG_PATH = log_path

        load_data.main()

        with closing(sqlite3.connect(db_path)) as db:
            loaded = db.execute(
                "SELECT COUNT(*) FROM sales"
            ).fetchone()[0]

            flagged = db.execute(
                "SELECT COUNT(*) FROM sales "
                "WHERE not_full_market_price = 1"
            ).fetchone()[0]

        log = log_path.read_text(encoding="utf-8")

        assert loaded == 1, f"Expected 1 row, got {loaded}"
        assert flagged == 1, "Flagged row was not retained"
        assert "Line 3:" in log, "Invalid date not logged"
        assert "Line 4:" in log, "Invalid price not logged"
        assert "31/02/2024" in log
        assert "bad-price" in log

        print("\nRejected-row test: PASS")


if __name__ == "__main__":
    main()
