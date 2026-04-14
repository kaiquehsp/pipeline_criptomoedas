{{ config(materialized='table') }}

with source_data as (
    select * from {{ source('bronze_layer', 'crypto_raw') }}
),

renamed as (
    select 
        cast(id as bigint) as coin_id,
        cast(name as varchar) as coin_name,
        cast(symbol as varchar) as symbol,
        cast("quote.USD.price" as decimal(18, 8)) as price_usd,
        cast("quote.USD.volume_24h" as decimal(18, 2)) as volume_24h,
        cast("quote.USD.market_cap" as decimal(18, 2)) as market_cap,
        cast("quote.USD.last_updated" as timestamp) as last_updated,
        cast(ingestion_timestamp as timestamp) as ingestion_timestamp
    from source_data
)

select * from renamed