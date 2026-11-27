"""Unit tests for IPPE-25 persistent commentary caching."""

import sqlite3
import pytest
from contextlib import closing

from app import create_app
from app.cache import (
    clear_cache,
    fingerprint,
    get_cached,
    put_cached,
)


@pytest.fixture
def flask_app(tmp_path):
    app = create_app("testing")
    app.config["DATABASE"] = str(tmp_path / "cache_test.db")
    return app


SUMMARY = {
    "county": "Cork",
    "period": (2020, 2024),
    "count": 100,
    "median": 250000,
}


def test_fingerprint_is_deterministic():
    reversed_summary = dict(reversed(list(SUMMARY.items())))

    assert fingerprint(SUMMARY) == fingerprint(reversed_summary)


def test_different_summaries_get_different_keys():
    changed = dict(SUMMARY)
    changed["median"] = 300000

    assert fingerprint(SUMMARY) != fingerprint(changed)


def test_missing_entry_returns_none(flask_app):
    with flask_app.app_context():
        assert get_cached("missing-key") is None


def test_store_and_retrieve_commentary(flask_app):
    key = fingerprint(SUMMARY)

    with flask_app.app_context():
        put_cached(key, "Property prices increased.")
        assert get_cached(key) == "Property prices increased."


def test_cache_persists_across_connections(flask_app):
    key = fingerprint(SUMMARY)

    with flask_app.app_context():
        put_cached(key, "Persistent commentary.")

    # A new Flask context opens a separate SQLite connection
    with flask_app.app_context():
        assert get_cached(key) == "Persistent commentary."


def test_timestamp_is_recorded(flask_app):
    key = fingerprint(SUMMARY)

    with flask_app.app_context():
        put_cached(key, "Timestamp test.")

    with closing(sqlite3.connect(flask_app.config["DATABASE"])) as db:
        row = db.execute(
            """
            SELECT generated_at
            FROM commentary_cache
            WHERE cache_key = ?
            """,
            (key,),
        ).fetchone()

    assert row is not None
    assert row[0] is not None


def test_clear_cache(flask_app):
    key = fingerprint(SUMMARY)

    with flask_app.app_context():
        put_cached(key, "Temporary commentary.")

        assert clear_cache() == 1
        assert get_cached(key) is None


def test_repeated_key_does_not_duplicate_rows(flask_app):
    key = fingerprint(SUMMARY)

    with flask_app.app_context():
        put_cached(key, "First response.")
        put_cached(key, "Updated response.")

        assert get_cached(key) == "Updated response."

    with closing(sqlite3.connect(flask_app.config["DATABASE"])) as db:
        count = db.execute(
            "SELECT COUNT(*) FROM commentary_cache"
        ).fetchone()[0]

    assert count == 1
