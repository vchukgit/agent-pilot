import csv
from collections import defaultdict

def compute_rgm_metrics(filepath):
    rows = []
    with open(filepath, "r") as f:
        for r in csv.DictReader(f):
            rows.append(r)

    by_sku = defaultdict(list)
    for r in rows:
        by_sku[r["sku"]].append(r)

    total_category_dollars = sum(float(r["dollar_sales"]) for r in rows)

    results = {}
    for sku, sku_rows in by_sku.items():
        total_units = sum(int(r["unit_sales"]) for r in sku_rows)
        total_dollars = sum(float(r["dollar_sales"]) for r in sku_rows)
        total_base_units = sum(int(r["base_unit_sales"]) for r in sku_rows)
        total_base_dollars = sum(float(r["base_dollar_sales"]) for r in sku_rows)
        total_volume_lbs = sum(int(r["unit_sales"]) * int(r["pack_lbs"]) for r in sku_rows)

        promo_rows = [r for r in sku_rows if r["is_promo"] == "True"]
        promo_units = sum(int(r["unit_sales"]) for r in promo_rows)

        incremental_dollars = total_dollars - total_base_dollars
        acv_values = [float(r["acv_distribution_pct"]) for r in sku_rows]

        results[sku] = {
            "avg_price_per_unit": round(total_dollars / total_units, 2),
            "avg_price_per_lb": round(total_dollars / total_volume_lbs, 2),
            "avg_acv_distribution_pct": round(sum(acv_values) / len(acv_values), 1),
            "acv_distribution_trend": {"first_week": acv_values[0], "last_week": acv_values[-1]},
            "promo_penetration_pct": round(100 * promo_units / total_units, 1),
            "promo_lift_pct": round(100 * incremental_dollars / total_base_dollars, 1),
            "incremental_dollars": round(incremental_dollars, 2),
            "category_share_pct": round(100 * total_dollars / total_category_dollars, 1),
            "total_dollar_sales": round(total_dollars, 2),
            "total_unit_sales": total_units,
        }

    return {"total_category_dollars": round(total_category_dollars, 2), "by_sku": results}

if __name__ == "__main__":
    import json
    metrics = compute_rgm_metrics("bark_bowl_pos_data.csv")
    print(json.dumps(metrics, indent=2))
