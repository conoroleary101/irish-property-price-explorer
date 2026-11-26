"""Plain-English commentary on the figures for the current selection.

The model only ever sees the summary dictionary (counts, mean, median and the
filters that produced them), never raw sales rows. The provider is Groq's
free tier, called through its OpenAI-compatible chat completions endpoint.
"""

import json
import os
from threading import Lock

import requests

GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
DEFAULT_MODEL = "openai/gpt-oss-20b"
# gpt-oss models reason before answering, and the reasoning counts towards
# max_tokens. At default effort the reasoning used the whole budget and the
# answer came back empty (tested on PythonAnywhere, 26 November 2026), so
# these models are asked for low effort and given a larger token budget.
REASONING_MODEL_PREFIX = "openai/gpt-oss"
MAX_TOKENS = 400
DEFAULT_TIMEOUT = 10  # seconds

# Shown by callers that want text rather than None when there is no commentary.
FALLBACK_COMMENTARY = (
    "Commentary is temporarily unavailable. Use the sales and summary figures "
    "below to interpret the results."
)
FALLBACK_TEXT = FALLBACK_COMMENTARY

SYSTEM_PROMPT = (
    "You explain Irish residential property price figures to people with no "
    "technical or financial background. Write one short paragraph of plain "
    "English, no more than 60 words. Use only the figures you are given. Do not "
    "add any other numbers, dates, causes, comparisons or predictions, and do "
    "not speculate about why prices are what they are."
)

# Successful answers only. Failures are never cached, so a brief outage does
# not leave a selection without commentary until the app restarts.
_commentary_cache = {}
_cache_lock = Lock()


def build_commentary_prompt(summary):
    """Build the user prompt from the summary dictionary alone."""
    county = summary.get("county") or "all counties"
    year_from = summary.get("year_from")
    year_to = summary.get("year_to")
    period = (
        f"from {year_from} to {year_to}"
        if year_from is not None and year_to is not None
        else "for the available period"
    )
    sales = summary.get("count", summary.get("sale_count", 0))
    mean = summary.get("mean", summary.get("mean_price", 0)) or 0
    median = summary.get("median", summary.get("median_price", 0)) or 0
    excluded = summary.get("excluded", summary.get("excluded_count", 0))
    return (
        "Describe these figures in plain English.\n"
        f"Scope: {county}; {period}.\n"
        f"Sales: {sales}.\n"
        f"Mean price: €{mean:,.2f}.\n"
        f"Median price: €{median:,.2f}.\n"
        f"Excluded non-market sales: {excluded}."
    )


def build_prompt(summary):
    """Short alias for build_commentary_prompt."""
    return build_commentary_prompt(summary)


def clear_commentary_cache():
    with _cache_lock:
        _commentary_cache.clear()


def _cache_key(summary):
    return json.dumps(summary, sort_keys=True, default=str)


def _api_key():
    return os.environ.get("GROQ_API_KEY") or os.environ.get("COMMENTARY_API_KEY")


def _extract_text(payload):
    choices = payload.get("choices") or []
    if choices:
        content = (choices[0].get("message") or {}).get("content")
        if isinstance(content, str) and content.strip():
            return content.strip()
    return None


def generate_commentary(summary, api_key=None, timeout=DEFAULT_TIMEOUT):
    """Return a short paragraph about the summary, or None if none is available.

    None is returned, never raised, when there is no API key, the request times
    out, the API returns an error, or the reply has no text. The caller decides
    what to show instead.
    """
    key = _cache_key(summary)
    with _cache_lock:
        if key in _commentary_cache:
            return _commentary_cache[key]

    api_key = api_key or _api_key()
    if not api_key:
        return None

    model = os.environ.get("COMMENTARY_MODEL", DEFAULT_MODEL)
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": build_commentary_prompt(summary)},
        ],
        "temperature": 0.2,
        "max_tokens": MAX_TOKENS,
    }
    if model.startswith(REASONING_MODEL_PREFIX):
        payload["reasoning_effort"] = "low"

    try:
        response = requests.post(
            os.environ.get("COMMENTARY_API_URL", GROQ_API_URL),
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json=payload,
            timeout=timeout,
        )
        response.raise_for_status()
        text = _extract_text(response.json())
    except Exception:
        return None

    if text:
        with _cache_lock:
            _commentary_cache[key] = text
    return text


get_commentary = generate_commentary
