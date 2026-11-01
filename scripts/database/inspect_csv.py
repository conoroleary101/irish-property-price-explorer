import csv
from itertools import islice
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CSV_PATH = ROOT / "data" / "PPR-ALL.csv"

with open(CSV_PATH, encoding="cp1252", newline="") as file:
    reader = csv.DictReader(file)

    print("CSV HEADERS:")
    for header in reader.fieldnames:
        print(repr(header))

    print("\nFIRST 5 RECORDS:")
    for number, row in enumerate(islice(reader, 5), start=1):
        print(f"\nRecord {number}")
        for column, value in row.items():
            print(f"{column!r}: {value!r}")
