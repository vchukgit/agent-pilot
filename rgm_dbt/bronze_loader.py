import duckdb
import os
import glob
from datetime import datetime, timezone

DB_PATH = "rgm.duckdb"
INCOMING_DIR = "incoming"

con = duckdb.connect(DB_PATH)

con.execute("""
    CREATE TABLE IF NOT EXISTS _load_manifest (
        source_file VARCHAR,
        batch_id INTEGER,
        loaded_at TIMESTAMP,
        row_count INTEGER
    )
""")

con.execute("""
    CREATE TABLE IF NOT EXISTS raw_pos_data (
        batch_id INTEGER,
        source_file VARCHAR,
        ingested_at TIMESTAMP,
        week INTEGER,
        sku VARCHAR,
        upc VARCHAR,
        pack_lbs INTEGER,
        acv_distribution_pct DOUBLE,
        unit_sales INTEGER,
        dollar_sales DOUBLE,
        base_unit_sales INTEGER,
        base_dollar_sales DOUBLE,
        is_promo VARCHAR
    )
""")

already_loaded = set(
    r[0] for r in con.execute("SELECT source_file FROM _load_manifest").fetchall()
)

next_batch_id = con.execute(
    "SELECT COALESCE(MAX(batch_id), 0) + 1 FROM _load_manifest"
).fetchone()[0]

new_files = sorted(glob.glob(os.path.join(INCOMING_DIR, "*.csv")))
loaded_any = False

for filepath in new_files:
    filename = os.path.basename(filepath)
    if filename in already_loaded:
        print(f"[skip] {filename} already loaded, skipping")
        continue

    now = datetime.now(timezone.utc)
    con.execute(f"""
        INSERT INTO raw_pos_data
        SELECT
            {next_batch_id} AS batch_id,
            '{filename}' AS source_file,
            TIMESTAMP '{now}' AS ingested_at,
            *
        FROM read_csv_auto('{filepath}')
    """)
    row_count = con.execute(
        f"SELECT COUNT(*) FROM raw_pos_data WHERE source_file = '{filename}'"
    ).fetchone()[0]

    con.execute(
        "INSERT INTO _load_manifest VALUES (?, ?, ?, ?)",
        [filename, next_batch_id, now, row_count]
    )
    print(f"[loaded] {filename} as batch {next_batch_id}, {row_count} rows")
    next_batch_id += 1
    loaded_any = True

if not loaded_any:
    print("No new files to load.")

total_rows = con.execute("SELECT COUNT(*) FROM raw_pos_data").fetchone()[0]
print(f"\nraw_pos_data now has {total_rows} total rows.")
con.close()
