"""Integration tests for IPPE-25 persistent commentary caching."""

import pytest

from app import create_app
from app.cache import fingerprint, get_cached
from app.commentary import (
    clear_commentary_cache,
    generate_commentary,
)


SUMMARY = {
    "county": "Cork",
    "period": (2020, 2024),
    "count": 100,
    "median": 250000,
}


@pytest.fixture
def flask_app(tmp_path):
    app = create_app("testing")
    app.config["DATABASE"] = str(tmp_path / "commentary.db")
    return app


def test_identical_request_uses_sqlite_without_api(flask_app, monkeypatch):
    clear_commentary_cache()
    monkeypatch.setenv("GROQ_API_KEY", "fake-test-key")

    calls = []

    class MockResponse:
        def raise_for_status(self):
            pass

        def json(self):
            return {
                "choices": [
                    {"message": {"content": "Stored test commentary."}}
                ]
            }

    def mocked_post(*args, **kwargs):
        calls.append(1)
        return MockResponse()

    monkeypatch.setattr(
        "app.commentary.requests.post",
        mocked_post,
    )

    # first request: generate commentary and persist it
    with flask_app.app_context():
        first = generate_commentary(SUMMARY)
        assert get_cached(fingerprint(SUMMARY)) == first

    # simulate a fresh process without the in-memory response
    clear_commentary_cache()

    # second request: must use SQLite rather than the API
    with flask_app.app_context():
        second = generate_commentary(dict(SUMMARY))

    assert first == second == "Stored test commentary."
    assert len(calls) == 1


def test_cached_response_works_without_api_key(flask_app, monkeypatch):
    clear_commentary_cache()
    monkeypatch.setenv("GROQ_API_KEY", "fake-test-key")

    class MockResponse:
        def raise_for_status(self):
            pass

        def json(self):
            return {
                "choices": [
                    {"message": {"content": "Previously cached."}}
                ]
            }

    monkeypatch.setattr(
        "app.commentary.requests.post",
        lambda *args, **kwargs: MockResponse(),
    )

    with flask_app.app_context():
        assert generate_commentary(SUMMARY) == "Previously cached."

    clear_commentary_cache()
    monkeypatch.delenv("GROQ_API_KEY", raising=False)
    monkeypatch.delenv("COMMENTARY_API_KEY", raising=False)

    def unexpected_api_call(*args, **kwargs):
        raise AssertionError("API should not be called")

    monkeypatch.setattr(
        "app.commentary.requests.post",
        unexpected_api_call,
    )

    with flask_app.app_context():
        assert generate_commentary(SUMMARY) == "Previously cached."
