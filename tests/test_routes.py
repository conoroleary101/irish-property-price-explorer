import sqlite3
from pathlib import Path

import pytest

from app import create_app

SCHEMA = Path(__file__).resolve().parents[1] / "scripts" / "schema.sql"

ROWS = [
    ("2024-01-01", "1 Test St", "Cork", 100000, 0, "Second-Hand Dwelling house /Apartment"),
    ("2024-02-01", "2 Test St", "Cork", 200000, 0, "Second-Hand Dwelling house /Apartment"),
    ("2024-03-01", "3 Test St", "Cork", 300000, 0, "Second-Hand Dwelling house /Apartment"),
    ("2024-04-01", "4 Test St", "Cork", 250000, 1, "Second-Hand Dwelling house /Apartment"),
    ("2024-05-01", "5 Test St", "Dublin", 400000, 0, "Apartment"),
]


@pytest.fixture
def app(tmp_path):
    app = create_app("testing")
    db_path = tmp_path / "routes.db"
    app.config["DATABASE"] = str(db_path)

    conn = sqlite3.connect(db_path)
    conn.executescript(SCHEMA.read_text())
    conn.executemany(
        "INSERT INTO sales (date_of_sale, address, county, price, not_full_market_price, description_of_property) "
        "VALUES (?, ?, ?, ?, ?, ?)",
        ROWS,
    )
    conn.commit()
    conn.close()
    return app


def test_index_route_valid_filters_return_200(app):
    client = app.test_client()
    response = client.get(
        "/?county=Cork&year_from=2024&year_to=2024"
        "&price_min=150000&property_type=Second-Hand%20Dwelling%20house%20%2FApartment"
    )

    assert response.status_code == 200
    assert b"Property Sales" in response.data


@pytest.mark.parametrize(
    "query_string",
    [
        "?county=bogus",
        "?year_from=9999",
        "?year_from=2024&year_to=2023",
        "?price_min=abc",
        "?page=-5",
        "?property_type=Nope",
    ],
)
def test_index_route_invalid_params_do_not_return_500(app, query_string):
    response = app.test_client().get(f"/{query_string}")

    assert response.status_code == 200
    assert response.status_code != 500


def test_index_route_empty_result_set_is_handled(app):
    response = app.test_client().get("/?county=Mayo")

    assert response.status_code == 200
    assert "No sales found matching your criteria." in response.get_data(as_text=True)


@pytest.mark.parametrize(
    "query_string",
    [
        "?county_a=Cork&county_b=Dublin",
        "?county_a=Nope&county_b=Dublin",
        "?county_a=Cork&county_b=Cork",
        "?county_a=&county_b=Dublin",
    ],
)
def test_compare_route_valid_and_invalid_inputs_do_not_500(app, query_string):
    response = app.test_client().get(f"/compare{query_string}")

    assert response.status_code == 200
    assert response.status_code != 500
