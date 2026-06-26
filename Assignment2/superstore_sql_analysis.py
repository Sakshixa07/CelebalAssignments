"""
Superstore Sales Data Analysis using SQL
==========================================
Objective: Analyze sales data using SQL with filtering, aggregation, and business queries
Dataset: 9,994 rows x 21 columns
"""

import sqlite3
import pandas as pd
import numpy as np
from datetime import datetime

# ============================================================================
# STEP 1: Load Dataset into SQL Database
# ============================================================================

print("=" * 80)
print("STEP 1: LOADING DATA INTO SQL DATABASE")
print("=" * 80)

# Read CSV file
csv_file = '/mnt/user-data/uploads/Sample_-_Superstore.csv'
df = pd.read_csv(csv_file, encoding='latin-1')

# Convert date columns to datetime
df['Order Date'] = pd.to_datetime(df['Order Date'])
df['Ship Date'] = pd.to_datetime(df['Ship Date'])

# Create SQL database
conn = sqlite3.connect(':memory:')
cursor = conn.cursor()

# Create table and insert data
df.to_sql('superstore', conn, if_exists='replace', index=False)
print(f"✓ Loaded {len(df)} rows into 'superstore' table")

# ============================================================================
# STEP 2: Explore Table Schema and Sample Data
# ============================================================================

print("\n" + "=" * 80)
print("STEP 2: TABLE SCHEMA & SAMPLE DATA")
print("=" * 80)

# Get schema
schema_query = "PRAGMA table_info(superstore);"
schema_df = pd.read_sql_query(schema_query, conn)
print("\nTable Schema:")
print(schema_df.to_string(index=False))

# Get sample data
print("\n\nSample Data (First 5 rows):")
sample_query = 'SELECT * FROM superstore LIMIT 5;'
sample_df = pd.read_sql_query(sample_query, conn)
print(sample_df.to_string())

# ============================================================================
# STEP 3: WHERE Filters (Region, Category, Date, Sales)
# ============================================================================

print("\n" + "=" * 80)
print("STEP 3: WHERE FILTERS (REGION, CATEGORY, DATE, SALES)")
print("=" * 80)

# Query 3.1: Sales in West Region with High Sales (> $100)
print("\n[3.1] Sales in West Region with Sales > $100:")
q3_1 = 'SELECT "Order ID", "Customer Name", Category, Sales, Profit FROM superstore WHERE Region = "West" AND Sales > 100 LIMIT 10;'
result = pd.read_sql_query(q3_1, conn)
print(f"Found {len(result)} records")
print(result.to_string(index=False))

# Query 3.2: Furniture Category in specific states
print("\n\n[3.2] Furniture Sales in California and Texas:")
q3_2 = 'SELECT "Order ID", "Customer Name", State, Sales, Quantity, Profit FROM superstore WHERE Category = "Furniture" AND State IN ("CA", "TX") LIMIT 10;'
result = pd.read_sql_query(q3_2, conn)
print(f"Found {len(result)} records")
print(result.to_string(index=False))

# Query 3.3: Orders with Discount > 0
print("\n\n[3.3] Discounted Orders (Discount > 0):")
q3_3 = 'SELECT "Order ID", "Product Name", Sales, Discount, Profit FROM superstore WHERE Discount > 0 ORDER BY Discount DESC LIMIT 10;'
result = pd.read_sql_query(q3_3, conn)
print(f"Found {len(result)} records")
print(result.to_string(index=False))

# Query 3.4: Loss-making orders (Negative Profit)
print("\n\n[3.4] Loss-Making Orders (Profit < 0):")
q3_4 = 'SELECT "Order ID", "Customer Name", "Product Name", Sales, Profit FROM superstore WHERE Profit < 0 ORDER BY Profit ASC LIMIT 10;'
result = pd.read_sql_query(q3_4, conn)
print(f"Found {len(result)} records")
print(result.to_string(index=False))

# ============================================================================
# STEP 4: GROUP BY Aggregations (Sales, Quantity, Averages)
# ============================================================================

print("\n" + "=" * 80)
print("STEP 4: GROUP BY AGGREGATIONS")
print("=" * 80)

# Query 4.1: Sales by Region
print("\n[4.1] Total Sales, Avg Sales, and Order Count by Region:")
q4_1 = 'SELECT Region, COUNT(*) as Order_Count, ROUND(SUM(Sales), 2) as Total_Sales, ROUND(AVG(Sales), 2) as Avg_Sales, ROUND(SUM(Profit), 2) as Total_Profit, ROUND(AVG(Profit), 2) as Avg_Profit FROM superstore GROUP BY Region ORDER BY Total_Sales DESC;'
result = pd.read_sql_query(q4_1, conn)
print(result.to_string(index=False))

