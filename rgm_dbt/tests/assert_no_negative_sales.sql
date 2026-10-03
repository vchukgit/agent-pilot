{{ config(store_failures=true, schema='dq_failures') }}
select * from {{ ref('stg_pos_data_current') }}
where unit_sales < 0 or dollar_sales < 0
