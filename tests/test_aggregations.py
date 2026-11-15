import sqlite3

import pytest

from app import queries


@pytest.fixture
def sample_db(monkeypatch):
    db = sqlite3.connect(":memory:")
    db.row_factory = sqlite3.Row

    db.execute("""
        CREATE TABLE sales (
            county TEXT,
            date_of_sale TEXT,
            price INTEGER,
            not_full_market_price INTEGER,
            description_of_property TEXT
        )
    """)

    db.executemany(
        "INSERT INTO sales VALUES (?, ?, ?, ?, ?)",
        [
            ("Cork", "2024-01-01", 100000, 0, "New"),
            ("Cork", "2024-02-01", 200000, 0, "New"),
            ("Cork", "2023-01-01", 300000, 0, "Second"),
            ("Cork", "2024-03-01", 5000, 1, "New"),
            ("Dublin", "2024-01-01", 800000, 0, "New"),
            ("Dublin", "2015-01-01", 250000, 1, "Second"),
        ],
    )

    monkeypatch.setattr(queries, "get_db", lambda: db)

    yield db
    db.close()


def test_all_sales(sample_db):
    assert queries.get_aggregate_stats() == {
        "count": 4,
        "mean": 350000,
        "median": 250000,
        "excluded": 2,
    }


def test_odd_median(sample_db):
    result = queries.get_aggregate_stats({"county": "Cork"})

    assert result["count"] == 3
    assert result["mean"] == 200000
    assert result["median"] == 200000
    assert result["excluded"] == 1


def test_even_median_with_filters(sample_db):
    result = queries.get_aggregate_stats({
        "county": "Cork",
        "year_from": 2024,
        "year_to": 2024,
        "property_type": "New",
    })

    assert result["count"] == 2
    assert result["mean"] == 150000
    assert result["median"] == 150000
    assert result["excluded"] == 1


def test_combined_filters(sample_db):
    result = queries.get_aggregate_stats({
        "county": "Cork",
        "year_from": 2024,
        "year_to": 2024,
        "price_min": 150000,
        "property_type": "New",
    })

    assert result["count"] == 1
    assert result["mean"] == 200000
    assert result["median"] == 200000
    assert result["excluded"] == 0


def test_only_excluded_sales_match(sample_db):
    result = queries.get_aggregate_stats({
        "county": "Cork",
        "price_max": 10000,
    })

    assert result == {
        "count": 0,
        "mean": 0,
        "median": 0,
        "excluded": 1,
    }


def test_no_matching_rows(sample_db):
    result = queries.get_aggregate_stats({
        "county": "Mayo",
    })

    assert result == {
        "count": 0,
        "mean": 0,
        "median": 0,
        "excluded": 0,
    }
