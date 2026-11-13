from .db import get_db

PAGE_SIZE = 50


def build_where(filters):
    """Turn a dict of cleaned filters into a SQL WHERE fragment and its parameters.

    Only filters that were actually supplied add a clause, so any mix of the
    six parameters combines correctly. Values are returned separately as
    placeholders rather than pasted into the SQL string, which is what keeps
    this safe from SQL injection.
    """
    clauses = []
    params = []

    if filters.get("county"):
        clauses.append("county = ?")
        params.append(filters["county"])

    # Compare the column directly against a full date string so SQLite can
    # still use idx_sales_date. Wrapping the column in substr() would make
    # the index unusable and force a scan of every row.
    if filters.get("year_from"):
        clauses.append("date_of_sale >= ?")
        params.append(f"{filters['year_from']}-01-01")

    if filters.get("year_to"):
        clauses.append("date_of_sale <= ?")
        params.append(f"{filters['year_to']}-12-31")

    if filters.get("price_min") is not None:
        clauses.append("price >= ?")
        params.append(filters["price_min"])

    if filters.get("price_max") is not None:
        clauses.append("price <= ?")
        params.append(filters["price_max"])

    if filters.get("property_type"):
        clauses.append("description_of_property = ?")
        params.append(filters["property_type"])

    where = " AND ".join(clauses) if clauses else "1 = 1"
    return where, params


def get_sales_page(page, filters=None):
    """Return one page of sales plus the counts the page needs.

    Rows flagged "Not Full Market Price" are left out of the listing because
    they are not open-market transactions, but the number left out is returned
    so the exclusion is visible to the user rather than silent.
    """
    filters = filters or {}
    db = get_db()
    where, params = build_where(filters)

    # One pass over the filtered rows gives both counts.
    counts = db.execute(
        f"""
        SELECT
            SUM(CASE WHEN not_full_market_price = 0 THEN 1 ELSE 0 END) AS included,
            SUM(CASE WHEN not_full_market_price = 1 THEN 1 ELSE 0 END) AS excluded
        FROM sales
        WHERE {where}
        """,
        params,
    ).fetchone()

    total = counts["included"] or 0
    excluded = counts["excluded"] or 0

    total_pages = max(1, (total + PAGE_SIZE - 1) // PAGE_SIZE)
    page = max(1, min(page, total_pages))
    offset = (page - 1) * PAGE_SIZE

    sales = db.execute(
        f"""
        SELECT date_of_sale, address, county, price, description_of_property
        FROM sales
        WHERE {where} AND not_full_market_price = 0
        ORDER BY date_of_sale DESC, id DESC
        LIMIT ? OFFSET ?
        """,
        params + [PAGE_SIZE, offset],
    ).fetchall()

    return sales, page, total_pages, total, excluded


def get_counties():
    """Distinct counties actually present in the data, for the filter dropdown."""
    rows = get_db().execute(
        "SELECT DISTINCT county FROM sales ORDER BY county"
    ).fetchall()
    return [r["county"] for r in rows]


def get_property_types():
    """Distinct property descriptions actually present in the data."""
    rows = get_db().execute(
        """
        SELECT DISTINCT description_of_property
        FROM sales
        WHERE description_of_property IS NOT NULL
          AND description_of_property <> ''
        ORDER BY description_of_property
        """
    ).fetchall()
    return [r["description_of_property"] for r in rows]
