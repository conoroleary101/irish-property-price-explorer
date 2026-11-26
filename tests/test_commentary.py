import requests

from app.commentary import (
    GROQ_API_URL,
    SYSTEM_PROMPT,
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


class OkResponse:
    def __init__(self, text="Mocked market commentary."):
        self.text = text

    def raise_for_status(self):
        return None

    def json(self):
        return {"choices": [{"message": {"content": self.text}}]}


def test_prompt_is_built_from_known_summary():
    prompt = build_commentary_prompt(SUMMARY)

    assert "Cork" in prompt
    assert "from 2023 to 2024" in prompt
    assert "Sales: 120" in prompt
    assert "Mean price: €325,000.00" in prompt
    assert "Median price: €310,000.00" in prompt
    assert "Excluded non-market sales: 4" in prompt


def test_system_prompt_forbids_invented_figures():
    assert "Use only the figures you are given" in SYSTEM_PROMPT
    assert "Do not add any other numbers" in SYSTEM_PROMPT


def test_only_the_summary_is_sent(monkeypatch):
    clear_commentary_cache()
    monkeypatch.setenv("GROQ_API_KEY", "test-key")
    sent = {}

    def post(url, **kwargs):
        sent["url"] = url
        sent["json"] = kwargs["json"]
        sent["timeout"] = kwargs["timeout"]
        return OkResponse()

    monkeypatch.setattr("app.commentary.requests.post", post)
    generate_commentary(SUMMARY)

    assert sent["url"] == GROQ_API_URL
    assert sent["timeout"] > 0
    messages = sent["json"]["messages"]
    assert [m["role"] for m in messages] == ["system", "user"]
    assert messages[1]["content"] == build_commentary_prompt(SUMMARY)


def test_timeout_returns_none(monkeypatch):
    clear_commentary_cache()
    monkeypatch.setenv("GROQ_API_KEY", "test-key")

    def timeout(*args, **kwargs):
        raise requests.Timeout("too slow")

    monkeypatch.setattr("app.commentary.requests.post", timeout)

    assert generate_commentary(SUMMARY) is None


def test_api_error_returns_none(monkeypatch):
    clear_commentary_cache()
    monkeypatch.setenv("GROQ_API_KEY", "test-key")

    class ErrorResponse:
        def raise_for_status(self):
            raise requests.HTTPError("bad gateway")

    monkeypatch.setattr("app.commentary.requests.post", lambda *a, **k: ErrorResponse())

    assert generate_commentary(SUMMARY) is None


def test_failure_is_not_cached(monkeypatch):
    clear_commentary_cache()
    monkeypatch.setenv("GROQ_API_KEY", "test-key")
    responses = [requests.ConnectionError("down"), OkResponse("Back again.")]

    def post(*args, **kwargs):
        result = responses.pop(0)
        if isinstance(result, Exception):
            raise result
        return result

    monkeypatch.setattr("app.commentary.requests.post", post)

    assert generate_commentary(SUMMARY) is None
    assert generate_commentary(SUMMARY) == "Back again."


def test_identical_request_is_served_from_cache(monkeypatch):
    clear_commentary_cache()
    monkeypatch.setenv("GROQ_API_KEY", "test-key")
    calls = []

    def post(*args, **kwargs):
        calls.append((args, kwargs))
        return OkResponse()

    monkeypatch.setattr("app.commentary.requests.post", post)

    first = generate_commentary(SUMMARY)
    second = generate_commentary(dict(SUMMARY))

    assert first == second == "Mocked market commentary."
    assert len(calls) == 1


def test_no_api_key_never_makes_request(monkeypatch):
    clear_commentary_cache()
    monkeypatch.delenv("GROQ_API_KEY", raising=False)
    monkeypatch.delenv("COMMENTARY_API_KEY", raising=False)

    def unexpected_call(*args, **kwargs):
        raise AssertionError("No real request should be made")

    monkeypatch.setattr("app.commentary.requests.post", unexpected_call)

    assert generate_commentary(SUMMARY) is None
