with deduped as (
    select *,
        row_number() over (partition by week, sku order by ingested_at) as rn
    from {{ ref('stg_pos_data') }}
),
one_per_week_sku as (
    select * from deduped where rn = 1
)
select
    batch_id, source_file, ingested_at, week, sku, upc, pack_lbs,
    acv_distribution_pct, unit_sales, dollar_sales, base_unit_sales,
    base_dollar_sales, is_promo, incremental_dollar_sales, incremental_unit_sales
from one_per_week_sku
where acv_distribution_pct between 0 and 100
  and unit_sales >= 0
  and dollar_sales >= 0
