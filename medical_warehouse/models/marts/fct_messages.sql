{{ config(materialized='table', schema='marts') }}

SELECT
    CONCAT(channel_name, '_', message_id) as message_key,
    channel_name,
    message_id,
    message_text,
    message_timestamp,
    views,
    forwards
FROM dbt_staging.stg_telegram_messages  -- Use the actual schema
WHERE message_timestamp IS NOT NULL
