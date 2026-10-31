"""
Hand-calculated expectations for tests/fixtures/sample_ppr.csv (20 rows):
  Dublin rows 1-6:   300k+400k+500k+600k+700k+800k = 3,300,000
  Cork rows 7-12:    150k+200k+250k+300k+350k+400k = 1,650,000
  Galway rows 13-16: 100k+200k+300k+400k           = 1,000,000
  Rows 19-20 are 100k each but have bad dates, so the parseable prices total
  3,300,000 + 1,650,000 + 1,000,000 + 200,000 = 6,150,000 (18 values).
  Rows 17-18 have a blank / "N/A" price (2 failures).
  Rows 19-20 have an invalid / wrong-format date (2 failures).
"""
from datetime import date

import pytest

from app.parsing import clean_price, parse_date


@pytest.mark.parametrize("raw, expected", [
    ("€250,000.00", 250000.0),     # normal value
    ("€1,250,000.00", 1250000.0),  # several thousands separators
    ("", None),                    # blank
    ("N/A", None),                 # malformed
    ("€25O,000", None),            # malformed: letter O instead of zero
])
def test_clean_price(raw, expected):
    assert clean_price(raw) == expected


def test_parse_date_valid():
    assert parse_date("01/03/2023") == date(2023, 3, 1)


@pytest.mark.parametrize("bad", ["31/02/2023", "2023-05-07", "", "abc"])
def test_parse_date_rejects_invalid(bad):
    with pytest.raises(ValueError):
        parse_date(bad)


def test_fixture_price_total(fixture_rows, price_col):
    prices = [clean_price(r[price_col]) for r in fixture_rows]
    good = [p for p in prices if p is not None]
    assert len(fixture_rows) == 20
    assert len(good) == 18
    assert sum(good) == 6_150_000


def test_fixture_date_counts(fixture_rows):
    ok = 0
    for r in fixture_rows:
        try:
            parse_date(r["Date of Sale (dd/mm/yyyy)"])
            ok += 1
        except ValueError:
            pass
    assert ok == 18
