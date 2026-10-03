import random
random.seed(42)

skus = {
    "Chicken & Rice 4lb":   {"upc": "00012345601", "pack_lbs": 4,  "base_price": 12.99, "base_units": 1800, "acv_start": 90, "acv_end": 93, "promo_weeks": {3,4}, "discount": 0.15, "lift": 0.50},
    "Chicken & Rice 15lb":  {"upc": "00012345602", "pack_lbs": 15, "base_price": 34.99, "base_units": 950,  "acv_start": 87, "acv_end": 89, "promo_weeks": {5,6}, "discount": 0.12, "lift": 0.40},
    "Salmon & Sweet Potato 15lb": {"upc": "00012345603", "pack_lbs": 15, "base_price": 39.99, "base_units": 400, "acv_start": 45, "acv_end": 72, "promo_weeks": {6,7,8}, "discount": 0.20, "lift": 0.90},
}

rows = ["week,sku,upc,pack_lbs,acv_distribution_pct,unit_sales,dollar_sales,base_unit_sales,base_dollar_sales,is_promo"]

for week in range(1, 9):
    for sku, cfg in skus.items():
        acv = cfg["acv_start"] + (cfg["acv_end"] - cfg["acv_start"]) * (week - 1) / 7
        acv = round(acv + random.uniform(-1, 1), 1)

        noise = random.uniform(0.95, 1.05)
        base_units = round(cfg["base_units"] * noise)
        base_price = cfg["base_price"]
        base_dollar = round(base_units * base_price, 2)

        is_promo = week in cfg["promo_weeks"]
        if is_promo:
            price = round(base_price * (1 - cfg["discount"]), 2)
            unit_sales = round(base_units * (1 + cfg["lift"]))
        else:
            price = base_price
            unit_sales = base_units
        dollar_sales = round(unit_sales * price, 2)

        rows.append(f'{week},{sku},{cfg["upc"]},{cfg["pack_lbs"]},{acv},{unit_sales},{dollar_sales},{base_units},{base_dollar},{is_promo}')

with open("bark_bowl_pos_data.csv", "w") as f:
    f.write(chr(10).join(rows))

print("Wrote bark_bowl_pos_data.csv")
