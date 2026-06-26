# Superstore Sales Data Analysis using SQL

## 📋 Project Overview

This project provides a comprehensive SQL-based analysis of superstore sales data spanning 4 years (2014-2017). It demonstrates practical SQL techniques including filtering, aggregations, grouping, and business intelligence queries on a real-world dataset.

**Dataset**: 9,994 sales records | **Customers**: 793 unique | **Products**: 1,862 unique | **Time Period**: Jan 2014 - Dec 2017

---

## 📁 Project Structure

```
superstore-sql-analysis/
├── README.md                          # This file
├── ANALYSIS_SUMMARY.md               # Executive summary & business insights
├── SQL_QUERIES_REFERENCE.md          # Complete SQL query guide (24 queries)
├── superstore_sql_analysis.py        # Complete analysis script (runnable)
└── Sample_-_Superstore.csv           # Original dataset
```

---

## 🎯 Quick Start

### Prerequisites
- Python 3.x
- pandas
- sqlite3 (included with Python)

### Installation

```bash
# Install required packages
pip install pandas

# Run the analysis
python superstore_sql_analysis.py
```

**Output**: Complete analysis with 7 sections and 50+ SQL queries executed

---

## 📊 What's Included

### 1. **ANALYSIS_SUMMARY.md** - Executive Summary
High-level business insights including:
- Financial overview ($2.3M sales, $286K profit)
- Regional and category performance analysis
- Top 10 products and customers
- **Critical Issues** flagged for immediate action
- 7 strategic recommendations with priorities
- Data quality assessment

**Best For**: Executives, business stakeholders, decision makers

### 2. **SQL_QUERIES_REFERENCE.md** - Technical Guide
Detailed documentation of 24 SQL queries:

#### **Section 1: Basic Filtering (WHERE)**
- Regional sales filtering
- Category-based queries
- High-discount product analysis
- Loss-making order detection

#### **Section 2: Aggregations (GROUP BY)**
- Regional performance summaries
- Category analysis with margins
- Customer segment breakdown
- Shipping mode performance

#### **Section 3: Top Products & Categories**
- Top 10 products by sales
- Top 10 sub-categories by profit
- Bottom 10 problem areas
- Top 10 customers

#### **Section 4: Business Use Cases**
- Monthly sales trends
- Profitability matrix (region × segment)
- High-value customer analysis
- At-risk products detection
- Regional deep dives
- Order value distribution

#### **Section 5: Data Quality**
- Row count validation
- Unique value counts
- Date range verification
- Duplicate detection
- Completeness checks
- Integrity validation

**Best For**: Data analysts, SQL developers, business analysts

### 3. **superstore_sql_analysis.py** - Executable Script
Production-ready Python script with:
- Data loading and preprocessing
- SQLite database creation
- 7 analysis sections
- 50+ SQL queries
- Formatted output tables
- Complete validation checks

**Features**:
- ✅ No external dependencies beyond pandas and sqlite3
- ✅ Reproducible results
- ✅ Well-commented code
- ✅ Easy to modify and extend
- ✅ Professional output formatting

**Best For**: Data professionals, automation, reproducibility

---

## 🔍 Analysis Sections

### Section 1: Data Loading & Schema
- Loads CSV into SQLite database
- Displays table schema
- Shows sample records
- Validates data types

### Section 2: WHERE Filters
```
Query Examples:
- Sales in West Region > $100
- Furniture category in CA and TX
- Orders with discounts > 0
- Loss-making orders (Profit < 0)
```

### Section 3: GROUP BY Aggregations
```
Query Examples:
- Sales by Region
- Sales by Category (with profit margins)
- Sales by Customer Segment
- Sales by Ship Mode
```

### Section 4: Top Products & Categories
```
Query Examples:
- Top 10 products by sales
- Top 10 sub-categories by profit
- Bottom 10 problem areas
- Top 10 customers
```

### Section 5: Business Use Cases
```
Query Examples:
- Monthly sales trends (time series)
- Profitability matrix (region × segment)
- High-value customers analysis
- At-risk products (high discounts)
- Regional performance comparison
- Order value distribution
```

### Section 6: Data Quality & Validation
```
Query Examples:
- Row count validation
- Unique value counts
- Date range verification
- Duplicate detection
- Null/missing value checks
- Data integrity validation
```

### Section 7: Summary Insights
- Overall profit margin: 12.47%
- Average order value: $229.86
- Total customers: 793
- Peak months: November, December

---

## 💡 Key Findings

