# Power BI Data Model

## Tables

Import these PostgreSQL tables from database `hotel_dw`:

| Table | Role | Grain |
| --- | --- | --- |
| `fact_revenue` | Fact table | One validated revenue transaction per source system and source record |
| `dim_customer` | Dimension | One row per unique customer name |
| `dim_service` | Dimension | One row per service category and service name |
| `dim_date` | Dimension | One row per transaction date |

## Relationships

Create one-to-many relationships from dimensions to the fact table:

| From | To | Cardinality | Cross-filter |
| --- | --- | --- | --- |
| `dim_customer[customer_id]` | `fact_revenue[customer_id]` | One-to-many | Single |
| `dim_service[service_id]` | `fact_revenue[service_id]` | One-to-many | Single |
| `dim_date[date_id]` | `fact_revenue[date_id]` | One-to-many | Single |

Mark `dim_date` as the date table and use `dim_date[full_date]` as the date column.

## Recommended Fields

Use these fields in report visuals:

| Business Area | Fields |
| --- | --- |
| Revenue | `fact_revenue[revenue]`, `dim_date[full_date]`, `dim_date[month_name]`, `dim_date[date_month]` |
| Customer | `dim_customer[customer_name]`, `dim_customer[customer_type]` |
| Service | `dim_service[service_category]`, `dim_service[service_name]` |
| Transaction audit | `fact_revenue[source_system]`, `fact_revenue[source_record_id]`, `fact_revenue[loaded_at]` |

## Model Notes

- Keep `fact_revenue` hidden except measures and audit fields needed by analysts.
- Sort `dim_date[month_name]` by `dim_date[date_month]`.
- Use `dim_date[full_date]` for trend visuals.
- Use Import mode for a portfolio dashboard; DirectQuery is optional for larger datasets.
