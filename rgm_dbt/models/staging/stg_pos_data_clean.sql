with valid as (
    select *
    from {{ ref('stg_pos_data') }}
    where acv_distribution_pct between 0 and 100
      and unit_sales >= 0
      and dollar_sales >= 0
),
ranked as (
    select *,
        row_number() over (
            partition by week, sku
            order by ingested_at desc, batch_id desc
        ) as rn
    from valid
)
select
    batch_id, source_file, ingested_at, week, sku, upc, pack_lbs,
    acv_distribution_pct, unit_sales, dollar_sales, base_unit_sales,
    base_dollar_sales, is_promo, incremental_dollar_sales, incremental_unit_sales
from ranked
where rn = 1