# Query 4.2: Sales by Category
print("\n\n[4.2] Sales Metrics by Category:")
q4_2 = 'SELECT Category, COUNT(*) as Items_Sold, ROUND(SUM(Quantity), 2) as Total_Quantity, ROUND(SUM(Sales), 2) as Total_Sales, ROUND(AVG(Sales), 2) as Avg_Sale_Value, ROUND(SUM(Profit), 2) as Total_Profit, ROUND(100.0 * SUM(Profit) / SUM(Sales), 2) as Profit_Margin_Percent FROM superstore GROUP BY Category ORDER BY Total_Sales DESC;'
result = pd.read_sql_query(q4_2, conn)
print(result.to_string(index=False))

# Query 4.3: Sales by Segment
print("\n\n[4.3] Sales by Customer Segment:")
q4_3 = 'SELECT Segment, COUNT(DISTINCT "Customer ID") as Unique_Customers, COUNT(*) as Total_Orders, ROUND(SUM(Sales), 2) as Total_Sales, ROUND(AVG(Sales), 2) as Avg_Order_Value, ROUND(SUM(Profit), 2) as Total_Profit FROM superstore GROUP BY Segment ORDER BY Total_Sales DESC;'
result = pd.read_sql_query(q4_3, conn)
print(result.to_string(index=False))

# Query 4.4: Sales by Ship Mode
print("\n\n[4.4] Performance by Ship Mode:")
q4_4 = 'SELECT "Ship Mode", COUNT(*) as Orders, ROUND(SUM(Sales), 2) as Total_Sales, ROUND(AVG(Sales), 2) as Avg_Sales, ROUND(SUM(Profit), 2) as Total_Profit FROM superstore GROUP BY "Ship Mode" ORDER BY Total_Sales DESC;'
result = pd.read_sql_query(q4_4, conn)
print(result.to_string(index=False))

# ============================================================================
# STEP 5: Sort and Limit Results (Top Products, Top Categories)
# ============================================================================

print("\n" + "=" * 80)
print("STEP 5: SORT & LIMIT (TOP PRODUCTS, TOP CATEGORIES)")
print("=" * 80)

# Query 5.1: Top 10 Products by Sales
print("\n[5.1] Top 10 Products by Sales:")
q5_1 = 'SELECT "Product Name", Category, "Sub-Category", COUNT(*) as Order_Count, ROUND(SUM(Sales), 2) as Total_Sales, ROUND(AVG(Sales), 2) as Avg_Sale FROM superstore GROUP BY "Product Name" ORDER BY Total_Sales DESC LIMIT 10;'
result = pd.read_sql_query(q5_1, conn)
print(result.to_string(index=False))

# Query 5.2: Top 10 Sub-Categories by Profit
print("\n\n[5.2] Top 10 Sub-Categories by Profit:")
q5_2 = 'SELECT "Sub-Category", Category, COUNT(*) as Items_Sold, ROUND(SUM(Sales), 2) as Total_Sales, ROUND(SUM(Profit), 2) as Total_Profit, ROUND(100.0 * SUM(Profit) / SUM(Sales), 2) as Profit_Margin FROM superstore GROUP BY "Sub-Category" ORDER BY Total_Profit DESC LIMIT 10;'
result = pd.read_sql_query(q5_2, conn)
print(result.to_string(index=False))

# Query 5.3: Bottom 10 Sub-Categories by Profit (Worst Performers)
print("\n\n[5.3] Bottom 10 Sub-Categories by Profit (Problem Areas):")
q5_3 = 'SELECT "Sub-Category", Category, COUNT(*) as Items_Sold, ROUND(SUM(Sales), 2) as Total_Sales, ROUND(SUM(Profit), 2) as Total_Profit, ROUND(100.0 * SUM(Profit) / SUM(Sales), 2) as Profit_Margin FROM superstore GROUP BY "Sub-Category" ORDER BY Total_Profit ASC LIMIT 10;'
result = pd.read_sql_query(q5_3, conn)
print(result.to_string(index=False))

