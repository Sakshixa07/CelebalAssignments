# SQL Assignment: E-Commerce Sales Database
## Celebal Summer Internship 2026 - Week 2 Task

---

## 📋 Table of Contents

1. [Overview](#overview)
2. [Scenario & Business Context](#scenario--business-context)
3. [Database Schema](#database-schema)
4. [Setup Instructions](#setup-instructions)
5. [File Structure](#file-structure)
6. [Section Breakdown](#section-breakdown)
7. [How to Use This Package](#how-to-use-this-package)
8. [Learning Outcomes](#learning-outcomes)
9. [Submission Guidelines](#submission-guidelines)

---

## Overview

This SQL assignment focuses on **database design, querying, and management** for a realistic e-commerce scenario. You will work with a relational database containing customer, product, order, and order item information.

**Database System Support:**
- MySQL 5.7+
- PostgreSQL 10+
- SQLite 3
- SQL Server 2016+
- MariaDB 10.3+

---

## Scenario & Business Context

You are a Junior Data Analyst at **ShopEase**, a mid-sized e-commerce company selling:
- Electronics (smartphones, earbuds, smartwatches, speakers)
- Clothing (t-shirts, shoes, accessories)
- Home products (bedsheets, cushion covers)

**Your Objectives:**
- Extract meaningful insights from sales data
- Understand customer behavior patterns
- Analyze product performance
- Support management decision-making

---

## Database Schema

### Entity-Relationship Diagram
```
                 ┌──────────────┐
                 │  customers   │
                 └──────┬───────┘
                        │ 1:N (customer_id)
                        ▼
                 ┌──────────────┐
                 │   orders     │
                 └──────┬───────┘
                        │ 1:N (order_id)
                        ▼
                 ┌──────────────┐      ┌──────────────┐
                 │ order_items  │◀──┐  │   products   │
                 └──────────────┘   │  └──────────────┘
                                    └─(product_id)
```

### Table Specifications

#### 1. **customers** Table
| Column | Type | Constraints | Purpose |
|--------|------|-------------|---------|
| customer_id | INT | PRIMARY KEY | Unique customer identifier |
| first_name | VARCHAR(50) | NOT NULL | Customer first name |
| last_name | VARCHAR(50) | NOT NULL | Customer last name |
| email | VARCHAR(100) | UNIQUE, NOT NULL | Email address (unique) |
| city | VARCHAR(50) | NOT NULL | City of residence |
| state | VARCHAR(50) | NOT NULL | State/Province |
| join_date | DATE | NOT NULL | Account creation date |
| is_premium | BOOLEAN | DEFAULT FALSE | Premium member status |

**Indexes:** city, state

**Sample Data:** 8 customers from various Indian cities

---

#### 2. **products** Table
| Column | Type | Constraints | Purpose |
|--------|------|-------------|---------|
| product_id | INT | PRIMARY KEY | Unique product identifier |
| product_name | VARCHAR(100) | NOT NULL | Product name |
| category | VARCHAR(50) | NOT NULL | Category (Electronics, Clothing, Home) |
| brand | VARCHAR(50) | NOT NULL | Brand name |
| unit_price | DECIMAL(10,2) | NOT NULL, CHECK > 0 | Price per unit (₹) |
| stock_qty | INT | NOT NULL, DEFAULT 0, CHECK >= 0 | Available quantity |

**Indexes:** category

**Sample Data:** 8 products across 3 categories

---

#### 3. **orders** Table
| Column | Type | Constraints | Purpose |
|--------|------|-------------|---------|
| order_id | INT | PRIMARY KEY | Unique order identifier |
| customer_id | INT | NOT NULL, FOREIGN KEY | References customers |
| order_date | DATE | NOT NULL | Order placement date |
| status | VARCHAR(20) | NOT NULL, CHECK IN (...) | Order status |
| total_amount | DECIMAL(12,2) | NOT NULL, CHECK >= 0 | Order total (₹) |

**Valid Status Values:** Pending, Shipped, Delivered, Cancelled

**Indexes:** order_date, status

**Foreign Key:** customer_id → customers.customer_id

**Sample Data:** 10 orders from August 2024

---

#### 4. **order_items** Table
| Column | Type | Constraints | Purpose |
|--------|------|-------------|---------|
| item_id | INT | PRIMARY KEY | Unique line item identifier |
| order_id | INT | NOT NULL, FOREIGN KEY | References orders |
| product_id | INT | NOT NULL, FOREIGN KEY | References products |
| quantity | INT | NOT NULL, CHECK > 0 | Quantity ordered |
| unit_price | DECIMAL(10,2) | NOT NULL, CHECK > 0 | Price at purchase time |
| discount_pct | DECIMAL(5,2) | DEFAULT 0, CHECK 0-100 | Discount percentage |

**Foreign Keys:**
- order_id → orders.order_id
- product_id → products.product_id

**Sample Data:** 15 line items across 10 orders

---

## Setup Instructions

### Step 1: Choose Your Database System

Select one of these systems:
- **MySQL:** Most common for web applications
- **PostgreSQL:** Enterprise-grade, advanced features
- **SQLite:** Lightweight, no server needed (great for learning)

### Step 2: Create Database and Run Setup Script

#### For MySQL:
```bash
mysql -u root -p

mysql> CREATE DATABASE ecommerce_db;
mysql> USE ecommerce_db;
mysql> SOURCE /path/to/00_setup.sql;
```

#### For PostgreSQL:
```bash
createdb ecommerce_db
psql -U postgres -d ecommerce_db -f /path/to/00_setup.sql
```

#### For SQLite:
```bash
sqlite3 ecommerce_db.db < /path/to/00_setup.sql
```

### Step 3: Verify Setup

Run the verification queries included in the setup script:
```sql
SELECT 'CUSTOMERS' AS table_name, COUNT(*) AS row_count FROM customers
UNION ALL
SELECT 'PRODUCTS', COUNT(*) FROM products
UNION ALL
SELECT 'ORDERS', COUNT(*) FROM orders
UNION ALL
SELECT 'ORDER_ITEMS', COUNT(*) FROM order_items;
```

Expected output:
```
CUSTOMERS      | 8
PRODUCTS       | 8
ORDERS         | 10
ORDER_ITEMS    | 15
```

---

## File Structure

```
sql-assignment/
│
├── 00_setup.sql                    # Database schema and sample data
├── Section_A_basic_queries.sql     # Q1-Q6: SELECT, constraints, PKs
├── Section_B_filtering_queries.sql # Q7-Q12: WHERE, indexes, SARGABILITY
├── Section_C_aggregation_queries.sql # Q13-Q18: GROUP BY, aggregate functions
├── Section_D_joins_queries.sql     # Q19-Q23: INNER/LEFT/FULL JOINs
├── Section_E_advanced_queries.sql  # Q24-Q27: CASE, ACID, transactions
│
└── README.md                       # This file
```

---

## Section Breakdown

### Section A: SQL Basics (Q1-Q6)
**Focus:** Foundational SQL concepts

- **Q1-Q3:** Basic SELECT queries
- **Q4:** Primary key concepts
- **Q5:** Unique and NOT NULL constraints
- **Q6:** CHECK constraints and validation

**Key Concepts:**
- Column selection
- Filtering columns
- DISTINCT keyword
- Primary keys and constraints

**Expected Time:** 10 minutes

---

### Section B: Filtering & Optimization (Q7-Q12)
**Focus:** WHERE clauses, indexes, and query optimization

- **Q7-Q10:** Various WHERE conditions (=, >, BETWEEN, AND, OR)
- **Q11:** Index usage and performance benefits
- **Q12:** SARGABILITY and index-friendly queries

**Key Concepts:**
- WHERE clause operators
- Compound conditions (AND, OR)
- Date range filtering
- Index selection and optimization
- SARGABLE queries

**Expected Time:** 20 minutes

---

### Section C: Aggregation (Q13-Q18)
**Focus:** GROUP BY and aggregate functions

- **Q13-Q14:** COUNT and SUM
- **Q15-Q16:** AVG, MIN, MAX with GROUP BY
- **Q17-Q18:** Complex aggregations and HAVING clause

**Key Concepts:**
- Aggregate functions (COUNT, SUM, AVG, MIN, MAX)
- GROUP BY clause
- WHERE vs HAVING
- Conditional aggregation

**Expected Time:** 25 minutes

---

### Section D: Joins & Relationships (Q19-Q23)
**Focus:** Combining data from multiple tables

- **Q19:** INNER JOIN
- **Q20:** LEFT JOIN
- **Q21:** Multi-table JOINs (3+ tables)
- **Q22:** LEFT/RIGHT/FULL OUTER JOINs comparison
- **Q23:** Foreign key relationships and constraints

**Key Concepts:**
- INNER JOIN (matching records)
- LEFT JOIN (all from left table)
- RIGHT JOIN (all from right table)
- FULL OUTER JOIN (all from both)
- Foreign key constraints
- Referential integrity

**Expected Time:** 30 minutes

---

### Section E: Advanced Concepts (Q24-Q27)
**Focus:** Conditional logic, database reliability, and transactions

- **Q24:** CASE statement for conditional logic
- **Q25:** CASE in aggregate functions
- **Q26:** ACID properties (detailed explanation)
- **Q27:** SQL transactions with COMMIT/ROLLBACK

**Key Concepts:**
- CASE statements (simple and searched)
- CASE in SELECT and aggregation
- ACID properties (Atomicity, Consistency, Isolation, Durability)
- Transactions and error handling
- COMMIT and ROLLBACK
- Savepoints

**Expected Time:** 35 minutes

---

## How to Use This Package

### Method 1: Sequential Learning (Recommended)

1. **Start with Setup**
   ```sql
   -- Run 00_setup.sql to create tables and load data
   SOURCE 00_setup.sql;
   ```

2. **Work through Sections A-E**
   - Read explanations provided in each SQL file
   - Execute queries and observe results
   - Modify queries to experiment
   - Write your own variations

3. **Progressive Difficulty**
   - Section A: 5-10 minutes per question
   - Section B: 10-20 minutes per question
   - Section C: 15-25 minutes per question
   - Section D: 20-30 minutes per question
   - Section E: 25-40 minutes per question

### Method 2: Topic-Based Learning

- Learning **SELECT statements?** → Section A
- Learning **WHERE clauses?** → Section B
- Learning **data aggregation?** → Section C
- Learning **JOINs?** → Section D
- Learning **advanced SQL?** → Section E

### Method 3: Practice by Doing

1. Read the question
2. Try to write the query yourself (5-10 minutes)
3. Compare your solution with the provided one
4. Understand the explanation
5. Experiment with variations

---

## Learning Outcomes

After completing this assignment, you should be able to:

### Foundational Skills
- [ ] Write basic SELECT queries with column selection
- [ ] Understand and use primary keys, unique constraints, and NOT NULL
- [ ] Recognize and explain CHECK constraints
- [ ] Use DISTINCT to eliminate duplicates

### Filtering & Optimization
- [ ] Write WHERE clauses with single and multiple conditions
- [ ] Use operators: =, <, >, <=, >=, !=, BETWEEN, IN, LIKE
- [ ] Understand how indexes improve query performance
- [ ] Write SARGABLE (index-friendly) queries
- [ ] Avoid common optimization pitfalls (functions on indexed columns)

### Aggregation
- [ ] Use COUNT, SUM, AVG, MIN, MAX functions
- [ ] Group data using GROUP BY
- [ ] Filter groups using HAVING clause
- [ ] Calculate percentages and running totals
- [ ] Understand WHERE vs HAVING

### Joins & Relationships
- [ ] Perform INNER JOINs to match records
- [ ] Perform LEFT JOINs to preserve all rows from left table
- [ ] Perform multi-table JOINs (3+ tables)
- [ ] Understand and explain LEFT/RIGHT/FULL OUTER JOINs
- [ ] Understand foreign key constraints and referential integrity

### Advanced Concepts
- [ ] Use CASE statements for conditional logic
- [ ] Implement CASE in aggregate functions
- [ ] Explain ACID properties with real-world examples
- [ ] Write and execute SQL transactions
- [ ] Implement COMMIT/ROLLBACK for data integrity
- [ ] Handle errors in transactions

---

## Submission Guidelines

### Step 1: Organize Your Work

Create this folder structure:
```
sql-assignment/
├── Section_A/
│   └── basic_queries.sql
├── Section_B/
│   └── filtering_queries.sql
├── Section_C/
│   └── aggregation_queries.sql
├── Section_D/
│   └── joins_queries.sql
├── Section_E/
│   └── advanced_queries.sql
├── setup.sql
└── README.md
```

### Step 2: Organize Queries

For each section file, organize as:
```sql
-- ===================================================================
-- Section X: [Title]
-- ===================================================================

-- Q1. Question text
-- Solution:
SELECT ... FROM ... WHERE ...;

-- Explanation:
-- [Detailed explanation of the query]
-- Expected output: [What the query should return]

-- Q2. Next question...
```

### Step 3: Add Comments

Every query should have:
```sql
-- Q#. Question text
-- Solution:
[QUERY]

-- Explanation:
-- [Why it works]
-- [Key concepts used]
-- [Expected output]
```

### Step 4: Test All Queries

Ensure:
- [ ] All queries execute without errors
- [ ] Results match expected output
- [ ] Comments explain the solution
- [ ] Formatting is readable (proper indentation)
- [ ] No sensitive data in queries

### Step 5: GitHub Submission

```bash
# Create repository
git init sql-assignment
cd sql-assignment

# Add all files
git add .
git commit -m "SQL Assignment: E-Commerce Database Queries"

# Push to GitHub
git push origin main
```

### GitHub Repository Format

```
sql-assignment/
├── .gitignore
├── README.md
├── Section_A_basic_queries.sql
├── Section_B_filtering_queries.sql
├── Section_C_aggregation_queries.sql
├── Section_D_joins_queries.sql
├── Section_E_advanced_queries.sql
└── 00_setup.sql
```

**.gitignore content:**
```
*.db
*.sqlite
.DS_Store
*.swp
*.swo
node_modules/
```

---

## Best Practices

### SQL Writing Standards

1. **Naming Conventions**
   - Tables: lowercase with underscores (customers, order_items)
   - Columns: lowercase with underscores (first_name, order_date)
   - Aliases: Use meaningful abbreviations (c for customers, o for orders)

2. **Formatting**
   ```sql
   -- Good
   SELECT 
       customer_id,
       first_name,
       last_name
   FROM customers
   WHERE join_date >= '2024-01-01'
   ORDER BY customer_id;
   
   -- Bad
   select customer_id,first_name,last_name from customers where join_date>='2024-01-01' order by customer_id;
   ```

3. **Comments**
   ```sql
   -- Use comments for clarity
   -- but not for obvious code
   
   -- Bad comment (obvious)
   SELECT * FROM customers;  -- Selects all customers
   
   -- Good comment (explains why)
   -- Retrieve premium customers only (cost optimization)
   SELECT * FROM customers WHERE is_premium = TRUE;
   ```

4. **Readability**
   - One clause per line (SELECT, FROM, WHERE, etc.)
   - Capitalize SQL keywords (SELECT, FROM, WHERE)
   - Lowercase column and table names
   - Use aliases for complex queries
   - Group related conditions with parentheses

5. **Performance**
   - Use SARGABLE conditions
   - Filter early (WHERE before JOIN)
   - Select specific columns (not SELECT *)
   - Use indexes appropriately
   - Avoid functions on indexed columns

---

## FAQ

**Q: Can I use different SQL syntax than provided?**
A: Yes! The solutions show one approach. Multiple valid solutions exist. The important thing is understanding the concepts.

**Q: What if my results don't match exactly?**
A: Check data insertion. Verify all 25 INSERT statements executed successfully.

**Q: Should I memorize all the syntax?**
A: No. Focus on understanding concepts. Syntax varies slightly between databases.

**Q: How do I practice beyond this assignment?**
A: Modify queries (e.g., "Find orders > ₹5000"), create new questions, or explore with different filters.

**Q: Which database should I use?**
A: For learning: SQLite (easiest). For production: MySQL or PostgreSQL. All three are covered in this assignment.

---

## Additional Resources

### Official Documentation
- [MySQL Documentation](https://dev.mysql.com/doc/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [SQLite Documentation](https://www.sqlite.org/docs.html)

### Learning Resources
- SQL Joins: Visual Explanation
- ACID Properties: Detailed Guide
- Query Optimization: Performance Tips
- Transaction Management: Best Practices

### Tools
- **DBeaver:** Free SQL IDE (all databases)
- **MySQL Workbench:** MySQL-specific IDE
- **pgAdmin:** PostgreSQL-specific IDE
- **DB Browser for SQLite:** SQLite GUI

---

## Support

**If you get stuck:**

1. **Read the explanation** in the SQL file
2. **Check the expected output** to understand what should happen
3. **Test step-by-step** - break complex queries into smaller parts
4. **Review the schema** - ensure you understand table relationships
5. **Check data** - verify data was loaded correctly with SELECT COUNT(*) queries

---

## Summary Timeline

| Activity | Time | Cumulative |
|----------|------|-----------|
| Setup database | 5 min | 5 min |
| Section A | 15 min | 20 min |
| Section B | 20 min | 40 min |
| Section C | 25 min | 65 min |
| Section D | 30 min | 95 min |
| Section E | 35 min | 130 min |
| Review & Testing | 20 min | 150 min |
| **Total** | | **2.5 hours** |

---

## Conclusion

This assignment provides comprehensive coverage of SQL concepts from basics to advanced topics. By working through all sections, you'll develop practical database skills applicable to real-world scenarios.

**Remember:** SQL is a skill best learned by **doing**. Write queries, experiment, fail, fix, and learn!

---

**Assignment Created:** Celebal Summer Internship 2026  
**Week:** 2  
**Difficulty:** Beginner to Intermediate  
**Estimated Duration:** 2.5-3 hours

---

**Happy Learning! 🚀**
