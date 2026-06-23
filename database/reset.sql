DROP TABLE IF EXISTS fact_revenue CASCADE;
DROP TABLE IF EXISTS dim_date CASCADE;
DROP TABLE IF EXISTS dim_service CASCADE;
DROP TABLE IF EXISTS dim_customer CASCADE;

CREATE TABLE dim_customer (
    customer_id BIGSERIAL PRIMARY KEY,
    customer_name VARCHAR(255) NOT NULL,
    customer_type VARCHAR(50) NOT NULL DEFAULT 'Regular',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_dim_customer_customer_name UNIQUE (customer_name)
);

CREATE TABLE dim_service (
    service_id BIGSERIAL PRIMARY KEY,
    service_category VARCHAR(100) NOT NULL,
    service_name VARCHAR(255) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_dim_service_category_name UNIQUE (service_category, service_name)
);

CREATE TABLE dim_date (
    date_id INTEGER PRIMARY KEY,
    full_date DATE NOT NULL,
    date_year SMALLINT NOT NULL,
    date_quarter SMALLINT NOT NULL,
    date_month SMALLINT NOT NULL,
    month_name VARCHAR(20) NOT NULL,
    date_day SMALLINT NOT NULL,
    day_name VARCHAR(20) NOT NULL,
    CONSTRAINT uq_dim_date_full_date UNIQUE (full_date)
);

CREATE TABLE fact_revenue (
    revenue_id BIGSERIAL PRIMARY KEY,
    source_system VARCHAR(50) NOT NULL,
    source_record_id VARCHAR(100) NOT NULL,
    customer_id BIGINT NOT NULL REFERENCES dim_customer(customer_id),
    service_id BIGINT NOT NULL REFERENCES dim_service(service_id),
    date_id INTEGER NOT NULL REFERENCES dim_date(date_id),
    revenue NUMERIC(12, 2) NOT NULL CHECK (revenue >= 0),
    loaded_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_fact_revenue_source_record UNIQUE (source_system, source_record_id)
);

CREATE INDEX idx_fact_revenue_customer_id ON fact_revenue(customer_id);
CREATE INDEX idx_fact_revenue_service_id ON fact_revenue(service_id);
CREATE INDEX idx_fact_revenue_date_id ON fact_revenue(date_id);