# Query 5.4: Top 10 Customers by Sales
print("\n\n[5.4] Top 10 Customers by Sales:")
q5_4 = 'SELECT "Customer ID", "Customer Name", Segment, COUNT(*) as Order_Count, ROUND(SUM(Sales), 2) as Total_Sales, ROUND(SUM(Profit), 2) as Total_Profit FROM superstore GROUP BY "Customer ID" ORDER BY Total_Sales DESC LIMIT 10;'
result = pd.read_sql_query(q5_4, conn)
print(result.to_string(index=False))

# ============================================================================
# STEP 6: Business Use Cases
# ============================================================================

print("\n" + "=" * 80)
print("STEP 6: BUSINESS USE CASES")
print("=" * 80)

# Use Case 6.1: Monthly Sales Trends
print("\n[6.1] Monthly Sales Trends (2015-2016):")
q6_1 = 'SELECT strftime("%Y-%m", "Order Date") as YearMonth, ROUND(SUM(Sales), 2) as Monthly_Sales, ROUND(SUM(Profit), 2) as Monthly_Profit, ROUND(AVG(Sales), 2) as Avg_Order_Value, COUNT(*) as Order_Count FROM superstore GROUP BY YearMonth ORDER BY YearMonth;'
result = pd.read_sql_query(q6_1, conn)
print(result.to_string(index=False))

# Use Case 6.2: Profitability by Region and Segment
print("\n\n[6.2] Profitability Matrix (Region × Segment):")
q6_2 = 'SELECT Region, Segment, COUNT(*) as Orders, ROUND(SUM(Sales), 2) as Total_Sales, ROUND(SUM(Profit), 2) as Total_Profit, ROUND(100.0 * SUM(Profit) / SUM(Sales), 2) as Profit_Margin FROM superstore GROUP BY Region, Segment ORDER BY Total_Profit DESC;'
result = pd.read_sql_query(q6_2, conn)
print(result.to_string(index=False))

# Use Case 6.3: High-Value Customers (Top Spenders)
print("\n\n[6.3] High-Value Customers Analysis:")
q6_3 = 'SELECT "Customer ID", "Customer Name", Segment, City, State, COUNT(*) as Purchase_Frequency, ROUND(SUM(Sales), 2) as Lifetime_Sales, ROUND(SUM(Profit), 2) as Lifetime_Profit, ROUND(AVG(Sales), 2) as Avg_Order_Value FROM superstore GROUP BY "Customer ID" HAVING SUM(Sales) > 2000 ORDER BY Lifetime_Sales DESC LIMIT 10;'
result = pd.read_sql_query(q6_3, conn)
print(result.to_string(index=False))

# Use Case 6.4: At-Risk Products (High Discount Impact)
print("\n\n[6.4] At-Risk Products (High Discount Orders):")
q6_4 = 'SELECT "Sub-Category", "Product Name", COUNT(*) as Discounted_Orders, ROUND(AVG(Discount), 2) as Avg_Discount, ROUND(SUM(Sales), 2) as Total_Sales, ROUND(SUM(Profit), 2) as Total_Profit, ROUND(100.0 * SUM(Profit) / SUM(Sales), 2) as Profit_Margin FROM superstore WHERE Discount > 0.2 GROUP BY "Product Name" ORDER BY Avg_Discount DESC LIMIT 15;'
result = pd.read_sql_query(q6_4, conn)
print(result.to_string(index=False))

# Use Case 6.5: Regional Performance Comparison
print("\n\n[6.5] Regional Deep Dive (Top Categories per Region):")
q6_5 = 'SELECT Region, Category, ROUND(SUM(Sales), 2) as Total_Sales, COUNT(*) as Orders, ROUND(SUM(Profit), 2) as Total_Profit FROM superstore GROUP BY Region, Category ORDER BY Region, Total_Sales DESC;'
result = pd.read_sql_query(q6_5, conn)
print(result.to_string(index=False))

# Use Case 6.6: Order Value Distribution
print("\n\n[6.6] Order Value Distribution:")
q6_6 = 'SELECT CASE WHEN Sales < 50 THEN "Under $50" WHEN Sales < 100 THEN "$50-$100" WHEN Sales < 250 THEN "$100-$250" WHEN Sales < 500 THEN "$250-$500" ELSE "Over $500" END as Price_Range, COUNT(*) as Order_Count, ROUND(SUM(Sales), 2) as Total_Sales, ROUND(AVG(Sales), 2) as Avg_Sale, ROUND(SUM(Profit), 2) as Total_Profit FROM superstore GROUP BY Price_Range ORDER BY CASE WHEN Price_Range = "Under $50" THEN 1 WHEN Price_Range = "$50-$100" THEN 2 WHEN Price_Range = "$100-$250" THEN 3 WHEN Price_Range = "$250-$500" THEN 4 ELSE 5 END;'
result = pd.read_sql_query(q6_6, conn)
print(result.to_string(index=False))

