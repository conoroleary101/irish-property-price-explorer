# Database Utilities

Scripts for inspecting the PSRA Property Price Register, initialising the SQLite database and verifying its schema.

Run all commands from the repository root.

## CSV inspection

```powershell
python scripts/database/inspect_csv.py
```

Prints the CSV column headers and the first five records.

## Data profiling

```powershell
python scripts/profile_data.py
```

Generates the dataset statistics documented in `docs/data-profile.md`.

## Price and flag verification

```powershell
python scripts/database/check_prices_flags.py
```

Counts prices containing non-zero cents and reports the distribution of the Not Full Market Price and VAT Exclusive flags.

## Database initialisation

```powershell
python scripts/database/init_db.py
```

Creates the SQLite database using `scripts/schema.sql`, including the `sales` table and its indexes. Existing tables and records are preserved.

## Database verification

```powershell
python scripts/database/verify_db.py
```

Displays the sales table structure, indexes and record count. Reports PASS when the expected columns and indexes exist.

## Import Verification

```powershell
python scripts/database/verify_import.py
```

Verifies the following:
- total records are 814413
- Full-market-price records are 772923
- Flagged records are 41490
- NULL Eircodes are 558595-
- NULL property sizes are 761567

and returns some sample records, along with an Overall Verification

## References

- `docs/database-schema.md` - Database structure and field conventions.
- `docs/data-profile.md` - Dataset profiling results.
- `scripts/schema.sql` - Executable SQLite schema.

The CSV file and generated SQLite database are local data files and are not committed to the repository.

### Commentary Cache (IPPE-25)

Generated commentary is stored in SQLite using a SHA-256
fingerprint of the summary data.

To clear cached commentary:

    python scripts/database/clear_commentary_cache.py

The command requires entering `CLEAR` before deleting entries.

To preview cache warm-up for selected counties:

    python scripts/database/warm_commentary_cache.py Cork Dublin

To generate and cache responses:

    python scripts/database/warm_commentary_cache.py Cork Dublin --execute

Optional `--year-from` and `--year-to` arguments must match
the filters used during the demonstration.

The `DATABASE` configuration must point to the intended
SQLite database. An API key must be supplied through the
environment, not committed to the repository.

The cache should be warmed on the deployed environment
before the presentation.