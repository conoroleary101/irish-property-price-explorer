from flask import Blueprint, render_template, request

from .queries import get_counties, get_property_types, get_sales_page

bp = Blueprint("main", __name__)

# The register covers 1 January 2010 onwards. Anything outside a sane window
# is treated as a typo and ignored rather than returning a server error.
MIN_YEAR = 2010
MAX_YEAR = 2100


def _int_arg(name, minimum=None, maximum=None):
    """Read one query parameter as an int, or None if it is missing or unusable.

    Returning None means "no filter", which is how an invalid or out-of-range
    value falls back to a sensible default instead of raising.
    """
    raw = request.args.get(name, "").strip()
    if not raw:
        return None
    try:
        value = int(raw)
    except ValueError:
        return None
    if minimum is not None and value < minimum:
        return None
    if maximum is not None and value > maximum:
        return None
    return value


def _str_arg(name):
    """Read one query parameter as a trimmed string, or None if it is blank."""
    value = request.args.get(name, "").strip()
    return value or None


def read_filters():
    """Build the cleaned filter dict from the query string."""
    year_from = _int_arg("year_from", MIN_YEAR, MAX_YEAR)
    year_to = _int_arg("year_to", MIN_YEAR, MAX_YEAR)
    price_min = _int_arg("price_min", 0)
    price_max = _int_arg("price_max", 0)

    # A reversed range is a typo, not a request for zero results, so swap it.
    if year_from and year_to and year_from > year_to:
        year_from, year_to = year_to, year_from
    if price_min is not None and price_max is not None and price_min > price_max:
        price_min, price_max = price_max, price_min

    filters = {
        "county": _str_arg("county"),
        "year_from": year_from,
        "year_to": year_to,
        "price_min": price_min,
        "price_max": price_max,
        "property_type": _str_arg("property_type"),
    }

    # Drop the empties so the dict can be splatted straight into url_for()
    # when building pagination links.
    return {k: v for k, v in filters.items() if v is not None}


@bp.route("/")
def index():
    page = _int_arg("page", 1) or 1
    filters = read_filters()

    sales, page, total_pages, total, excluded = get_sales_page(page, filters)

    return render_template(
        "index.html",
        sales=sales,
        page=page,
        total_pages=total_pages,
        total=total,
        excluded=excluded,
        filters=filters,
        counties=get_counties(),
        property_types=get_property_types(),
    )


@bp.route("/health")
def health():
    return {"status": "ok"}
