{{ config(materialized='view') }}

select 
    coin_id,
    coin_name,
    symbol,
    price_usd,
    market_cap,
    volume_24h,
    last_updated,
    ingestion_timestamp
from {{ ref('int_coins_cleaned') }}
order by market_cap desc
limit 10