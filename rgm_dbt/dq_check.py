import duckdb

def get_dq_summary(db_path="rgm.duckdb"):
    con = duckdb.connect(db_path)

    failure_tables = con.execute(
        "select table_name from information_schema.tables "
        "where table_schema = 'main_dq_failures'"
    ).fetchall()

    findings = {}
    for (table_name,) in failure_tables:
        rows = con.execute(f"select * from main_dq_failures.{table_name}").fetchall()
        columns = [desc[0] for desc in con.description]
        if rows:
            findings[table_name] = {
                "failing_row_count": len(rows),
                "sample_rows": [
                    {col: str(val) for col, val in zip(columns, row)}
                    for row in rows[:10]
                ],
            }

    total_staged = con.execute("select count(*) from stg_pos_data").fetchone()[0]
    total_clean = con.execute("select count(*) from stg_pos_data_clean").fetchone()[0]

    con.close()

    return {
        "total_rows_staged": total_staged,
        "total_rows_clean": total_clean,
        "rows_excluded_by_clean_model": total_staged - total_clean,
        "failing_tests": findings,
    }

if __name__ == "__main__":
    import json
    print(json.dumps(get_dq_summary(), indent=2))
