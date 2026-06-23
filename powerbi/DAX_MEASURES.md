# DAX Measures

Create a measure table named `Measures`, then add these measures.

## Total Revenue

```DAX
Total Revenue =
SUM ( fact_revenue[revenue] )
```

## Total Customers

```DAX
Total Customers =
DISTINCTCOUNT ( dim_customer[customer_id] )
```

## Total Transactions

```DAX
Total Transactions =
COUNTROWS ( fact_revenue )
```

## Average Revenue

```DAX
Average Revenue =
AVERAGE ( fact_revenue[revenue] )
```

## Average Revenue Per Customer

```DAX
Average Revenue Per Customer =
DIVIDE ( [Total Revenue], [Total Customers] )
```

## Revenue Growth %

```DAX
Revenue Growth % =
VAR CurrentRevenue =
    [Total Revenue]
VAR PreviousRevenue =
    CALCULATE (
        [Total Revenue],
        DATEADD ( dim_date[full_date], -1, MONTH )
    )
RETURN
    DIVIDE ( CurrentRevenue - PreviousRevenue, PreviousRevenue )
```

## Customer Contribution %

```DAX
Customer Contribution % =
DIVIDE (
    [Total Revenue],
    CALCULATE ( [Total Revenue], ALL ( dim_customer ) )
)
```

## Formatting

| Measure | Format |
| --- | --- |
| `[Total Revenue]` | Currency |
| `[Average Revenue]` | Currency |
| `[Average Revenue Per Customer]` | Currency |
| `[Revenue Growth %]` | Percentage |
| `[Customer Contribution %]` | Percentage |
