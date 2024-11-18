{{ config(
    materialized='table'
) }}

select
    "OrderId" as order_id,
    "UserId" as user_id,
    "ProductName" as product_name,
    "OrderAmount" as order_amount,
    "OrderDate" as order_date
from {{ source('raw_data', 'mysql_orderdetails') }}