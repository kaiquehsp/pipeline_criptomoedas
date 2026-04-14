{{ config(materialized='table') }}

with staging_history as (
    -- pegamos direto da staging para garantir que estamos pegando TODOS os dias de extração
    select * from {{ ref('stg_df_coins') }}
)

select
    coin_id,
    price_usd,
    volume_24h,
    market_cap,
    last_updated,
    ingestion_timestamp
from staging_history