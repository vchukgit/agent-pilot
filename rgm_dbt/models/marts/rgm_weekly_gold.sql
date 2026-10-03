select
    week,
    sku,
    is_promo,
    unit_sales,
    round(dollar_sales, 2)                                   as dollar_sales,
    round(dollar_sales / unit_sales, 2)                      as price_per_unit,
    acv_distribution_pct,
    round(dollar_sales - base_dollar_sales, 2)               as incremental_dollar_sales,
    round(100.0 * dollar_sales / sum(dollar_sales) over (partition by week), 1) as week_category_share_pct
from {{ ref('stg_pos_data_clean') }}
order by week, sku
