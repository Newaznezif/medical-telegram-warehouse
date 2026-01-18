{{ config(materialized='table', schema='marts') }}

SELECT DISTINCT
    DATE(message_timestamp) as date_key,
    COUNT(*) as message_count
FROM dbt_staging.stg_telegram_messages  -- Use the actual schema
WHERE message_timestamp IS NOT NULL
GROUP BY DATE(message_timestamp)
