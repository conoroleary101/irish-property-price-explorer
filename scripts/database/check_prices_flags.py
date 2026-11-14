import csv
from decimal import Decimal
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CSV_PATH = ROOT / "data" / "PPR-ALL.csv"

flags = Counter()
fractional_prices = 0
examples = []

with open(CSV_PATH, encoding="cp1252", newline="") as file:
    reader = csv.DictReader(file)
    price_col = next(
        col for col in reader.fieldnames
        if col.startswith("Price")
    )

    for row in reader:
        raw_price = row[price_col]
        cleaned = "".join(
            char for char in raw_price
            if char.isdigit() or char == "."
        )
        price = Decimal(cleaned)

        if price != price.to_integral_value():
            fractional_prices += 1
            if len(examples) < 5:
                examples.append(raw_price)

        for column in ("Not Full Market Price", "VAT Exclusive"):
            flags[(column, row[column].strip())] += 1

print("Prices with non-zero cents:", fractional_prices)
print("Examples:", examples)
print("Flag values:", dict(flags))
