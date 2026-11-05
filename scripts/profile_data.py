import csv
import statistics
from collections import Counter
from datetime import datetime

PATH = "data/PPR-ALL.csv"

total = 0
null_counts = Counter()
prices = []
nfmp = 0
counties = Counter()
earliest = latest = None

with open(PATH, encoding="cp1252", newline="") as f:
    reader = csv.DictReader(f)
    columns = reader.fieldnames
    print("Columns:", columns)

    # The euro sign in the price header is corrupted in the source file,
    # so find the column by its prefix instead of its exact name.
    price_col = next(c for c in columns if c.startswith("Price"))

    for row in reader:
        total += 1

        # IPPE-73: count empty values per column
        for col in columns:
            if not (row[col] or "").strip():
                null_counts[col] += 1

        # IPPE-72: date range
        d = datetime.strptime(row["Date of Sale (dd/mm/yyyy)"], "%d/%m/%Y")
        if earliest is None or d < earliest:
            earliest = d
        if latest is None or d > latest:
            latest = d

        # IPPE-74: prices (keep only digits and the decimal point)
        cleaned = "".join(ch for ch in row[price_col] if ch.isdigit() or ch == ".")
        prices.append(float(cleaned))
        if row["Not Full Market Price"] == "Yes":
            nfmp += 1

        # IPPE-75: rows per county
        counties[row["County"]] += 1

print("\nTotal rows:", total)
print("Earliest sale:", earliest.date())
print("Latest sale:", latest.date())

print("\nNull % per column:")
for col in columns:
    print(f"  {col}: {null_counts[col] / total * 100:.2f}%")

print("\nMin price:", min(prices))
print("Max price:", max(prices))
print("Median price:", statistics.median(prices))
print(f"Not Full Market Price rows: {nfmp} ({nfmp / total * 100:.2f}%)")

print("\nRows per county:")
for county, count in counties.most_common():
    print(f"  {county}: {count}")