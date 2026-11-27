"""
Warm the persistent commentary cache for selected counties.

Preview without API requests:
    python scripts/database/warm_commentary_cache.py Cork Dublin

Generate and persist commentary:
    python scripts/database/warm_commentary_cache.py Cork Dublin --execute

Optional year filters must match the demonstration URL.
The DATABASE setting determines which SQLite database is used.
"""

import argparse
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from app import create_app
from app.cache import fingerprint, get_cached
from app.commentary import generate_commentary
from app.queries import get_aggregate_stats, get_counties


def build_summary(filters):
    """Build exactly the same summary dictionary as the index route."""
    stats = get_aggregate_stats(filters)

    return {
        "count": stats["count"],
        "mean": stats["mean"],
        "median": stats["median"],
        "excluded": stats["excluded"],
        "county": filters.get("county"),
        "year_from": filters.get("year_from"),
        "year_to": filters.get("year_to"),
    }


def main():
    parser = argparse.ArgumentParser(
        description="Preview or warm cached AI commentary."
    )
    parser.add_argument("counties", nargs="+")
    parser.add_argument("--year-from", type=int)
    parser.add_argument("--year-to", type=int)
    parser.add_argument(
        "--execute",
        action="store_true",
        help="Allow live API calls and cache the successful responses.",
    )

    args = parser.parse_args()

    if args.year_from and args.year_to:
        if args.year_from > args.year_to:
            parser.error("year-from cannot exceed year-to")

    for year in (args.year_from, args.year_to):
        if year is not None and not 2010 <= year <= 2100:
            parser.error("Years must be between 2010 and 2100")

    app = create_app()

    with app.app_context():
        print("Database:", app.config["DATABASE"])
        print("Mode:", "EXECUTE" if args.execute else "DRY RUN")

        available = {
            county.casefold(): county
            for county in get_counties()
        }

        # Validate all requested counties before making any API calls.
        counties = []
        for requested in args.counties:
            county = available.get(requested.strip().casefold())
            if county is None:
                parser.error(f"Unknown county: {requested}")
            if county not in counties:
                counties.append(county)

        failures = 0

        for county in counties:
            filters = {"county": county}

            if args.year_from is not None:
                filters["year_from"] = args.year_from
            if args.year_to is not None:
                filters["year_to"] = args.year_to

            summary = build_summary(filters)
            key = fingerprint(summary)

            print(f"\nCounty: {county}")
            print("Count:", summary["count"])
            print("Cache key:", key)

            if not args.execute:
                print("DRY RUN: no API call or cache write")
                continue

            cached = get_cached(key)
            if cached is not None:
                print("PASS: already cached")
                continue

            if not (
                os.environ.get("GROQ_API_KEY")
                or os.environ.get("COMMENTARY_API_KEY")
            ):
                print("FAIL: no commentary API key configured")
                failures += 1
                continue

            response = generate_commentary(summary)

            # Verify that the result was actually persisted to SQLite.
            if response and get_cached(key) == response:
                print("PASS: generated and persisted")
            else:
                print("FAIL: commentary was not persisted")
                failures += 1

        if failures:
            raise SystemExit(f"{failures} cache warm-up(s) failed")

    print("\nWarm-up complete.")


if __name__ == "__main__":
    main()
