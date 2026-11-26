# AI commentary: provider, data sent and cost

Recorded for IPPE-24. Lecture 02 requires the cost of AI tools used by the application to be stated.

## Provider

| | |
| --- | --- |
| Provider | Groq (GroqCloud), Free plan, no payment card on the account |
| Endpoint | `https://api.groq.com/openai/v1/chat/completions` (OpenAI-compatible) |
| Model | `openai/gpt-oss-20b` with `reasoning_effort` set to `low` (override with the `COMMENTARY_MODEL` environment variable) |
| Code | `app/commentary.py`, function `generate_commentary(summary)` |
| API key | `GROQ_API_KEY` environment variable. Set in the WSGI file on PythonAnywhere and never committed. The full git history was checked for keys on 26 November 2026 and none were found |
| Reachable from PythonAnywhere | Yes. `api.groq.com` is on PythonAnywhere's free-account allowlist, and a test call was made from the server on 26 November 2026 |

## Why this model

The first choice, `llama-3.1-8b-instant`, was taken from third-party pricing pages. A test call from PythonAnywhere on 26 November 2026 returned `404 model_not_found`: Groq no longer offers it to this account. The live model list for the account was checked instead, and the candidates were tested from the server with a real summary:

| Model | Result |
| --- | --- |
| `openai/gpt-oss-20b`, default settings | Empty answer. The model's reasoning used the whole 150-token budget |
| `openai/gpt-oss-20b`, `reasoning_effort` low | Correct plain-English paragraph using only the supplied figures |
| `allam-2-7b` | Answered, but added details that were not in the data ("Cork city", "approximately") |

`openai/gpt-oss-20b` with low reasoning effort was chosen, and the token budget was raised to 400 so the reasoning cannot crowd out the answer.

## What is sent

Only the summary dictionary for the current selection: the county, the year range, the number of sales, the mean and median price, and the number of excluded non-market sales. Raw sales rows, addresses and Eircodes are never sent.

The system prompt tells the model to use only the figures it is given and not to add other numbers, causes, comparisons or predictions.

## Failure behaviour

The request has a 10 second timeout. If there is no API key, the request times out, the API returns an error, or the reply is empty, `generate_commentary` returns `None` and the page shows its "commentary unavailable" notice instead. A failure never causes a 500 error. Successful answers are cached in memory, so the same selection does not call the API twice, and failures are not cached.

## Cost

**Actual cost to the project: €0.** The Groq Free plan does not charge, and usage is limited by rate limits instead.

For comparison, the paid on-demand price for `openai/gpt-oss-20b` is $0.075 per million input tokens and $0.30 per million output tokens. One commentary request is roughly 150 input tokens and up to about 250 output tokens including reasoning, so under $0.0001 per request, or about 9 cents per thousand requests.

The Free plan limits requests and tokens per minute and per day for each model. The current figures for this account are on the Limits page of the Groq console. Because identical selections are answered from the cache, the app makes far fewer requests than it serves pages.
