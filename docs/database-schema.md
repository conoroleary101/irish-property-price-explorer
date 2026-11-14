# Database Schema - Irish Property Price Explorer

**Database:** `property.db` (default; path set by the `DATABASE` configuration value)  
**Table:** `sales`  
**Data source:** PSRA Residential Property Price Register (`PPR-ALL.csv`, Windows-1252 / `cp1252` encoding)

## `sales` columns

| Column | SQLite definition | CSV source | Stored value |
| --- | --- | --- | --- |
| `id` | `INTEGER PRIMARY KEY` | - | SQLite-generated row identifier |
| `date_of_sale` | `TEXT NOT NULL` | `Date of Sale (dd/mm/yyyy)` | ISO date string: `YYYY-MM-DD` |
| `address` | `TEXT NOT NULL` | `Address` | Original address text |
| `county` | `TEXT NOT NULL` | `County` | County name |
| `eircode` | `TEXT` | `Eircode` | Text; `NULL` if blank |
| `price` | `INTEGER NOT NULL` | `Price` | Whole euros, e.g. `285000` |
| `not_full_market_price` | `INTEGER NOT NULL DEFAULT 0` | `Not Full Market Price` | `1` = Yes; `0` = No |
| `vat_exclusive` | `INTEGER NOT NULL DEFAULT 0` | `VAT Exclusive` | `1` = Yes; `0` = No |
| `description_of_property` | `TEXT` | `Description of Property` | Original property description text |
| `property_size_description` | `TEXT` | `Property Size Description` | Text; `NULL` if blank |

## SQLite definition

```sql
CREATE TABLE IF NOT EXISTS sales (
    id INTEGER PRIMARY KEY,
    date_of_sale TEXT NOT NULL,
    address TEXT NOT NULL,
    county TEXT NOT NULL,
    eircode TEXT,
    price INTEGER NOT NULL,
    not_full_market_price INTEGER NOT NULL DEFAULT 0
        CHECK (not_full_market_price IN (0, 1)),
    vat_exclusive INTEGER NOT NULL DEFAULT 0
        CHECK (vat_exclusive IN (0, 1)),
    description_of_property TEXT,
    property_size_description TEXT
);

CREATE INDEX IF NOT EXISTS idx_sales_county ON sales(county);
CREATE INDEX IF NOT EXISTS idx_sales_date ON sales(date_of_sale);
```

## Data conventions

- `date_of_sale` is stored as an ISO date string (`YYYY-MM-DD`), not a timestamp.
- `price` is stored as an integer number of euros. Source prices containing fractional euros are rounded to the nearest whole euro using `ROUND_HALF_UP`.
- `not_full_market_price` and `vat_exclusive` use integer boolean values (`0` or `1`).
- Blank source values for `eircode` and `property_size_description` are stored as SQL `NULL`.
- Rows marked `not_full_market_price = 1` remain in `sales`; full-market-price statistics use `not_full_market_price = 0`.
- `id` is a database-generated row identifier; it is not a field in the source CSV.

## Application data contract

**Listing fields:** `date_of_sale`, `address`, `county`, `price`, `description_of_property`.

**Listing order:** `date_of_sale DESC, id DESC`. **Page size:** 50 rows.

**Display input formats:** `date_of_sale` -> `2024-03-14`; `price` -> `285000`.

**Indexes:** `idx_sales_county` on `county`; `idx_sales_date` on `date_of_sale`.