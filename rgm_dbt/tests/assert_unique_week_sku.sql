{{ config(store_failures=true, schema='dq_failures') }}
select s.*
from {{ ref('stg_pos_data_current') }} s
join (
    select week, sku
    from {{ ref('stg_pos_data_current') }}
    group by week, sku
    having count(*) > 1
) dupes
  on s.week = dupes.week and s.sku = dupes.sku
