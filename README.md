# Irish Property Price Explorer

[![CI](https://github.com/conoroleary101/irish-property-price-explorer/actions/workflows/ci.yml/badge.svg)](https://github.com/conoroleary101/irish-property-price-explorer/actions/workflows/ci.yml)

A web app to search, filter and compare residential property sale prices in Ireland.

**Live site:** https://chrisbowes.pythonanywhere.com

Built for the Agile Processes module (COMP7039), BSc (Hons) Software Development, Year 3, Munster Technological University.

## What it does

The app has three components, one per sprint:

| Component | What the user gets |
| --- | --- |
| Data input | The full Property Price Register cleaned, validated and loaded into an indexed SQLite database |
| Data presentation and visualisation | Sales filtered by county, year, price and property type, with count, mean and median price, price trend charts and a two-county comparison |
| Knowledge extraction | A short plain-English commentary on the figures for the current selection, written by a language model from the summary figures only |

## Team

- Conor O'Leary
- Katie McGrath 
- Saadman Chowdhury
- Christopher Bowes
- Samuel Ignacio Acosta

## Data

[Residential Property Price Register](https://www.propertypriceregister.ie/website/npsra/pprweb.nsf/page/ppr-home-en), published by the Property Services Regulatory Authority (PSRA).

Snapshot used: downloaded 30 October 2026. 814,413 rows covering 1 January 2010 to 23 October 2026, all 26 counties. The full data profile is in [`docs/data-profile.md`](docs/data-profile.md).

Note: the CSV is Windows-1252 encoded, not UTF-8.

Contains Irish public sector information reused under the PSRA's re-use of public sector information terms.

## Tech stack

Python, Flask, Jinja2, SQLite, matplotlib, pytest, pytest-cov, GitHub Actions, PythonAnywhere. Commentary uses the Groq API (free tier) through `requests`; see [`docs/ai-commentary.md`](docs/ai-commentary.md).

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

**4. Load the data**

The register snapshot is committed as `data/PPR-ALL.zip`. Unzip it into `data/`, create the database, then load it:

Windows PowerShell:

    Expand-Archive data\PPR-ALL.zip -DestinationPath data

macOS or Linux:

    unzip data/PPR-ALL.zip -d data

Then, on any system:

    python scripts/database/init_db.py
    python scripts/load_data.py
    python scripts/database/verify_import.py

`init_db.py` creates `property.db` with the `sales` table and its indexes. `load_data.py` cleans and loads every row, logging any rejected rows to `data/import_rejections.log`. `verify_import.py` should report 814,413 records, of which 772,923 are full market price. The CSV and the database are ignored by git. More database scripts are described in [`scripts/database/README.md`](scripts/database/README.md).

**5. Run the app**

    flask --app app run --debug

Open http://127.0.0.1:5000

## Configuration

Settings live in `config.py` and in environment variables. Nothing needs setting to run locally.

| Variable | Needed | Purpose |
| --- | --- | --- |
| `FLASK_CONFIG` | No | `development` (default, debug on), `production` (debug off) or `testing` (uses `test.db`) |
| `SECRET_KEY` | In production | Flask secret key. Development falls back to a placeholder |
| `DATABASE` | No | Path to the SQLite file. Defaults to `property.db` in the project folder |
| `GROQ_API_KEY` | For commentary | Groq API key. Without it the app still works and the commentary panel shows an "unavailable" notice |
| `COMMENTARY_MODEL` | No | Overrides the commentary model (default `openai/gpt-oss-20b`) |
| `DEPLOY_SECRET`, `WSGI_FILE` | On the server only | Used by the automated deployment route, see below |

Keys and secrets are set as environment variables (in the WSGI file on PythonAnywhere, and as GitHub secrets for CI). None are committed to the repository; the full git history was checked for API keys on 26 November 2026 and none were found.

## Running tests

    pip install -r requirements.txt
    python -m pytest

`pytest.ini` adds coverage reporting, so the run ends with a coverage table and writes `coverage.xml` and `htmlcov/`. The commentary tests mock the Groq API, so no key or network connection is needed. On Windows, use `python -m pytest` rather than `pytest` if Application Control blocks `pytest.exe`.

## Continuous integration and deployment

Every push and pull request runs the `test` job in [`.github/workflows/ci.yml`](.github/workflows/ci.yml). The badge at the top of this page shows the latest result on `main`.

Every push to `main` then deploys automatically, but only if the tests pass:

- The `deploy` job runs only after the `test` job succeeds, and only on `main`. If tests fail, nothing is deployed.
- It sends a POST request to `/deploy` on the live site with a secret token. The route runs `git pull` and then touches the WSGI file, which makes PythonAnywhere reload the app.
- This works on the PythonAnywhere free tier, which has no SSH access.
- The token is stored as the `DEPLOY_SECRET` GitHub secret and in the WSGI file on PythonAnywhere.

When something fails, the Actions log says what broke. Each step is named ("Run tests with coverage", "Pull and reload on PythonAnywhere", "Check the site is up after reload"), pytest names the failing test, and the deploy route's response names the step that failed (`git pull` or `reload`).

## Deployment (PythonAnywhere)

Live site: https://chrisbowes.pythonanywhere.com

1. On PythonAnywhere, open a Bash console and run:

       git clone https://github.com/conoroleary101/irish-property-price-explorer.git
       mkvirtualenv ippe-venv --python=python3.13
       pip install --no-cache-dir -r irish-property-price-explorer/requirements.txt

2. Load the data on the server, then delete the CSV to save disk space (the zip stays in the repository):

       cd ~/irish-property-price-explorer
       unzip data/PPR-ALL.zip -d data
       python scripts/database/init_db.py
       python scripts/load_data.py
       rm data/PPR-ALL.csv

3. Web tab → Add a new web app → Manual configuration → Python 3.13.
4. Set Source code to `/home/<username>/irish-property-price-explorer`.
5. Set Virtualenv to `/home/<username>/.virtualenvs/ippe-venv`.
6. Replace the WSGI file contents with the following, using your own username, deploy token and Groq key:

       import os
       import sys

       os.environ["DEPLOY_SECRET"] = "<your-deploy-secret>"
       os.environ["WSGI_FILE"] = "/var/www/<username>_pythonanywhere_com_wsgi.py"
       os.environ["GROQ_API_KEY"] = "<your-groq-api-key>"

       path = "/home/<username>/irish-property-price-explorer"
       if path not in sys.path:
           sys.path.insert(0, path)

       from app import create_app
       application = create_app()

7. Click Reload, then check `/health` returns `{"status": "ok"}` and the home page lists sales.

### Limits of the automated deployment

- **New packages are not installed by a deploy.** Before merging a pull request that changes `requirements.txt`, run `pip install --no-cache-dir -r requirements.txt` in the server virtualenv first. Otherwise the new code cannot import the package and every page returns an error. This happened twice during the project (matplotlib and requests).
- **The database is not rebuilt by a deploy.** If the schema or data changes, run the scripts in step 2 on the server by hand.
- **Disk space is limited to 512 MB** on the free tier. Check it with `du -sh ~`. Use `--no-cache-dir` with pip and do not keep the unzipped CSV on the server.

Manual fallback: in a PythonAnywhere Bash console run `cd irish-property-price-explorer && git pull`, then click Reload on the Web tab.

Disk usage on 26 November 2026: [436] MB of 512 MB.

## Project status

Sprint 3 of 3 (21 to 30 November 2026), the final sprint: knowledge extraction and final delivery.

| Sprint | Dates | Goal |
| --- | --- | --- |
| 1 | 31 October to 7 November 2026 | Load the register into a tested, deployed Flask app that lists real sales |
| 2 | 9 to 21 November 2026 | Filter the register and compare prices across counties and over time |
| 3 | 21 to 30 November 2026 | Identify the most affordable areas and explain the result in plain English |

Project management is in Jira (project IPPE) and Confluence (space IPPE).
