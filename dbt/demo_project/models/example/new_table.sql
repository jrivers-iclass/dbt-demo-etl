{{
    config(
        materialized='table'
    )
}}

select
    "something_special" as "key",
    "something_bad" as "enabled" 
from {{ source('raw_data', 'mysql_weirdtable') }}