{{
    config(
        materialized='table',
        unique_key='object_key'
    )
}}

WITH detected_objects AS (
    SELECT DISTINCT
        detected_class,
        CASE 
            WHEN detected_class IN ('medicine', 'pill', 'syringe', 'medical_device') 
            THEN 'medical'
            WHEN detected_class IN ('cosmetic', 'cream', 'ointment', 'bottle', 'box', 'package')
            THEN 'cosmetic'
            ELSE 'other'
        END as object_category,
        CASE 
            WHEN detected_class IN ('bottle', 'box', 'package') 
            THEN 'packaging'
            WHEN detected_class IN ('medicine', 'pill', 'syringe')
            THEN 'product'
            WHEN detected_class IN ('cream', 'ointment')
            THEN 'topical'
            ELSE 'miscellaneous'
        END as object_type
    FROM {{ ref('stg_image_detections') }}
)

SELECT
    MD5(detected_class) as object_key,
    detected_class as object_name,
    object_category,
    object_type,
    CURRENT_TIMESTAMP as created_at
FROM detected_objects
