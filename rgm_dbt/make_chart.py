"""
Plain code, no model involved. Draws the chart from the same gold
numbers the report agent reads, so the two can never disagree.
Needs: pip3 install matplotlib
"""

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from gold_metrics import get_gold_metrics

metrics = get_gold_metrics()
skus = metrics["skus"]
names = [s["sku"].replace(" & ", "&\n") for s in skus]
share = [s["category_share_pct"] for s in skus]
lift = [s["promo_lift_pct"] for s in skus]

weeks = metrics["weeks_loaded"]
subtitle = f"weeks {weeks['first']} to {weeks['last']}"
if metrics["incomplete_weeks"]:
    subtitle += f" (incomplete: {', '.join(str(w) for w in metrics['incomplete_weeks'])})"

fig, axes = plt.subplots(1, 2, figsize=(10, 4.5))
axes[0].bar(names, share, color="#4C72B0")
axes[0].set_title("Category $ Share by SKU")
axes[0].set_ylabel("% of category dollars")
axes[1].bar(names, lift, color="#DD8452")
axes[1].set_title("Promo Lift by SKU")
axes[1].set_ylabel("% incremental $ vs. base")
fig.suptitle(f"Bark & Bowl RGM Snapshot, {subtitle}")
fig.tight_layout()
fig.savefig("rgm_chart.png", dpi=150)
print("Wrote rgm_chart.png")
