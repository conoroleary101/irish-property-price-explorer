import sqlite3
from pathlib import Path

import pytest

from app import create_app
from app.charts import median_price_by_year, render_trend_chart

PNG_SIGNATURE = b"\x89PNG"
SCHEMA = Path(__file__).resolve().parents[1] / "scripts" / "schema.sql"

ROWS = [
   
    ("2020-03-01", "Cork", 200000, 0),
    ("2020-06-01", "Cork", 300000, 0),
    ("2020-07-01", "Cork", 999999, 1),  # non-market: must be ignored
    ("2021-03-01", "Cork", 400000, 0),
    ("2020-05-01", "Galway", 150000, 0),
    ("2021-05-01", "Galway", 250000, 0),
    ("2021-05-01", "Leitrim", 90000, 0),  # only one year
]


@pytest.fixture
def app(tmp_path):
    app = create_app("testing")
    db_path = tmp_path / "charts.db"
    app.config["DATABASE"] = str(db_path)

    conn = sqlite3.connect(db_path)
    conn.executescript(SCHEMA.read_text())
    conn.executemany(
        "INSERT INTO sales (date_of_sale, address, county, price, not_full_market_price)"
        " VALUES (?, 'x', ?, ?, ?)",
        ROWS,
    )
    conn.commit()
    conn.close()
    return app


def test_median_per_year_excludes_non_market_sales(app):
    with app.app_context():
        assert median_price_by_year({"county": "Cork"}) == {2020: 250000, 2021: 400000}


def test_median_respects_year_filter(app):
    with app.app_context():
        assert median_price_by_year({"county": "Cork", "year_from": 2021}) == {2021: 400000}


def test_render_returns_png():
    png = render_trend_chart({"Cork": {2020: 250000, 2021: 400000}}, "Test")
    assert png.startswith(PNG_SIGNATURE)


def test_too_few_points_still_returns_png_message():
    png = render_trend_chart({"Leitrim": {2021: 90000}}, "Test")
    assert png.startswith(PNG_SIGNATURE)


def test_trend_route_returns_png(app):
    response = app.test_client().get("/chart/trend.png?county=Cork")
    assert response.status_code == 200
    assert response.mimetype == "image/png"
    assert response.data.startswith(PNG_SIGNATURE)


def test_compare_route_returns_png(app):
    response = app.test_client().get("/chart/compare.png?county_a=Cork&county_b=Galway")
    assert response.status_code == 200
    assert response.mimetype == "image/png"