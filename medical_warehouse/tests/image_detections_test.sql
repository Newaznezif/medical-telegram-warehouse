-- medical_warehouse/tests/image_detections_test.sql
-- Test 1: No future detections
SELECT 
    COUNT(*) as future_detections
FROM {{ ref('stg_image_detections') }}
WHERE processed_at > CURRENT_TIMESTAMP
HAVING COUNT(*) > 0

-- Test 2: Confidence scores are valid (0-1)
SELECT
    COUNT(*) as invalid_confidence
FROM {{ ref('stg_image_detections') }}
WHERE confidence < 0 OR confidence > 1
HAVING COUNT(*) > 0

-- Test 3: Bounding box coordinates are normalized (0-1)
SELECT
    COUNT(*) as invalid_coordinates
FROM {{ ref('stg_image_detections') }}
WHERE x_center < 0 OR x_center > 1
   OR y_center < 0 OR y_center > 1
   OR box_width < 0 OR box_width > 1
   OR box_height < 0 OR box_height > 1
HAVING COUNT(*) > 0

-- Test 4: No duplicate detection hashes
SELECT
    detection_hash,
    COUNT(*) as duplicate_count
FROM {{ ref('stg_image_detections') }}
GROUP BY detection_hash
HAVING COUNT(*) > 1

-- Test 5: Valid channel references
SELECT
    COUNT(*) as invalid_channel_references
FROM {{ ref('stg_image_detections') }}
WHERE channel_key = -1
HAVING COUNT(*) > 0

-- Test 6: Valid date references
SELECT
    COUNT(*) as invalid_date_references
FROM {{ ref('stg_image_detections') }}
WHERE date_key = -1 AND detection_date IS NOT NULL
HAVING COUNT(*) > 0
