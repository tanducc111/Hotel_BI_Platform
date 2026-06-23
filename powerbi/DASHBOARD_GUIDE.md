# Power BI Dashboard Guide

## Page 1: Executive Revenue Overview

Recommended visuals:

| Visual | Fields / Measures | Purpose |
| --- | --- | --- |
| KPI card | `[Total Revenue]` | Shows total validated revenue |
| KPI card | `[Total Customers]` | Shows unique customers |
| KPI card | `[Total Transactions]` | Shows revenue transaction count |
| KPI card | `[Average Revenue]` | Shows average transaction value |
| Line chart | `dim_date[full_date]`, `[Total Revenue]` | Shows revenue trend over time |
| Bar chart | `dim_service[service_category]`, `[Total Revenue]` | Compares revenue by business line |

Screenshot placeholder:

```text
screenshots/powerbi_overview.png
```

## Page 2: Customer Analytics

Recommended visuals:

| Visual | Fields / Measures | Purpose |
| --- | --- | --- |
| Table | `dim_customer[customer_name]`, `[Total Revenue]`, `[Customer Contribution %]` | Ranks customer contribution |
| Bar chart | `dim_customer[customer_name]`, `[Total Revenue]` | Identifies top customers |
| KPI card | `[Average Revenue Per Customer]` | Shows customer-level revenue productivity |

Screenshot placeholder:

```text
screenshots/powerbi_customers.png
```

## Page 3: Service Performance

Recommended visuals:

| Visual | Fields / Measures | Purpose |
| --- | --- | --- |
| Matrix | `dim_service[service_category]`, `dim_service[service_name]`, `[Total Revenue]`, `[Total Transactions]` | Compares detailed service revenue |
| Bar chart | `dim_service[service_name]`, `[Average Revenue]` | Finds high-value services |
| Slicer | `dim_service[service_category]` | Filters dashboard by business line |

Screenshot placeholder:

```text
screenshots/powerbi_services.png
```

## Suggested Slicers

- `dim_date[full_date]`
- `dim_service[service_category]`
- `dim_customer[customer_name]`
- `fact_revenue[source_system]`

## QA Checklist

- Revenue total in Power BI matches SQL `SUM(fact_revenue.revenue)`.
- Customer count in Power BI matches SQL `COUNT(*) FROM dim_customer`.
- Transaction count in Power BI matches SQL `COUNT(*) FROM fact_revenue`.
- Date slicer filters all revenue visuals.
- Service slicer filters both revenue and customer tables.
