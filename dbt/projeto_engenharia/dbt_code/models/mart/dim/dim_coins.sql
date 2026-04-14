select distinct
    coin_id,
    coin_name,
    symbol
from {{ ref('int_coins_cleaned') }}