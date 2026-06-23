-- Hotel BI Platform - Analytics Query Pack

-- 1. Revenue by month
SELECT
    d.date_year,
    d.date_month,
    d.month_name,
    SUM(f.revenue) AS total_revenue
FROM fact_revenue f
JOIN dim_date d ON f.date_id = d.date_id
GROUP BY d.date_year, d.date_month, d.month_name
ORDER BY d.date_year, d.date_month;

-- 2. Revenue by service
SELECT
    s.service_category,
    s.service_name,
    SUM(f.revenue) AS total_revenue,
    COUNT(*) AS transaction_count
FROM fact_revenue f
JOIN dim_service s ON f.service_id = s.service_id
GROUP BY s.service_category, s.service_name
ORDER BY total_revenue DESC;

-- 3. Top customers
SELECT
    c.customer_name,
    SUM(f.revenue) AS total_revenue,
    COUNT(*) AS transaction_count
FROM fact_revenue f
JOIN dim_customer c ON f.customer_id = c.customer_id
GROUP BY c.customer_name
ORDER BY total_revenue DESC
LIMIT 10;

-- 4. Revenue trend by day
SELECT
    d.full_date,
    SUM(f.revenue) AS daily_revenue,
    SUM(SUM(f.revenue)) OVER (ORDER BY d.full_date) AS cumulative_revenue
FROM fact_revenue f
JOIN dim_date d ON f.date_id = d.date_id
GROUP BY d.full_date
ORDER BY d.full_date;

-- 5. Customer count
SELECT
    COUNT(*) AS customer_count
FROM dim_customer;

-- 6. Customer segmentation by total revenue
WITH customer_revenue AS (
    SELECT
        c.customer_id,
        c.customer_name,
        SUM(f.revenue) AS total_revenue,
        COUNT(*) AS transaction_count
    FROM fact_revenue f
    JOIN dim_customer c ON f.customer_id = c.customer_id
    GROUP BY c.customer_id, c.customer_name
)
SELECT
    customer_name,
    total_revenue,
    transaction_count,
    CASE
        WHEN total_revenue >= 1000 THEN 'VIP'
        WHEN total_revenue >= 500 THEN 'High Value'
        WHEN total_revenue >= 100 THEN 'Regular'
        ELSE 'Low Value'
    END AS customer_segment
FROM customer_revenue
ORDER BY total_revenue DESC;

-- 7. Average revenue per customer
SELECT
    ROUND(SUM(revenue) / NULLIF(COUNT(DISTINCT customer_id), 0), 2) AS average_revenue_per_customer
FROM fact_revenue;

-- 8. Average transaction value by service category
SELECT
    s.service_category,
    ROUND(AVG(f.revenue), 2) AS average_transaction_value
FROM fact_revenue f
JOIN dim_service s ON f.service_id = s.service_id
GROUP BY s.service_category
ORDER BY average_transaction_value DESC;
