{{
    config(
        materialized='table',
        unique_key='detection_id',
        tags=['yolo', 'image_detections']
    )
}}

WITH detection_metrics AS (
    SELECT
        -- Create a deterministic ID for each unique detection
        MD5(
            CONCAT(
                channel_key::VARCHAR,
                date_key::VARCHAR,
                detected_class,
                CAST(FLOOR(confidence * 100) AS VARCHAR)
            )
        ) as detection_id,
        channel_key,
        date_key,
        detected_class,
        COUNT(*) as detection_count,
        COUNT(DISTINCT image_name) as unique_images_count,
        AVG(confidence) as avg_confidence,
        MIN(confidence) as min_confidence,
        MAX(confidence) as max_confidence,
        STDDEV(confidence) as confidence_stddev,
        AVG(x_center) as avg_x_center,
        AVG(y_center) as avg_y_center,
        AVG(box_width * box_height) as avg_box_area,
        -- Count by confidence levels
        SUM(CASE WHEN confidence >= 0.8 THEN 1 ELSE 0 END) as high_confidence_count,
        SUM(CASE WHEN confidence >= 0.5 AND confidence < 0.8 THEN 1 ELSE 0 END) as medium_confidence_count,
        SUM(CASE WHEN confidence < 0.5 THEN 1 ELSE 0 END) as low_confidence_count,
        MIN(processed_at) as first_detected_at,
        MAX(processed_at) as last_detected_at
    FROM {{ ref('stg_image_detections') }}
    WHERE channel_key != -1 AND date_key != -1
    GROUP BY 1, 2, 3, 4
),

detection_details AS (
    SELECT
        dm.detection_id,
        dm.channel_key,
        dm.date_key,
        dm.detected_class,
        dm.detection_count,
        dm.unique_images_count,
        dm.avg_confidence,
        dm.min_confidence,
        dm.max_confidence,
        dm.confidence_stddev,
        dm.avg_x_center,
        dm.avg_y_center,
        dm.avg_box_area,
        dm.high_confidence_count,
        dm.medium_confidence_count,
        dm.low_confidence_count,
        dm.first_detected_at,
        dm.last_detected_at,
        -- Calculate percentages
        ROUND(
            dm.high_confidence_count * 100.0 / NULLIF(dm.detection_count, 0), 
            2
        ) as high_confidence_percent,
        -- Detection frequency per image
        ROUND(
            dm.detection_count * 1.0 / NULLIF(dm.unique_images_count, 0), 
            2
        ) as detections_per_image,
        -- Add business context flags
        CASE 
            WHEN dm.detected_class IN ('medicine', 'pill', 'syringe', 'medical_device') 
            THEN 'medical'
            WHEN dm.detected_class IN ('cosmetic', 'cream', 'ointment', 'bottle')
            THEN 'cosmetic'
            ELSE 'other'
        END as product_category
    FROM detection_metrics dm
)

SELECT
    dd.detection_id,
    dc.channel_key,
    dc.channel_name,
    dd.date_key,
    dd.full_date,
    dd.detected_class,
    dd.product_category,
    dd.detection_count,
    dd.unique_images_count,
    dd.detections_per_image,
    dd.avg_confidence,
    dd.min_confidence,
    dd.max_confidence,
    dd.confidence_stddev,
    dd.avg_x_center,
    dd.avg_y_center,
    dd.avg_box_area,
    dd.high_confidence_count,
    dd.medium_confidence_count,
    dd.low_confidence_count,
    dd.high_confidence_percent,
    dd.first_detected_at,
    dd.last_detected_at,
    -- Add derived metrics
    ROUND(
        dd.detection_count * 100.0 / SUM(dd.detection_count) OVER (PARTITION BY dc.channel_key, dd.date_key), 
        2
    ) as daily_channel_percent,
    ROUND(
        dd.detection_count * 100.0 / SUM(dd.detection_count) OVER (PARTITION BY dd.detected_class), 
        2
    ) as class_distribution_percent
FROM detection_details dd
LEFT JOIN {{ ref('dim_channels') }} dc ON dd.channel_key = dc.channel_key
LEFT JOIN {{ ref('dim_dates') }} dd2 ON dd.date_key = dd2.date_key
