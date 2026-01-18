-- Test: Ensure views and forwards are non-negative
WITH negative_metrics AS (
    SELECT 
        message_id,
        channel_name,
        views,
        forwards
    FROM {{ ref('stg_telegram_messages') }}
    WHERE views < 0 OR forwards < 0
)

SELECT 
    COUNT(*) as negative_metrics_count
FROM negative_metrics
HAVING COUNT(*) > 0
