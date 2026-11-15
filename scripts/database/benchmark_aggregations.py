import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from app import create_app
from app.queries import get_aggregate_stats

TARGET_SECONDS = 1.0

CASES = {
    "All sales": {},
    "County (Cork)": {"county": "Cork"},
    "Year range": {"year_from": 2018, "year_to": 2020},
    "Price range": {
        "price_min": 200000,
        "price_max": 350000,
    },
    "Property type": {
        "property_type": "Second-Hand Dwelling house /Apartment",
    },
    "Combined filters": {
        "county": "Dublin",
        "year_from": 2015,
        "year_to": 2020,
        "price_min": 200000,
        "price_max": 500000,
    },
}


def main():
    app = create_app()
    passed = True

    with app.app_context():
        for label, filters in CASES.items():
            start = time.perf_counter()
            result = get_aggregate_stats(filters)
            elapsed = time.perf_counter() - start

            ok = elapsed < TARGET_SECONDS
            passed = passed and ok

            print(f"\n{label}")
            print(f"Duration: {elapsed:.4f} seconds")
            print(f"Results: {result}")
            print("PASS" if ok else "FAIL")

    print("\nOverall:", "PASS" if passed else "FAIL")

    if not passed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