### 🎯 Strengths
✅ **Technology Category**: 17.40% profit margin (50.8% of total profit)
✅ **West Region**: Best performer with 14.94% margin
✅ **Consumer Segment**: Highest sales volume ($1.16M)
✅ **Data Quality**: No missing values, complete dataset

### 🚨 Critical Issues
❌ **Furniture Category**: Only 2.49% margin (UNSUSTAINABLE)
- Tables: -$17,725 loss (negative 8.56% margin)
- Bookcases: -$3,472 loss (negative 3.02% margin)

❌ **Aggressive Discounting**: 80% discounts destroy profitability
- Example: Binding machines losing $2,929 each with 80% discount

❌ **Regional Variance**: Central region significantly underperforms
- Central: 7.93% margin vs West: 14.94% margin

### 💼 Opportunities
1. Fix Furniture category pricing/costs (potential +$20K profit)
2. Eliminate high-discount strategy (save $100K+ annually)
3. Expand Technology category (highest margins)
4. Replicate West region strategy to Central region

---

## 📈 Data Summary

### Sales by Region
| Region | Sales | Profit | Margin | Orders |
|--------|-------|--------|--------|--------|
| West | $725K | $108K | 14.94% | 3,203 |
| East | $679K | $92K | 13.49% | 2,848 |
| Central | $501K | $40K | 7.93% | 2,323 |
| South | $392K | $47K | 11.94% | 1,620 |

### Sales by Category
| Category | Sales | Profit | Margin | Items |
|----------|-------|--------|--------|-------|
| Technology | $836K | $145K | 17.40% | 1,847 |
| Office Supplies | $719K | $122K | 17.04% | 6,026 |
| Furniture | $742K | $18K | 2.49% | 2,121 |

### Sales by Segment
| Segment | Sales | Profit | Customers | Orders |
|---------|-------|--------|-----------|--------|
| Consumer | $1.16M | $134K | 409 | 5,191 |
| Corporate | $706K | $92K | 236 | 3,020 |
| Home Office | $430K | $60K | 148 | 1,783 |

---

## 🛠️ SQL Techniques Demonstrated

### Filtering & Selection
- WHERE clause with multiple conditions (AND, OR, IN)
- Complex filtering logic
- Date range queries

### Aggregation & Grouping
- SUM, AVG, COUNT aggregations
- GROUP BY single and multiple columns
- HAVING clause for post-aggregation filters

### Advanced Features
- CASE statements for data binning
- Date functions (strftime)
- DISTINCT for unique counts
- Subqueries and joins
- ROUND for decimal formatting

### Window Functions
- ORDER BY with LIMIT for top-N queries
- Date formatting for trend analysis

---

## 📖 How to Use

### For Business Users
1. Read **ANALYSIS_SUMMARY.md** for executive insights
2. Look for sections marked 🚨 for urgent issues
3. Review "Strategic Recommendations" for action items
4. Use "Next Steps" section for implementation timeline

### For Data Analysts
1. Review **SQL_QUERIES_REFERENCE.md** for query patterns
2. Run **superstore_sql_analysis.py** to see results
3. Modify queries for your specific use cases
4. Use as template for similar analyses

### For Developers
1. Clone/download the script
2. Modify CSV path if needed
3. Add your own queries to the script
4. Run and export results to CSV/JSON as needed

---

## 🔄 Customization Guide

### Add a New Query
```python
# Example: Add a new query to section 3

print("\n\n[3.5] Your Custom Query Title:")
q3_5 = '''
SELECT 
    Column1,
    COUNT(*) as Count,
    ROUND(SUM(Column2), 2) as Total
FROM superstore
WHERE Condition
GROUP BY Column1
ORDER BY Total DESC
LIMIT 10;
'''
result = pd.read_sql_query(q3_5, conn)
print(result.to_string(index=False))
```

### Change Date Range
```python
# Filter for specific year
WHERE strftime('%Y', "Order Date") = '2017'
```

### Focus on Specific Region
```python
# Add to WHERE clause
WHERE Region = 'West'
```

### Export Results to CSV
```python
# Add at end of query
result.to_csv('output.csv', index=False)
```

---

## 📊 Visualizations You Can Create

Based on the analysis, consider visualizing:

1. **Monthly Sales Trend** (Line Chart)
   - Query: 6.1 Monthly Sales Trends
   - Seasonal patterns are clear

2. **Regional Performance** (Bar Chart)
   - Query: 4.1 Sales by Region
   - Show profit margins

3. **Category Comparison** (Pie Chart)
   - Query: 4.2 Sales by Category
   - Highlight Furniture problem

4. **Product Performance** (Horizontal Bar)
   - Query: 5.1 Top 10 Products
   - Top revenue generators

