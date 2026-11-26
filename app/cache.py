"""
Persistent SQLite cache for AI-generated commentary.

IPPE-25: Stores commentary using a stable fingerprint of the summary data, preventing repeated API requests.
"""

import hashlib
import json

from .db import get_db


CREATE_CACHE_TABLE = """
CREATE TABLE IF NOT EXISTS commentary_cache (
    cache_key TEXT PRIMARY KEY,
    response_text TEXT NOT NULL,
    generated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
)
"""


def fingerprint(summary):
    """Generate a deterministic SHA-256 hash of summary data."""
    canonical = json.dumps(
        summary,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    )

    return hashlib.sha256(
        canonical.encode("utf-8")
    ).hexdigest()


def _ensure_table(db):
    """Create the cache table if it does not already exist."""
    db.execute(CREATE_CACHE_TABLE)


def get_cached(key):
    """Return stored commentary for a key, or None if missing."""
    db = get_db()
    _ensure_table(db)

    row = db.execute(
        """
        SELECT response_text
        FROM commentary_cache
        WHERE cache_key = ?
        """,
        (key,),
    ).fetchone()

    return row["response_text"] if row else None


def put_cached(key, text):
    """Store commentary, updating an existing matching entry."""
    db = get_db()

    with db:
        _ensure_table(db)

        db.execute(
            """
            INSERT INTO commentary_cache
                (cache_key, response_text)
            VALUES (?, ?)
            ON CONFLICT(cache_key) DO UPDATE SET
                response_text = excluded.response_text,
                generated_at = CURRENT_TIMESTAMP
            """,
            (key, text),
        )


def clear_cache():
    """Delete all cached commentary without deleting sales data."""
    db = get_db()

    with db:
        _ensure_table(db)
        cursor = db.execute(
            "DELETE FROM commentary_cache"
        )

    return cursor.rowcount
