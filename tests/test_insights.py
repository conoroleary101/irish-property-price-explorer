"""
Unit tests for IPPE-23 summarisation
"""

from app.insights import summarise


EXPECTED_KEYS = {
    "county",
    "period",
    "count",
    "median",
    "pct_change",
    "biggest_move_year",
    "biggest_move_pct",
    "sufficient",
}


def test_summary_with_known_values():
    yearly = [
        (2021, 100000),
        (2022, 110000),
        (2023, 99000),
        (2024, 118800),
    ]

    result = summarise("Cork", 2021, 2024, yearly, 80)

    assert result == {
        "county": "Cork",
        "period": (2021, 2024),
        "count": 80,
        "median": 105000,
        "pct_change": 18.8,
        "biggest_move_year": 2024,
        "biggest_move_pct": 20.0,
        "sufficient": True,
    }


def test_largest_negative_movement():
    yearly = [
        (2020, 200000),
        (2021, 140000),
        (2022, 154000),
    ]

    result = summarise("Dublin", 2020, 2022, yearly, 30)

    assert result["median"] == 154000
    assert result["pct_change"] == -23.0
    assert result["biggest_move_year"] == 2021
    assert result["biggest_move_pct"] == -30.0


def test_insufficient_single_year():
    result = summarise(
        "Cork", 2023, 2024, [(2023, 250000)], 50
    )

    assert set(result) == EXPECTED_KEYS
    assert result["sufficient"] is False
    assert result["median"] is None
    assert result["pct_change"] is None
    assert result["biggest_move_year"] is None
    assert result["biggest_move_pct"] is None


def test_empty_selection():
    result = summarise("Mayo", 2020, 2024, [], 0)

    assert set(result) == EXPECTED_KEYS
    assert result["count"] == 0
    assert result["sufficient"] is False
    assert result["median"] is None


def test_missing_county():
    yearly = [(2022, 200000), (2023, 220000)]

    result = summarise(None, 2022, 2023, yearly, 20)

    assert result["county"] == "All counties"
    assert result["pct_change"] == 10.0
    assert result["sufficient"] is True


def test_input_is_not_modified():
    yearly = [(2022, 200000), (2023, 220000)]
    original = list(yearly)

    summarise("Cork", 2022, 2023, yearly, 20)

    assert yearly == original


def test_no_sales_despite_yearly_values():
    result = summarise(
        "Cork",
        2022,
        2023,
        [(2022, 200000), (2023, 220000)],
        0,
    )

    assert result["sufficient"] is False
    assert result["median"] is None
