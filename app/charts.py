import io
import statistics
from collections import defaultdict

from matplotlib.figure import Figure
from matplotlib.ticker import FuncFormatter, MaxNLocator

from .db import get_db
from .queries import build_where

MIN_YEARS = 2


def median_price_by_year(filters):
    """Median open-market price per year for a filtered selection.

    Returns a dict like {2010: 180000, 2011: 165000, ...}, sorted by year.
    Uses the same filters and the same "Not Full Market Price" exclusion
    as the sales listing, so the chart always matches the table.
    """
    where, params = build_where(filters)
    rows = get_db().execute(
        f"""
        SELECT substr(date_of_sale, 1, 4) AS year, price
        FROM sales
        WHERE {where} AND not_full_market_price = 0
        """,
        params,
    )

    prices_by_year = defaultdict(list)
    for row in rows:
        prices_by_year[int(row["year"])].append(row["price"])

    return {
        year: statistics.median(prices)
        for year, prices in sorted(prices_by_year.items())
    }


def _euro(value, _position):
    return f"€{value:,.0f}"


def render_trend_chart(series, title):
    """Draw one line per series and return the chart as PNG bytes.

    `series` maps a label (such as a county name) to a {year: median} dict.
    If no series has enough years, a message is drawn instead of a chart,
    so the user never sees an empty or misleading graph.
    """

    fig = Figure(figsize=(8, 4.5), dpi=100)
    ax = fig.subplots()

    plotted = 0
    for label, by_year in series.items():
        if len(by_year) >= MIN_YEARS:
            ax.plot(list(by_year), list(by_year.values()), marker="o", label=label)
            plotted += 1

    if plotted:
        ax.set_title(title)
        ax.set_xlabel("Year of sale")
        ax.set_ylabel("Median price")
        ax.yaxis.set_major_formatter(FuncFormatter(_euro))
        ax.xaxis.set_major_locator(MaxNLocator(integer=True))
        ax.grid(True, alpha=0.3)
        if len(series) > 1:
            ax.legend()
    else:
        ax.axis("off")
        ax.text(
            0.5, 0.5,
            "Not enough sales in this selection to show a trend.\n"
            "Try widening the filters.",
            ha="center", va="center", fontsize=12,
        )

    fig.tight_layout()
    buffer = io.BytesIO()
    fig.savefig(buffer, format="png")
    return buffer.getvalue()