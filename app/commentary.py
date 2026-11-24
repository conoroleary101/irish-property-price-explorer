"""Generate short, filtered property-price commentary.

The API is isolated behind this module so tests and the route never need a real
credential or network connection.
"""

import json
import os
from threading import Lock

import requests


FALLBACK_COMMENTARY = (
    "Commentary is temporarily unavailable. Use the sales and summary figures "
    "below to interpret the results."
)
FALLBACK_TEXT = FALLBACK_COMMENTARY

_DEFAULT_API_URL = "https://api.openai.com/v1/chat/completions"
_DEFAULT_MODEL = "gpt-4o-mini"
_commentary_cache = {}
_cache_lock = Lock()


def build_commentary_prompt(summary):
    """Build a deterministic prompt from a known summary dictionary."""
    county = summary.get("county") or "all counties"
    year_from = summary.get("year_from")
    year_to = summary.get("year_to")
    period = (
        f"from {year_from} to {year_to}"
        if year_from is not None and year_to is not None
        else "for the available period"
    )
    sales = summary.get("count", summary.get("sale_count", 0))
    mean = summary.get("mean", summary.get("mean_price", 0))
    median = summary.get("median", summary.get("median_price", 0))
    excluded = summary.get("excluded", summary.get("excluded_count", 0))
    return (
        "Write a concise, factual commentary of no more than 60 words for an "
        "Irish residential property price report. Do not invent or speculate.\n"
        f"Scope: {county}; {period}.\n"
        f"Sales: {sales}.\n"
        f"Mean price: €{mean:,.2f}.\n"
        f"Median price: €{median:,.2f}.\n"
        f"Excluded non-market sales: {excluded}."
    )


def build_prompt(summary):
    """Backward-friendly short name for the prompt builder."""
    return build_commentary_prompt(summary)


def clear_commentary_cache():
    with _cache_lock:
        _commentary_cache.clear()


def _cache_key(summary):
    return json.dumps(summary, sort_keys=True, default=str)


def _extract_text(payload):
    choices = payload.get("choices") or []
    if choices:
        message = choices[0].get("message") or {}
        content = message.get("content")
        if isinstance(content, str) and content.strip():
            return content.strip()
        text = choices[0].get("text")
        if isinstance(text, str) and text.strip():
            return text.strip()
    output_text = payload.get("output_text")
    if isinstance(output_text, str) and output_text.strip():
        return output_text.strip()
    return None


def generate_commentary(summary, api_key=None, timeout=10):
    """Return commentary, caching identical summaries and swallowing API failures."""
    key = _cache_key(summary)
    with _cache_lock:
        if key in _commentary_cache:
            return _commentary_cache[key]

    key_name = api_key or os.environ.get("COMMENTARY_API_KEY") or os.environ.get("OPENAI_API_KEY")
    if not key_name:
        result = FALLBACK_COMMENTARY
    else:
        prompt = build_commentary_prompt(summary)
        try:
            response = requests.post(
                os.environ.get("COMMENTARY_API_URL", _DEFAULT_API_URL),
                headers={
                    "Authorization": f"Bearer {key_name}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": os.environ.get("COMMENTARY_MODEL", _DEFAULT_MODEL),
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.2,
                },
                timeout=timeout,
            )
            response.raise_for_status()
            result = _extract_text(response.json()) or FALLBACK_COMMENTARY
        except Exception:
            result = FALLBACK_COMMENTARY

    with _cache_lock:
        _commentary_cache[key] = result
    return result


get_commentary = generate_commentary
