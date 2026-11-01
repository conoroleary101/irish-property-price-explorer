# Irish Property Price Explorer

A web app to search, filter and compare residential property sale prices in Ireland.

Built for the Agile Processes module (COMP7039), BSc (Hons) Software Development, Year 3, Munster Technological University.

## Team

- Conor O'Leary
- Katie McGrath - Templates and UX (Frontend)
- Saadman Chowdhury
- Christopher Bowes
- Samuel Ignacio Acosta

## Data

Residential Property Price Register, published by the Property Services Regulatory Authority (PSRA).

https://www.propertypriceregister.ie/website/npsra/pprweb.nsf/page/ppr-home-en

Snapshot used: register last updated 09/09/2026. 805,311 rows covering 1 January 2010 to 4 September 2026, all 26 counties.

Note: the CSV is Windows-1252 encoded, not UTF-8.

Contains Irish public sector information reused under the PSRA's re-use of public sector information terms.

## Tech stack

Python, Flask, Jinja2, SQLite, pandas, matplotlib, pytest, GitHub Actions.

## Run locally

Requires Python 3.12 or later and Git.

**1. Clone and enter the repo**

    git clone https://github.com/conoroleary101/irish-property-price-explorer.git
    cd irish-property-price-explorer

**2. Create and activate a virtual environment**

Windows PowerShell:

    python -m venv .venv
    Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned
    .\.venv\Scripts\Activate.ps1

macOS or Linux:

    python3 -m venv .venv
    source .venv/bin/activate

The prompt starts with `(.venv)` once it is active.

**3. Install dependencies**

    pip install -r requirements.txt

**4. Run the app**

    flask --app app run --debug

Open http://127.0.0.1:5000

## Configuration

Settings live in `config.py` and are selected with the `FLASK_CONFIG` environment variable. It defaults to `development`, so no setup is needed locally.

| Value | Debug | Database |
| --- | --- | --- |
| `development` (default) | on | `property.db` |
| `production` | off | `property.db` |
| `testing` | off | `test.db` |

`SECRET_KEY` is read from the environment. Development uses a placeholder. Production refuses to start unless a real `SECRET_KEY` is set, so no secret is ever committed to the repository.

## Status

Sprint 1 (28 Sep to 12 Oct 2026) in progress.

## Running tests

```bash
pip install -r requirements.txt
pytest
```
## Deployment (PythonAnywhere)

Live site: https://chrisbowes.pythonanywhere.com

1. On PythonAnywhere, open a Bash console and run:

       git clone https://github.com/conoroleary101/irish-property-price-explorer.git
       mkvirtualenv ippe-venv --python=python3.13
       pip install -r irish-property-price-explorer/requirements.txt

2. Web tab → Add a new web app → Manual configuration → Python 3.13.
3. Set Source code to `/home/<username>/irish-property-price-explorer`.
4. Set Virtualenv to `/home/<username>/.virtualenvs/ippe-venv`.
5. Replace the WSGI file contents with:

       import sys
       path = "/home/<username>/irish-property-price-explorer"
       if path not in sys.path:
           sys.path.insert(0, path)
       from app import create_app
       application = create_app()

6. Click Reload, then check `/health` returns `{"status": "ok"}`.

To update after changes are merged to main: in a Bash console run
`cd irish-property-price-explorer && git pull`, then click Reload on the Web tab.

Disk usage after deploying the skeleton: 36 MB of 512 MB (free tier).