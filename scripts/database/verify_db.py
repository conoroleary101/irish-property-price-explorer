import os
import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

db_path = Path(os.environ.get("DATABASE", "property.db"))
if not db_path.is_absolute():
    db_path = ROOT / db_path

if not db_path.is_file():
    raise SystemExit(f"Database not found: {db_path}")

connection = sqlite3.connect(db_path)

try:
    columns = list(connection.execute("PRAGMA table_info(sales)"))
    indexes = list(connection.execute("PRAGMA index_list(sales)"))
    count = connection.execute(
        "SELECT COUNT(*) FROM sales"
    ).fetchone()[0]

    print("Table structure:")
    for column in columns:
        print(column)

    print("\nIndexes:")
    for index in indexes:
        print(index)

    print("\nRecords:", count)

    column_names = {column[1] for column in columns}
    index_names = {index[1] for index in indexes}

    expected_columns = {
        "id", "date_of_sale", "address", "county",
        "eircode", "price", "not_full_market_price",
        "vat_exclusive", "description_of_property",
        "property_size_description"
    }

    expected_indexes = {
        "idx_sales_county",
        "idx_sales_date"
    }

    if column_names == expected_columns and expected_indexes <= index_names:
        print("\nSchema verification: PASS")
    else:
        print("\nSchema verification: FAIL")
        raise SystemExit(1)

finally:
    connection.close()
