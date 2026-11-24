import requests

from app.commentary import (
    FALLBACK_COMMENTARY,
    build_commentary_prompt,
    clear_commentary_cache,
    generate_commentary,
)


SUMMARY = {
    "count": 120,
    "mean": 325000,
    "median": 310000,
    "excluded": 4,
    "county": "Cork",
    "year_from": 2023,
    "year_to": 2024,
}


def test_prompt_is_built_from_known_summary():
    prompt = build_commentary_prompt(SUMMARY)

    assert "Cork" in prompt
    assert "from 2023 to 2024" in prompt
    assert "Sales: 120" in prompt
    assert "Mean price: €325,000.00" in prompt
    assert "Median price: €310,000.00" in prompt
    assert "Excluded non-market sales: 4" in prompt


def test_timeout_returns_fallback(monkeypatch):
    clear_commentary_cache()
    monkeypatch.setenv("COMMENTARY_API_KEY", "test-key")

    def timeout(*args, **kwargs):
        raise requests.Timeout("too slow")

    monkeypatch.setattr("app.commentary.requests.post", timeout)

    assert generate_commentary(SUMMARY) == FALLBACK_COMMENTARY


def test_api_error_returns_fallback(monkeypatch):
    clear_commentary_cache()
    monkeypatch.setenv("COMMENTARY_API_KEY", "test-key")

    class ErrorResponse:
        def raise_for_status(self):
            raise requests.HTTPError("bad gateway")

    monkeypatch.setattr("app.commentary.requests.post", lambda *a, **k: ErrorResponse())

    assert generate_commentary(SUMMARY) == FALLBACK_COMMENTARY


def test_identical_request_is_served_from_cache(monkeypatch):
    clear_commentary_cache()
    monkeypatch.setenv("COMMENTARY_API_KEY", "test-key")
    calls = []

    class Response:
        def raise_for_status(self):
            return None

        def json(self):
            return {"choices": [{"message": {"content": "Mocked market commentary."}}]}

    def post(*args, **kwargs):
        calls.append((args, kwargs))
        return Response()

    monkeypatch.setattr("app.commentary.requests.post", post)

    first = generate_commentary(SUMMARY)
    second = generate_commentary(dict(SUMMARY))

    assert first == second == "Mocked market commentary."
    assert len(calls) == 1


def test_no_api_key_never_makes_request(monkeypatch):
    clear_commentary_cache()
    monkeypatch.delenv("COMMENTARY_API_KEY", raising=False)
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)

    def unexpected_call(*args, **kwargs):
        raise AssertionError("No real request should be made")

    monkeypatch.setattr("app.commentary.requests.post", unexpected_call)

    assert generate_commentary(SUMMARY) == FALLBACK_COMMENTARY
