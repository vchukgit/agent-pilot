with sku_agg as (
    select
        sku,
        sum(unit_sales) as total_unit_sales,
        sum(dollar_sales) as total_dollar_sales,
        sum(base_unit_sales) as total_base_unit_sales,
        sum(base_dollar_sales) as total_base_dollar_sales,
        sum(unit_sales * pack_lbs) as total_volume_lbs,
        avg(acv_distribution_pct) as avg_acv_distribution_pct,
        sum(case when is_promo then unit_sales else 0 end) as promo_units
    from {{ ref('stg_pos_data_clean') }}
    group by sku
),
acv_trend as (
    select
        sku,
        min_by(acv_distribution_pct, week) as acv_first_week,
        max_by(acv_distribution_pct, week) as acv_last_week
    from {{ ref('stg_pos_data_clean') }}
    group by sku
),
category_total as (
    select sum(dollar_sales) as total_category_dollars
    from {{ ref('stg_pos_data_clean') }}
)
select
    a.sku,
    round(a.total_dollar_sales / a.total_unit_sales, 2) as avg_price_per_unit,
    round(a.total_dollar_sales / a.total_volume_lbs, 2) as avg_price_per_lb,
    round(a.avg_acv_distribution_pct, 1) as avg_acv_distribution_pct,
    t.acv_first_week,
    t.acv_last_week,
    round(100.0 * a.promo_units / a.total_unit_sales, 1) as promo_penetration_pct,
    round(100.0 * (a.total_dollar_sales - a.total_base_dollar_sales) / a.total_base_dollar_sales, 1) as promo_lift_pct,
    round(a.total_dollar_sales - a.total_base_dollar_sales, 2) as incremental_dollars,
    round(100.0 * a.total_dollar_sales / c.total_category_dollars, 1) as category_share_pct,
    round(a.total_dollar_sales, 2) as total_dollar_sales,
    a.total_unit_sales
from sku_agg a
join acv_trend t on a.sku = t.sku
cross join category_total c
order by a.sku
