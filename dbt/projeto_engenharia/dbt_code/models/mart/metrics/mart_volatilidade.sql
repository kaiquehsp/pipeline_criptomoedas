{{ config(materialized='view') }}

with preco_geral as (
    select 
        f.coin_id,
        d.coin_name,
        f.price_usd,
        f.ingestion_timestamp
    from {{ ref('fct_coins') }} as f
    join {{ ref('dim_coins') }} as d on f.coin_id = d.coin_id
),

preco_anterior as ( 
    select
        *,
        lag(price_usd, 1) over(
            partition by coin_id 
            order by ingestion_timestamp asc
        ) as price_usd_anterior,
        
        row_number() over(
            partition by coin_id 
            order by ingestion_timestamp desc
        ) as rank_temporal
    from preco_geral
),

calculo_variacao as (
    select 
        *,
        round(
            case 
                when price_usd_anterior is null or price_usd_anterior = 0 then 0
                else ((price_usd - price_usd_anterior) / price_usd_anterior) * 100
            end, 
        2) as variacao_percentual
    from preco_anterior
)

select 
    coin_id,
    coin_name,
    price_usd,
    ingestion_timestamp,
    price_usd_anterior,
    variacao_percentual,
    case
        when variacao_percentual > 0 then 'Alta'
        when variacao_percentual < 0 then 'Baixa'
        else 'Estavel'
    end as tendencia
from calculo_variacao
where rank_temporal = 1