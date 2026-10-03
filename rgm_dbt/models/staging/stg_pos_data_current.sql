with latest_batch as (
    select week, sku, max(batch_id) as batch_id
    from {{ ref('stg_pos_data') }}
    group by week, sku
)
select s.*
from {{ ref('stg_pos_data') }} s
join latest_batch l
  on s.week = l.week and s.sku = l.sku and s.batch_id = l.batch_id
