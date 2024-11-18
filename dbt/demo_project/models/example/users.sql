{{
    config(
        materialized='table'
    )
}}

select
    "UserId" as user_id,
    "FirstName" as first_name,
    "LastName" as last_name,
    "EmailAddress" as email_address,
    "CreatedAt" as created_at
from {{ source('raw_data', 'mysql_users') }}