# SQL Queries Reference Guide - Superstore Analysis

## Table of Contents
1. [Basic Filtering (WHERE)](#basic-filtering)
2. [Aggregations (GROUP BY)](#aggregations)
3. [Business Use Cases](#business-use-cases)
4. [Data Quality Checks](#data-quality)

---

## Basic Filtering (WHERE)

### Query 1: Sales in Specific Region with High Sales
```sql
SELECT "Order ID", "Customer Name", Category, Sales, Profit
FROM superstore
WHERE Region = 'West' AND Sales > 100
LIMIT 10;
```
**Use Case**: Find high-value orders in a specific region
**Result**: 10 records from West region with sales > $100

---

### Query 2: Category-Based Filtering by State
```sql
SELECT "Order ID", "Customer Name", State, Sales, Quantity, Profit
FROM superstore
WHERE Category = 'Furniture' AND State IN ('CA', 'TX')
LIMIT 10;
```
**Use Case**: Analyze specific category sales by state
**Result**: Find all furniture sales in California and Texas

---

### Query 3: Orders with Discounts
```sql
SELECT "Order ID", "Product Name", Sales, Discount, Profit
FROM superstore
WHERE Discount > 0
ORDER BY Discount DESC
LIMIT 10;
```
**Use Case**: Identify heavily discounted products (risk analysis)
**Result**: Top 10 most discounted orders
**Insight**: High discounts often lead to losses

---

### Query 4: Loss-Making Orders
```sql
SELECT "Order ID", "Customer Name", "Product Name", Sales, Profit
FROM superstore
WHERE Profit < 0
ORDER BY Profit ASC
LIMIT 10;
```
**Use Case**: Identify unprofitable transactions for investigation
**Result**: Worst performing 10 orders
**Key Finding**: Some orders have losses up to -$6,599.98

---

## Aggregations (GROUP BY)

### Query 5: Regional Performance Summary
```sql
SELECT 
    Region,
    COUNT(*) as Order_Count,
    ROUND(SUM(Sales), 2) as Total_Sales,
    ROUND(AVG(Sales), 2) as Avg_Sales,
    ROUND(SUM(Profit), 2) as Total_Profit,
    ROUND(AVG(Profit), 2) as Avg_Profit
FROM superstore
GROUP BY Region
ORDER BY Total_Sales DESC;
```
**Result**:
```
Region  | Order_Count | Total_Sales | Avg_Sales | Total_Profit | Avg_Profit
West    | 3203        | 725457.82   | 226.49    | 108418.45    | 33.85
East    | 2848        | 678781.24   | 238.34    | 91522.78     | 32.14
Central | 2323        | 501239.89   | 215.77    | 39706.36     | 17.09
South   | 1620        | 391721.91   | 241.80    | 46749.43     | 28.86
```

---

### Query 6: Category Performance Analysis
```sql
SELECT 
    Category,
    COUNT(*) as Items_Sold,
    ROUND(SUM(Quantity), 2) as Total_Quantity,
    ROUND(SUM(Sales), 2) as Total_Sales,
    ROUND(AVG(Sales), 2) as Avg_Sale_Value,
    ROUND(SUM(Profit), 2) as Total_Profit,
    ROUND(100.0 * SUM(Profit) / SUM(Sales), 2) as Profit_Margin_Percent
FROM superstore
GROUP BY Category
ORDER BY Total_Sales DESC;
```
**Result**:
```
Category        | Items_Sold | Total_Sales | Profit_Margin
Technology      | 1847       | 836154.03   | 17.40%
Furniture       | 2121       | 741999.80   | 2.49%  ⚠️
Office Supplies | 6026       | 719047.03   | 17.04%
```

---

### Query 7: Customer Segment Analysis
```sql
SELECT 
    Segment,
    COUNT(DISTINCT "Customer ID") as Unique_Customers,
    COUNT(*) as Total_Orders,
    ROUND(SUM(Sales), 2) as Total_Sales,
    ROUND(AVG(Sales), 2) as Avg_Order_Value,
    ROUND(SUM(Profit), 2) as Total_Profit
FROM superstore
GROUP BY Segment
ORDER BY Total_Sales DESC;
```
**Result**: Consumer > Corporate > Home Office

---

### Query 8: Shipping Mode Performance
```sql
SELECT 
    "Ship Mode",
    COUNT(*) as Orders,
    ROUND(SUM(Sales), 2) as Total_Sales,
    ROUND(AVG(Sales), 2) as Avg_Sales,
    ROUND(SUM(Profit), 2) as Total_Profit
FROM superstore
GROUP BY "Ship Mode"
ORDER BY Total_Sales DESC;
```
**Result**: Standard Class dominates (59.7% of orders)

---

## Top Products & Categories (LIMIT & ORDER BY)

### Query 9: Top 10 Products by Sales
```sql
SELECT 
    "Product Name",
    Category,
    "Sub-Category",
    COUNT(*) as Order_Count,
    ROUND(SUM(Sales), 2) as Total_Sales,
    ROUND(AVG(Sales), 2) as Avg_Sale
FROM superstore
GROUP BY "Product Name"
ORDER BY Total_Sales DESC
LIMIT 10;
```
**Key Finding**: Canon Copier is #1 with $61,599.82 in sales

---

### Query 10: Top 10 Sub-Categories by Profit
```sql
SELECT 
    "Sub-Category",
    Category,
    COUNT(*) as Items_Sold,
    ROUND(SUM(Sales), 2) as Total_Sales,
    ROUND(SUM(Profit), 2) as Total_Profit,
    ROUND(100.0 * SUM(Profit) / SUM(Sales), 2) as Profit_Margin
FROM superstore
GROUP BY "Sub-Category"
ORDER BY Total_Profit DESC
LIMIT 10;
```
**Key Finding**: Copiers ($55,617.82) and Phones ($44,515.73) are profit drivers

---

### Query 11: Bottom 10 Sub-Categories (Problem Areas)
```sql
SELECT 
    "Sub-Category",
    Category,
    COUNT(*) as Items_Sold,
    ROUND(SUM(Sales), 2) as Total_Sales,
    ROUND(SUM(Profit), 2) as Total_Profit,
    ROUND(100.0 * SUM(Profit) / SUM(Sales), 2) as Profit_Margin
FROM superstore
GROUP BY "Sub-Category"
ORDER BY Total_Profit ASC
LIMIT 10;
```
**CRITICAL**: Tables lose $17,725.48 (negative 8.56% margin)

---

### Query 12: Top 10 Customers by Sales
```sql
SELECT 
    "Customer ID",
    "Customer Name",
    Segment,
    COUNT(*) as Order_Count,
    ROUND(SUM(Sales), 2) as Total_Sales,
    ROUND(SUM(Profit), 2) as Total_Profit
FROM superstore
GROUP BY "Customer ID"
ORDER BY Total_Sales DESC
LIMIT 10;
```
**Alert**: Top customer (Sean Miller) has negative profit!

---

## Business Use Cases

### Query 13: Monthly Sales Trends
```sql
SELECT 
    strftime('%Y-%m', "Order Date") as YearMonth,
    ROUND(SUM(Sales), 2) as Monthly_Sales,
    ROUND(SUM(Profit), 2) as Monthly_Profit,
    ROUND(AVG(Sales), 2) as Avg_Order_Value,
    COUNT(*) as Order_Count
FROM superstore
GROUP BY YearMonth
ORDER BY YearMonth;
```
**Use Case**: Identify seasonal patterns
**Pattern**: Nov-Dec show 50%+ higher sales than Jun-Jul

---

### Query 14: Profitability Matrix (Region × Segment)
```sql
SELECT 
    Region,
    Segment,
    COUNT(*) as Orders,
    ROUND(SUM(Sales), 2) as Total_Sales,
    ROUND(SUM(Profit), 2) as Total_Profit,
    ROUND(100.0 * SUM(Profit) / SUM(Sales), 2) as Profit_Margin
FROM superstore
GROUP BY Region, Segment
ORDER BY Total_Profit DESC;
```
**Result**: Best combination is West + Consumer (15.83% margin)

---

### Query 15: High-Value Customers (HAVING Clause)
```sql
SELECT 
    "Customer ID",
    "Customer Name",
    Segment,
    City,
    State,
    COUNT(*) as Purchase_Frequency,
    ROUND(SUM(Sales), 2) as Lifetime_Sales,
    ROUND(SUM(Profit), 2) as Lifetime_Profit,
    ROUND(AVG(Sales), 2) as Avg_Order_Value
FROM superstore
GROUP BY "Customer ID"
HAVING SUM(Sales) > 2000
ORDER BY Lifetime_Sales DESC
LIMIT 10;
```
**Use Case**: Identify VIP customers for retention programs
**Note**: HAVING filters after GROUP BY (unlike WHERE which filters before)

---

### Query 16: At-Risk Products (High Discounts)
```sql
SELECT 
    "Sub-Category",
    "Product Name",
    COUNT(*) as Discounted_Orders,
    ROUND(AVG(Discount), 2) as Avg_Discount,
    ROUND(SUM(Sales), 2) as Total_Sales,
    ROUND(SUM(Profit), 2) as Total_Profit,
    ROUND(100.0 * SUM(Profit) / SUM(Sales), 2) as Profit_Margin
FROM superstore
WHERE Discount > 0.2
GROUP BY "Product Name"
ORDER BY Avg_Discount DESC
LIMIT 15;
```
**Critical Finding**: 80% discounts are destroying profitability

---

### Query 17: Regional Deep Dive
```sql
SELECT 
    Region,
    Category,
    ROUND(SUM(Sales), 2) as Total_Sales,
    COUNT(*) as Orders,
    ROUND(SUM(Profit), 2) as Total_Profit
FROM superstore
GROUP BY Region, Category
ORDER BY Region, Total_Sales DESC;
```
**Use Case**: Understand category performance by region

---

### Query 18: Order Value Distribution (CASE Statement)
```sql
SELECT 
    CASE 
        WHEN Sales < 50 THEN 'Under $50'
        WHEN Sales < 100 THEN '$50-$100'
        WHEN Sales < 250 THEN '$100-$250'
        WHEN Sales < 500 THEN '$250-$500'
        ELSE 'Over $500'
    END as Price_Range,
    COUNT(*) as Order_Count,
    ROUND(SUM(Sales), 2) as Total_Sales,
    ROUND(AVG(Sales), 2) as Avg_Sale,
    ROUND(SUM(Profit), 2) as Total_Profit
FROM superstore
GROUP BY Price_Range
ORDER BY CASE 
    WHEN Price_Range = 'Under $50' THEN 1
    WHEN Price_Range = '$50-$100' THEN 2
    WHEN Price_Range = '$100-$250' THEN 3
    WHEN Price_Range = '$250-$500' THEN 4
    ELSE 5
END;
```
**Result**: Most profit comes from high-value orders (>$500)

---

## Data Quality Checks

### Query 19: Row Count Validation
```sql
SELECT COUNT(*) as Total_Rows FROM superstore;
```
**Result**: 9,994 rows ✓

---

### Query 20: Unique Values Count
```sql
SELECT 
    COUNT(DISTINCT "Customer ID") as Unique_Customers,
    COUNT(DISTINCT "Order ID") as Unique_Orders,
    COUNT(DISTINCT "Product ID") as Unique_Products,
    COUNT(DISTINCT Region) as Regions,
    COUNT(DISTINCT Segment) as Segments,
    COUNT(DISTINCT Category) as Categories
FROM superstore;
```
**Result**: 793 customers, 5,009 orders, 1,862 products

---

### Query 21: Date Range Check
```sql
SELECT 
    MIN("Order Date") as Earliest_Order,
    MAX("Order Date") as Latest_Order,
    julianday(MAX("Order Date")) - julianday(MIN("Order Date")) as Days_Span
FROM superstore;
```
**Result**: 1,457 days (4 years of data)

---

### Query 22: Duplicate Orders Detection
```sql
SELECT 
    "Order ID",
    COUNT(*) as Occurrence_Count,
    COUNT(DISTINCT "Row ID") as Unique_Items,
    ROUND(SUM(Sales), 2) as Total_Amount
FROM superstore
GROUP BY "Order ID"
HAVING COUNT(*) > 1
ORDER BY Occurrence_Count DESC
LIMIT 20;
```
**Result**: This is normal - orders can have multiple line items

---

### Query 23: Data Completeness Check
```sql
SELECT 
    COUNT(*) as Total_Records,
    COUNT(CASE WHEN Sales IS NULL THEN 1 END) as Null_Sales,
    COUNT(CASE WHEN Profit IS NULL THEN 1 END) as Null_Profit,
    COUNT(CASE WHEN "Customer ID" IS NULL THEN 1 END) as Null_Customer_ID
FROM superstore;
```
**Result**: Zero nulls - data is complete ✓

---

### Query 24: Data Integrity Check
```sql
SELECT 
    COUNT(CASE WHEN Sales < 0 THEN 1 END) as Negative_Sales,
    COUNT(CASE WHEN Quantity < 0 THEN 1 END) as Negative_Quantity,
    COUNT(CASE WHEN Discount < 0 OR Discount > 1 THEN 1 END) as Invalid_Discount,
    COUNT(CASE WHEN Profit < -1000 THEN 1 END) as Extreme_Loss_Orders
FROM superstore;
```
**Result**: 22 extreme losses detected (review for data quality)

---

## SQL Techniques Summary

| Technique | Purpose | Example |
|-----------|---------|---------|
| **WHERE** | Filter rows before grouping | `WHERE Region = 'West'` |
| **GROUP BY** | Aggregate by dimension | `GROUP BY Category` |
| **HAVING** | Filter groups after aggregation | `HAVING SUM(Sales) > 1000` |
| **ORDER BY** | Sort results | `ORDER BY Profit DESC` |
| **LIMIT** | Restrict row count | `LIMIT 10` |
| **DISTINCT** | Get unique values | `COUNT(DISTINCT Customer_ID)` |
| **CASE** | Conditional logic | `CASE WHEN Sales > 500...` |
| **ROUND** | Format decimals | `ROUND(SUM(Sales), 2)` |
| **Date Functions** | Work with dates | `strftime('%Y-%m', Order_Date)` |
| **String Functions** | String operations | Column names in quotes: `"Order Date"` |

---

## Key SQL Learnings

1. **Always quote column names with spaces**: Use `"Order ID"` not `Order_ID`
2. **Use HAVING for post-aggregation filters**: Filter groups, not individual rows
3. **CASE for bucketing**: Create custom categories like price ranges
4. **Date formatting**: Use `strftime()` in SQLite for date operations
5. **Profitability = Profit / Sales * 100**: Calculate margins explicitly

---

**Document Version**: 1.0
**Last Updated**: June 2025
**Analysis Tool**: Python + SQLite
