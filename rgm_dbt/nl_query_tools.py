import os
import duckdb

DB_PATH = "rgm.duckdb"
ALLOWED_TABLES = ["rgm_metrics_gold", "rgm_weekly_gold"]
# dbt views reference the database by its file name, so attach under that same name
DB_ALIAS = os.path.splitext(os.path.basename(DB_PATH))[0]

TABLE_NOTES = {
    "rgm_metrics_gold": (
        "One row per SKU, aggregated across all loaded weeks. "
        "avg_price_per_unit = total dollars / total units. "
        "avg_price_per_lb = total dollars / total pounds sold. "
        "avg_acv_distribution_pct = simple average of weekly ACV. "
        "acv_first_week / acv_last_week = ACV in the earliest / latest week present for that SKU. "
        "promo_penetration_pct = percent of units sold in promo weeks. "
        "promo_lift_pct = 100 * (dollars - base dollars) / base dollars. "
        "incremental_dollars = dollars minus base dollars. "
        "category_share_pct = the SKU's share of total dollars across all SKUs."
    ),
    "rgm_weekly_gold": (
        "One row per SKU per week. price_per_unit = dollars / units. "
        "incremental_dollar_sales = dollars minus base dollars for that week. "
        "week_category_share_pct = the SKU's share of that week's dollars across the SKUs present that week."
    ),
}


def _sandbox():
    con = duckdb.connect(":memory:")
    con.execute(f"ATTACH '{DB_PATH}' AS {DB_ALIAS} (READ_ONLY)")
    for t in ALLOWED_TABLES:
        con.execute(f"CREATE TABLE {t} AS SELECT * FROM {DB_ALIAS}.main.{t}")
    con.execute(f"DETACH {DB_ALIAS}")
    con.execute("SET enable_external_access=false")
    con.execute("SET lock_configuration=true")
    return con


def get_data_context():
    con = _sandbox()
    tables = {}
    for t in ALLOWED_TABLES:
        cols = con.execute(
            "select column_name, data_type from information_schema.columns "
            f"where table_name = '{t}' order by ordinal_position"
        ).fetchall()
        tables[t] = {
            "description": TABLE_NOTES[t],
            "columns": [{"name": c, "type": d} for c, d in cols],
        }

    coverage_rows = con.execute(
        "select week, count(*) as skus_present from rgm_weekly_gold group by week order by week"
    ).fetchall()
    total_skus = con.execute("select count(*) from rgm_metrics_gold").fetchone()[0]
    coverage = [
        {"week": w, "skus_present": n, "complete": n == total_skus}
        for w, n in coverage_rows
    ]
    con.close()
    return {
        "tables": tables,
        "total_skus": total_skus,
        "weekly_coverage": coverage,
        "note": (
            "Rows that failed data quality checks are excluded, so a week can be "
            "incomplete. Flag incomplete weeks when a question compares across weeks."
        ),
    }


def run_readonly_query(sql, max_rows=50):
    con = _sandbox()
    try:
        statements = con.extract_statements(sql)
        if len(statements) != 1:
            return {"error": "Send exactly one SQL statement."}
        if statements[0].type != duckdb.StatementType.SELECT:
            return {"error": "Only read-only SELECT queries are allowed."}
        cur = con.execute(sql)
        columns = [d[0] for d in cur.description]
        rows = cur.fetchmany(max_rows + 1)
        truncated = len(rows) > max_rows
        return {
            "columns": columns,
            "rows": [list(r) for r in rows[:max_rows]],
            "truncated": truncated,
        }
    except Exception as e:
        return {"error": str(e)}
    finally:
        con.close()


if __name__ == "__main__":
    import json
    print(json.dumps(get_data_context(), indent=2, default=str))
