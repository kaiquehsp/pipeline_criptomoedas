with deduplicacao as (
    select 
        *,
        row_number() over (
            partition by coin_id            
            order by ingestion_timestamp desc 
        ) as rn
    from {{ ref('stg_df_coins') }}
)

select 
    coin_id,
    coin_name,
    symbol,
    price_usd,
    volume_24h,
    market_cap,
    last_updated,
    ingestion_timestamp
from deduplicacao
where rn = 1  