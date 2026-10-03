{{ config(store_failures=true, schema='dq_failures') }}
select * from {{ ref('stg_pos_data') }}
where acv_distribution_pct < 0 or acv_distribution_pct > 100
