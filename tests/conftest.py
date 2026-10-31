import csv
from pathlib import Path
import pytest

FIXTURE = Path(__file__).parent / "fixtures" / "sample_ppr.csv"


@pytest.fixture
def fixture_rows():
    with open(FIXTURE, encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


@pytest.fixture
def price_col(fixture_rows):
    # Match by prefix: in the real file the euro sign in the header is corrupted
    return next(c for c in fixture_rows[0] if c.startswith("Price"))
