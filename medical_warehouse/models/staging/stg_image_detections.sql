{{
    config(
        materialized='table',
        unique_key='detection_hash'
    )
}}

WITH raw_detections AS (
    SELECT 
        *,
        -- Create a unique hash for each detection
        MD5(
            CONCAT(
                image_path, 
                detected_class, 
                CAST(confidence AS VARCHAR),
                CAST(x_center AS VARCHAR),
                CAST(y_center AS VARCHAR)
            )
        ) as detection_hash
    FROM {{ source('enrichment', 'raw_image_detections') }}
),

enriched_detections AS (
    SELECT
        rd.detection_hash,
        rd.image_path,
        rd.image_name,
        rd.channel_name,
        rd.date_str,
        rd.detected_class,
        rd.confidence,
        rd.x_center,
        rd.y_center,
        rd.box_width,
        rd.box_height,
        rd.original_width,
        rd.original_height,
        rd.processed_at,
        -- Extract channel from path and match with dim_channels
        CASE 
            WHEN rd.channel_name LIKE '%chemed%' THEN 'chemed123'
            WHEN rd.channel_name LIKE '%lobelia%' THEN 'lobelia4cosmetics'
            WHEN rd.channel_name LIKE '%tikvah%' THEN 'tikvahpharma'
            ELSE LOWER(rd.channel_name)
        END as normalized_channel_name,
        -- Parse date string
        CASE 
            WHEN rd.date_str != 'unknown' AND rd.date_str ~ '^\d{4}-\d{2}-\d{2}$' 
            THEN rd.date_str::DATE
            ELSE NULL
        END as detection_date
    FROM raw_detections rd
)

SELECT
    ed.detection_hash,
    ed.image_path,
    ed.image_name,
    ed.normalized_channel_name as channel_name,
    ed.detected_class,
    ed.confidence,
    ed.x_center,
    ed.y_center,
    ed.box_width,
    ed.box_height,
    ed.original_width,
    ed.original_height,
    ed.detection_date,
    ed.processed_at,
    -- Join with dim_channels
    COALESCE(dc.channel_key, -1) as channel_key,
    -- Join with dim_dates
    COALESCE(dd.date_key, -1) as date_key
FROM enriched_detections ed
LEFT JOIN {{ ref('dim_channels') }} dc 
    ON ed.normalized_channel_name = dc.channel_name
LEFT JOIN {{ ref('dim_dates') }} dd 
    ON ed.detection_date = dd.full_date
