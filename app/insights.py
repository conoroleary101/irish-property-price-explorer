"""
Prepare numerical summary facts for AI-generated commentary

This module contains no database access or LLM calls
"""

from statistics import median


MIN_YEARS = 2


def summarise(county, year_from, year_to, yearly_medians, count):
    """Summarise yearly median prices for a filtered property selection.

    yearly_medians: ascending list of (year, median_price) tuples.
    count: total matching full-market-price sales.

    The returned median is the median of the supplied yearly medians,
    not the median of all individual sale prices.
    """
    result = {
        "county": county or "All counties",
        "period": (year_from, year_to),
        "count": count,
        "median": None,
        "pct_change": None,
        "biggest_move_year": None,
        "biggest_move_pct": None,
        "sufficient": False,
    }

    valid_years = [
        (year, price)
        for year, price in yearly_medians
        if price is not None and price > 0
    ]

    # at least two years are required to describe a price trend
    if count < 2 or len(valid_years) < MIN_YEARS:
        return result

    first_price = valid_years[0][1]
    last_price = valid_years[-1][1]

    pct_change = (last_price - first_price) / first_price * 100

    # find the largest percentage movement between successive available yearly medians, retaining its direction (+/-)
    movements = []

    for previous, current in zip(valid_years, valid_years[1:]):
        previous_price = previous[1]
        current_year, current_price = current

        change = (
            (current_price - previous_price)
            / previous_price
            * 100
        )

        movements.append((current_year, change))

    biggest_year, biggest_pct = max(
        movements,
        key=lambda item: abs(item[1]),
    )

    result.update({
        "median": median(price for _, price in valid_years),
        "pct_change": round(pct_change, 1),
        "biggest_move_year": biggest_year,
        "biggest_move_pct": round(biggest_pct, 1),
        "sufficient": True,
    })

    return result
