"""Parsing helpers for the PPR data: prices and dates."""
import re
from datetime import date, datetime

_NUMBER = re.compile(r"^(\d{1,3}(,\d{3})+|\d+)(\.\d+)?$")


def clean_price(raw):
    """Turn a raw price like '€250,000.00' into 250000.0.

    Returns None for blank or malformed values. Leading non-digit characters
    are dropped, so a corrupted euro sign in the source file is tolerated.
    """
    if raw is None:
        return None
    text = re.sub(r"^\D+", "", str(raw).strip())
    if not _NUMBER.match(text):
        return None
    return float(text.replace(",", ""))


def parse_date(raw):
    """Parse a dd/mm/yyyy string into a date. Raises ValueError if invalid."""
    if not isinstance(raw, str):
        raise ValueError(f"Date must be a string, got {raw!r}")
    return datetime.strptime(raw.strip(), "%d/%m/%Y").date()
