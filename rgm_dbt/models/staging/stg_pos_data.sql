select
    batch_id,
    source_file,
    ingested_at,
    cast(week as integer)                  as week,
    sku,
    upc,
    cast(pack_lbs as integer)               as pack_lbs,
    cast(acv_distribution_pct as double)    as acv_distribution_pct,
    cast(unit_sales as integer)             as unit_sales,
    cast(dollar_sales as double)            as dollar_sales,
    cast(base_unit_sales as integer)        as base_unit_sales,
    cast(base_dollar_sales as double)       as base_dollar_sales,
    cast(is_promo as boolean)               as is_promo,
    (dollar_sales - base_dollar_sales)      as incremental_dollar_sales,
    (unit_sales - base_unit_sales)          as incremental_unit_sales
from {{ source('raw', 'raw_pos_data') }}
