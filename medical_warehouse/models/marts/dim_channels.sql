{{ config(materialized='table', schema='marts') }}

SELECT DISTINCT
    channel_name,
    COUNT(*) as message_count
FROM dbt_staging.stg_telegram_messages  -- Use the actual schema
GROUP BY channel_name
