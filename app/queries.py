from .db import get_db

PAGE_SIZE = 50


def get_sales_page(page):
    """Return one page of sales, the page actually used, and the page count."""
    db = get_db()

    total = db.execute("SELECT COUNT(*) AS n FROM sales").fetchone()["n"]
    total_pages = max(1, (total + PAGE_SIZE - 1) // PAGE_SIZE)

    page = max(1, min(page, total_pages))

    offset = (page - 1) * PAGE_SIZE
    sales = db.execute(
        """
        SELECT date_of_sale, address, county, price, description_of_property
        FROM sales
        ORDER BY date_of_sale DESC, id DESC
        LIMIT ? OFFSET ?
        """,
        (PAGE_SIZE, offset),
    ).fetchall()

    return sales, page, total_pages