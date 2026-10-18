"""
Pure query module, no LLM. Reads the gold RGM tables and returns the
metrics plus enough coverage information for a reader to know what the
numbers are based on. Nothing is calculated here: every figure comes
straight from the dbt gold models, so the report agent and the chart
can never disagree with the warehouse.
"""

import duckdb

from nl_query_tools import TABLE_NOTES


def get_gold_metrics(db_path="rgm.duckdb"):
    con = duckdb.connect(db_path, read_only=True)

    cur = con.execute("select * from rgm_metrics_gold order by sku")
    cols = [d[0] for d in cur.description]
    skus = [dict(zip(cols, row)) for row in cur.fetchall()]

    week_rows = con.execute(
        "select week, count(*) as skus_present "
        "from rgm_weekly_gold group by week order by week"
    ).fetchall()
    con.close()

    total_skus = len(skus)
    coverage = [
        {"week": w, "skus_present": n, "complete": n == total_skus}
        for w, n in week_rows
    ]
    weeks = [c["week"] for c in coverage]

    return {
        "weeks_loaded": {
            "first": min(weeks) if weeks else None,
            "last": max(weeks) if weeks else None,
            "count": len(weeks),
        },
        "weekly_coverage": coverage,
        "incomplete_weeks": [c["week"] for c in coverage if not c["complete"]],
        "total_category_dollars": round(sum(s["total_dollar_sales"] for s in skus), 2),
        "metric_definitions": TABLE_NOTES["rgm_metrics_gold"],
        "skus": skus,
    }


if __name__ == "__main__":
    import json
    print(json.dumps(get_gold_metrics(), indent=2, default=str))
