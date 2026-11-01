import os
import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCHEMA_PATH = ROOT / "scripts" / "schema.sql"

db_path = Path(os.environ.get("DATABASE", "property.db"))
if not db_path.is_absolute():
    db_path = ROOT / db_path

schema = SCHEMA_PATH.read_text(encoding="utf-8")

connection = sqlite3.connect(db_path)

try:
    connection.executescript(schema)
    connection.commit()
finally:
    connection.close()

print(f"Database schema initialised: {db_path}")