5. **Profitability Matrix** (Heatmap)
   - Query: 6.2 Profitability Matrix
   - Region × Segment view

---

## ⚠️ Data Quality Notes

### Strengths
- ✅ 9,994 complete records (no missing values)
- ✅ 4 years of consistent data
- ✅ All numeric fields valid
- ✅ Proper date ranges (2014-2017)

### Observations
- ⚠️ 22 orders with extreme losses (< -$1,000)
  - Review if data entry errors
  - Investigate business reasons
  
- ⚠️ 80% discount orders
  - Some may be promotional
  - Many are unprofitable
  - Review discount policy

- ⚠️ Furniture category unprofitability
  - Consistent pattern across all furniture sub-categories
  - Suggests structural pricing issue

---

## 🚀 Performance Metrics

| Metric | Value |
|--------|-------|
| Total Rows Analyzed | 9,994 |
| Time Range | 1,457 days (4 years) |
| Query Execution Time | < 1 second each |
| Database Size | In-memory (no storage) |
| Analysis Runtime | ~5-10 seconds |

---

## 📚 Learning Resources

### SQL Concepts Covered
1. **SELECT & WHERE** - Filtering data
2. **GROUP BY & HAVING** - Aggregation
3. **ORDER BY & LIMIT** - Sorting and limiting
4. **Joins** - Combining data (implicit in GROUP BY)
5. **CASE** - Conditional logic
6. **Aggregate Functions** - SUM, AVG, COUNT, etc.
7. **Date Functions** - strftime for formatting

### Best Practices Demonstrated
- ✓ Quoting column names with spaces
- ✓ Using HAVING for post-aggregation filters
- ✓ Proper aliasing for clarity
- ✓ Rounding monetary values
- ✓ Sorting results meaningfully
- ✓ Validation checks for data quality

---

## 🤝 Contributing

To extend this analysis:
1. Add new business questions
2. Create additional queries
3. Build visualizations
4. Document findings
5. Share improvements

---

## 📝 License

This project is provided as-is for educational and commercial use.

---

## 📧 Support & Questions

For questions about:
- **Business Insights**: See ANALYSIS_SUMMARY.md
- **SQL Queries**: See SQL_QUERIES_REFERENCE.md
- **Code Execution**: Review comments in superstore_sql_analysis.py
- **Customization**: Check "Customization Guide" section above

---

## 🎓 Educational Value

This project teaches:
- ✅ Real-world SQL analysis patterns
- ✅ Business intelligence querying
- ✅ Data validation techniques
- ✅ Performance optimization
- ✅ Report generation
- ✅ Python-SQL integration

---

## 📋 Checklist for Using This Project

- [ ] Review ANALYSIS_SUMMARY.md for business context
- [ ] Run superstore_sql_analysis.py successfully
- [ ] Understand the 7 analysis sections
- [ ] Review critical findings (🚨 items)
- [ ] Consider strategic recommendations
- [ ] Customize queries for your needs
- [ ] Export results for presentations
- [ ] Create visualizations
- [ ] Share insights with stakeholders

---

## 🎯 Next Steps

1. **Immediate** (This Week)
   - Review critical issues in ANALYSIS_SUMMARY
   - Run the analysis script
   - Validate findings against your knowledge

2. **Short-term** (This Month)
   - Investigate Furniture category pricing
   - Review discount policy impact
   - Analyze Central region underperformance

3. **Long-term** (This Quarter)
   - Implement corrective actions
   - Monitor KPIs using these queries
   - Build automated reporting dashboard

---

**Project Version**: 1.0
**Last Updated**: June 2025
**Analysis Tool**: Python + SQLite
**Status**: ✅ Production Ready

For the latest version and updates, refer to the included files.

---

## 📞 Quick Reference

**Main Files**:
- 📄 `ANALYSIS_SUMMARY.md` - Business insights (5 min read)
- 📄 `SQL_QUERIES_REFERENCE.md` - Technical guide (15 min read)
- 🐍 `superstore_sql_analysis.py` - Runnable analysis (< 1 min to run)

**Key Findings**:
- 🎯 Technology: Best profit margin (17.40%)
- 🚨 Furniture: Critical issue (2.49% margin)
- 📊 West Region: Best performer (14.94% margin)
- 💰 Total Profit: $286,397 (12.47% overall margin)

**Recommendations**:
1. Fix Furniture pricing immediately
2. Eliminate 80% discounts
3. Expand Technology category
4. Improve Central region performance

---

*Thank you for using this analysis. For more information, refer to the detailed documentation files included in this project.*