# ============================================================================
# STEP 7: Data Quality & Validation
# ============================================================================

print("\n" + "=" * 80)
print("STEP 7: DATA QUALITY & VALIDATION")
print("=" * 80)

# Query 7.1: Row Count Validation
print("\n[7.1] Row Count Validation:")
q7_1 = "SELECT COUNT(*) as Total_Rows FROM superstore;"
result = pd.read_sql_query(q7_1, conn)
print(f"Total Rows: {result['Total_Rows'][0]}")

# Query 7.2: Unique Count Validation
print("\n[7.2] Unique Values Count:")
q7_2 = 'SELECT COUNT(DISTINCT "Customer ID") as Unique_Customers, COUNT(DISTINCT "Order ID") as Unique_Orders, COUNT(DISTINCT "Product ID") as Unique_Products, COUNT(DISTINCT Region) as Regions, COUNT(DISTINCT Segment) as Segments, COUNT(DISTINCT Category) as Categories FROM superstore;'
result = pd.read_sql_query(q7_2, conn)
print(result.to_string(index=False))

# Query 7.3: Date Range
print("\n[7.3] Date Range Validation:")
q7_3 = 'SELECT MIN("Order Date") as Earliest_Order, MAX("Order Date") as Latest_Order, julianday(MAX("Order Date")) - julianday(MIN("Order Date")) as Days_Span FROM superstore;'
result = pd.read_sql_query(q7_3, conn)
print(result.to_string(index=False))

# Query 7.4: Duplicate Check
print("\n[7.4] Duplicate Order Detection:")
q7_4 = 'SELECT "Order ID", COUNT(*) as Occurrence_Count, COUNT(DISTINCT "Row ID") as Unique_Items, ROUND(SUM(Sales), 2) as Total_Amount FROM superstore GROUP BY "Order ID" HAVING COUNT(*) > 1 ORDER BY Occurrence_Count DESC LIMIT 20;'
result = pd.read_sql_query(q7_4, conn)
print(f"Found {len(result)} orders with multiple line items")
print(result.to_string(index=False))

# Query 7.5: Missing/Null Values
print("\n[7.5] Data Completeness Check:")
q7_5 = 'SELECT COUNT(*) as Total_Records, COUNT(CASE WHEN Sales IS NULL THEN 1 END) as Null_Sales, COUNT(CASE WHEN Profit IS NULL THEN 1 END) as Null_Profit, COUNT(CASE WHEN "Customer ID" IS NULL THEN 1 END) as Null_Customer_ID FROM superstore;'
result = pd.read_sql_query(q7_5, conn)
print(result.to_string(index=False))

# Query 7.6: Negative Values Check
print("\n[7.6] Data Integrity Check (Negative Values):")
q7_6 = 'SELECT COUNT(CASE WHEN Sales < 0 THEN 1 END) as Negative_Sales, COUNT(CASE WHEN Quantity < 0 THEN 1 END) as Negative_Quantity, COUNT(CASE WHEN Discount < 0 OR Discount > 1 THEN 1 END) as Invalid_Discount, COUNT(CASE WHEN Profit < -1000 THEN 1 END) as Extreme_Loss_Orders FROM superstore;'
result = pd.read_sql_query(q7_6, conn)
print(result.to_string(index=False))

# ============================================================================
# SUMMARY INSIGHTS
# ============================================================================

print("\n" + "=" * 80)
print("KEY INSIGHTS & SUMMARY")
print("=" * 80)

summary_query = 'SELECT ROUND(SUM(Sales), 2) as Total_Sales, ROUND(SUM(Profit), 2) as Total_Profit, ROUND(100.0 * SUM(Profit) / SUM(Sales), 2) as Overall_Profit_Margin, ROUND(AVG(Sales), 2) as Avg_Order_Value, ROUND(AVG(Quantity), 2) as Avg_Quantity_Per_Order, COUNT(*) as Total_Orders, COUNT(DISTINCT "Customer ID") as Total_Customers FROM superstore;'
summary = pd.read_sql_query(summary_query, conn)
print(summary.to_string(index=False))

print("\n✓ Analysis Complete!")
print("=" * 80)

conn.close()
