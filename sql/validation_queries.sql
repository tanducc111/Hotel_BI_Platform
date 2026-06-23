-- Hotel BI Platform - Validation Query Pack

-- Row counts for each warehouse table
SELECT 'dim_customer' AS table_name, COUNT(*) AS row_count FROM dim_customer
UNION ALL
SELECT 'dim_service' AS table_name, COUNT(*) AS row_count FROM dim_service
UNION ALL
SELECT 'dim_date' AS table_name, COUNT(*) AS row_count FROM dim_date
UNION ALL
SELECT 'fact_revenue' AS table_name, COUNT(*) AS row_count FROM fact_revenue
ORDER BY table_name;

-- Revenue sanity check
SELECT
    COUNT(*) AS fact_rows,
    COUNT(DISTINCT source_system || ':' || source_record_id) AS distinct_source_records,
    SUM(revenue) AS total_revenue,
    MIN(revenue) AS min_revenue,
    MAX(revenue) AS max_revenue
FROM fact_revenue;

-- Duplicate checks; every result should return zero rows
SELECT customer_name, COUNT(*) AS duplicate_count
FROM dim_customer
GROUP BY customer_name
HAVING COUNT(*) > 1;

SELECT service_category, service_name, COUNT(*) AS duplicate_count
FROM dim_service
GROUP BY service_category, service_name
HAVING COUNT(*) > 1;

SELECT full_date, COUNT(*) AS duplicate_count
FROM dim_date
GROUP BY full_date
HAVING COUNT(*) > 1;

SELECT source_system, source_record_id, COUNT(*) AS duplicate_count
FROM fact_revenue
GROUP BY source_system, source_record_id
HAVING COUNT(*) > 1;

-- Constraint inventory
SELECT
    tc.table_name,
    tc.constraint_name,
    tc.constraint_type
FROM information_schema.table_constraints tc
WHERE tc.table_schema = 'public'
  AND tc.table_name IN ('dim_customer', 'dim_service', 'dim_date', 'fact_revenue')
ORDER BY tc.table_name, tc.constraint_type, tc.constraint_name;

-- Foreign key health check; every count should be zero
SELECT
    SUM(CASE WHEN c.customer_id IS NULL THEN 1 ELSE 0 END) AS missing_customer_fk,
    SUM(CASE WHEN s.service_id IS NULL THEN 1 ELSE 0 END) AS missing_service_fk,
    SUM(CASE WHEN d.date_id IS NULL THEN 1 ELSE 0 END) AS missing_date_fk
FROM fact_revenue f
LEFT JOIN dim_customer c ON f.customer_id = c.customer_id
LEFT JOIN dim_service s ON f.service_id = s.service_id
LEFT JOIN dim_date d ON f.date_id = d.date_id;
