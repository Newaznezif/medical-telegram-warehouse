-- Test: Ensure no messages have future dates
WITH future_messages AS (
    SELECT 
        message_id,
        channel_name,
        message_timestamp
    FROM {{ ref('stg_telegram_messages') }}
    WHERE message_timestamp > CURRENT_TIMESTAMP
)

SELECT 
    COUNT(*) as future_message_count
FROM future_messages
HAVING COUNT(*) > 0
