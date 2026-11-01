# Data quality profile: Residential Property Price Register

- **Source:** PSRA Residential Property Price Register, PPR-ALL.zip
- **Downloaded:** 30/10/2026
- **Register last updated:** 23/10/2026 HH:MM (fill in from PSRA page)
- **Produced by:** `scripts/profile_data.py` (Python standard library only)

## Size and date range

| Measure | Value |
|---|---|
| Total rows | 814,413 |
| Earliest sale | 01/01/2010 |
| Latest sale | 23/10/2026 |

## Missing values per column

| Column | Null % |
|---|---|
| Date of Sale | 0.00% |
| Address | 0.00% |
| County | 0.00% |
| Eircode | 68.59% |
| Price | 0.00% |
| Not Full Market Price | 0.00% |
| VAT Exclusive | 0.00% |
| Description of Property | 0.00% |
| Property Size Description | 93.51% |

## Prices

| Measure | Value |
|---|---|
| Minimum | €5,001 |
| Maximum | €387,665,198 |
| Median | €245,100 |
| Not Full Market Price rows | 41,490 (5.09%) |

## Rows per county

| County | Rows |
|---|---|
| Dublin | 255,242 |
| Cork | 90,120 |
| Kildare | 44,496 |
| Galway | 39,167 |
| Meath | 33,894 |
| Limerick | 29,821 |
| Wexford | 28,485 |
| Wicklow | 27,542 |
| Louth | 22,983 |
| Waterford | 22,286 |
| Kerry | 22,036 |
| Tipperary | 21,744 |
| Donegal | 21,580 |
| Mayo | 19,390 |
| Clare | 18,184 |
| Westmeath | 15,748 |
| Laois | 13,565 |
| Kilkenny | 13,154 |
| Cavan | 11,982 |
| Sligo | 11,832 |
| Roscommon | 11,461 |
| Offaly | 10,429 |
| Carlow | 8,862 |
| Leitrim | 7,143 |
| Longford | 6,856 |
| Monaghan | 6,411 |

## Findings for the team

- The euro sign in the price column header is corrupted in the source file. Code should find the column by its "Price" prefix and strip non-numeric characters from values, not match "€".
- The maximum price reflects bulk multi-unit sales, which heavily skew averages. Use the median for summaries.
- Eircode is mostly empty (introduced in 2015, often not recorded), so it is not usable for location filtering.
- Property Size Description is over 93% empty, so it is not usable as a filter.
- About 5% of rows are flagged Not Full Market Price; these should be excluded or flagged in price statistics.