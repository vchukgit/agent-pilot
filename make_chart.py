import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from rgm_metrics import compute_rgm_metrics

metrics = compute_rgm_metrics("bark_bowl_pos_data.csv")
skus = list(metrics["by_sku"].keys())
short_names = [s.replace(" & ", "&\n") for s in skus]
share = [metrics["by_sku"][s]["category_share_pct"] for s in skus]
lift = [metrics["by_sku"][s]["promo_lift_pct"] for s in skus]

fig, axes = plt.subplots(1, 2, figsize=(10, 4.5))
axes[0].bar(short_names, share, color="#4C72B0")
axes[0].set_title("Category $ Share by SKU")
axes[0].set_ylabel("% of category dollars")
axes[1].bar(short_names, lift, color="#DD8452")
axes[1].set_title("Promo Lift by SKU")
axes[1].set_ylabel("% incremental $ vs. base")
fig.suptitle("Bark & Bowl RGM Snapshot, 8-Week POS Data")
fig.tight_layout()
fig.savefig("rgm_chart.png", dpi=150)
print("Wrote rgm_chart.png")
