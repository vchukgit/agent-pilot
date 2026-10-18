"""
Pure query module, no LLM. Reads the dbt failure tables, then explains
every row the clean model excluded: why it was excluded, and whether
that left the data fine, stale, or with a gap. The agent only ever sees
this output, so anything it needs to say has to be in here.
"""

import duckdb

EXCLUSION_SQL = """
with s as (
    select batch_id, source_file, week, sku,
        case when acv_distribution_pct < 0 or acv_distribution_pct > 100 then 'acv_out_of_range'
             when unit_sales < 0 or dollar_sales < 0 then 'negative_sales'
        end as invalid_reason
    from stg_pos_data
),
c as (select week, sku, batch_id as clean_batch_id from stg_pos_data_clean),
g as (
    select s.week, s.sku, s.batch_id, s.source_file, s.invalid_reason,
           c.clean_batch_id, count(*) as n
    from s left join c on s.week = c.week and s.sku = c.sku
    group by all
),
x as (
    select week, sku, batch_id, source_file, clean_batch_id,
        case when invalid_reason is not null then invalid_reason
             when batch_id < clean_batch_id then 'superseded_by_later_batch'
             else 'duplicate_resend' end as reason,
        case when invalid_reason is not null then n
             when batch_id < clean_batch_id then n
             else n - 1 end as rows_excluded,
        case when clean_batch_id is null then 'no_clean_row_data_gap'
             when invalid_reason is not null and clean_batch_id < batch_id then 'stale_value_in_use'
             when clean_batch_id > batch_id then 'replaced_by_later_batch'
             else 'one_copy_kept' end as resolution
    from g
)
select week, sku, batch_id, source_file, reason, rows_excluded, resolution, clean_batch_id
from x where rows_excluded > 0
order by week, sku, batch_id
"""

RESOLUTION_MEANING = {
    "replaced_by_later_batch": "A later batch supplied a valid row for this week and SKU, so nothing is missing.",
    "one_copy_kept": "An exact duplicate within the same batch; one copy is kept, nothing is missing.",
    "no_clean_row_data_gap": "No valid row exists for this week and SKU, so it is missing from clean and gold.",
    "stale_value_in_use": "A newer batch was rejected as invalid, so an OLDER valid row is still being used for this week and SKU.",
}


def get_dq_summary(db_path="rgm.duckdb"):
    con = duckdb.connect(db_path, read_only=True)

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
    combos = con.execute(
        "select count(*) from (select distinct week, sku from stg_pos_data)"
    ).fetchone()[0]

    cur = con.execute(EXCLUSION_SQL)
    cols = [d[0] for d in cur.description]
    excluded = [dict(zip(cols, r)) for r in cur.fetchall()]
    con.close()

    needs_attention = [
        e for e in excluded
        if e["resolution"] in ("no_clean_row_data_gap", "stale_value_in_use")
    ]

    return {
        "current_state": {
            "week_sku_combinations_loaded": combos,
            "combinations_with_a_clean_row": total_clean,
            "combinations_missing_a_clean_row": combos - total_clean,
        },
        "history_note": (
            "stg_pos_data keeps every batch ever loaded, so total_rows_staged includes "
            "old versions that later batches replaced. Do not treat staged minus clean "
            "as a failure rate."
        ),
        "total_rows_staged": total_staged,
        "total_rows_clean": total_clean,
        "rows_excluded_by_clean_model": total_staged - total_clean,
        "excluded_rows_by_reason": excluded,
        "resolution_meanings": RESOLUTION_MEANING,
        "exclusions_needing_attention": needs_attention,
        "failing_tests": findings,
    }


if __name__ == "__main__":
    import json
    print(json.dumps(get_dq_summary(), indent=2, default=str))
