from datetime import datetime
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP

def clean_price(value):
    if not isinstance(value, str) or not value.strip():
        return None

    try:
        cleaned = value.replace("€", "").replace(",", "").strip()
        price = Decimal(cleaned)

        if not price.is_finite() or price < 0:
            return None

        return int(price.quantize(Decimal("1"), rounding=ROUND_HALF_UP))

    except (InvalidOperation, ValueError):
        return None


def parse_date(value):
    if not isinstance(value, str) or not value.strip():
        return None

    try:
        date = datetime.strptime(value.strip(), "%d/%m/%Y")
        return date.strftime("%Y-%m-%d")

    except ValueError:
        return None
