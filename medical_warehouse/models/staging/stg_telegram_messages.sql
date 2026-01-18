{{ config(materialized='view', schema='staging') }}

SELECT 
    id as raw_id,
    channel_name,
    message_id,
    message_text,
    message_date::timestamp as message_timestamp,
    COALESCE(views, 0) as views,
    COALESCE(forwards, 0) as forwards,
    media_path,
    scraped_at
FROM raw_telegram.telegram_messages
