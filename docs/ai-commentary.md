# AI commentary: provider, data sent and cost

Recorded for IPPE-24. Lecture 02 requires the cost of AI tools used by the application to be stated.

## Provider

| | |
| --- | --- |
| Provider | Groq (GroqCloud), Free plan, no payment card on the account |
| Endpoint | `https://api.groq.com/openai/v1/chat/completions` (OpenAI-compatible) |
| Model | `llama-3.1-8b-instant` (override with the `COMMENTARY_MODEL` environment variable) |
| Code | `app/commentary.py`, function `generate_commentary(summary)` |
| API key | `GROQ_API_KEY` environment variable. Set in the WSGI file on PythonAnywhere and never committed. The full git history was checked for keys on 26 November 2026 and none were found |
| Reachable from PythonAnywhere | Yes. `api.groq.com` is on PythonAnywhere's free-account allowlist, and a test call was made from the server on [DATE] |

## What is sent

Only the summary dictionary for the current selection: the county, the year range, the number of sales, the mean and median price, and the number of excluded non-market sales. Raw sales rows, addresses and Eircodes are never sent.

The system prompt tells the model to use only the figures it is given and not to add other numbers, causes, comparisons or predictions.

## Failure behaviour

The request has a 10 second timeout. If there is no API key, the request times out, the API returns an error, or the reply is empty, `generate_commentary` returns `None` and the page shows its "commentary unavailable" notice instead. A failure never causes a 500 error. Successful answers are cached in memory, so the same selection does not call the API twice, and failures are not cached.

## Cost

**Actual cost to the project: €0.** The Groq Free plan does not charge, and usage is limited by rate limits instead.

For comparison, the paid on-demand price for `llama-3.1-8b-instant` is $0.05 per million input tokens and $0.08 per million output tokens. One commentary request is roughly 150 input tokens and up to about 100 output tokens, so about $0.000016 per request, or about 1.6 cents per thousand requests.

Free plan limits for this model, as published by Groq in 2026: 30 requests per minute, 14,400 requests per day, 6,000 tokens per minute and 500,000 tokens per day. The current figures for our account are on the Limits page of the Groq console. At about 250 tokens per request, the tokens-per-minute limit allows roughly 24 uncached requests a minute, which is well above the project's expected traffic.
