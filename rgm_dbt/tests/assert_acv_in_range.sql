{{ config(store_failures=true, schema='dq_failures') }}
select * from {{ ref('stg_pos_data_current') }}
where acv_distribution_pct < 0 or acv_distribution_pct > 100
