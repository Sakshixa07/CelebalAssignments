-- =====================================================================
-- SECTION A: SQL BASICS (SELECT, Constraints, Primary Keys)
-- =====================================================================
-- These questions test your understanding of basic data retrieval, 
-- table structure, and database constraints.
-- =====================================================================

-- ===================================================================
-- Q1. Display all columns and rows from the customers table
-- ===================================================================
-- Solution:
SELECT * FROM customers;

-- Explanation: The asterisk (*) is a wildcard that selects all columns.
-- This query retrieves all customer records with all their information.

-- ===================================================================
-- Q2. Retrieve only first_name, last_name, and city of all customers
-- ===================================================================
-- Solution:
SELECT first_name, last_name, city FROM customers;

-- Explanation: By specifying column names instead of *, we retrieve
-- only the required columns. This reduces network traffic and improves
-- query efficiency.

-- ===================================================================
-- Q3. List all unique categories available in the products table
-- ===================================================================
-- Solution:
SELECT DISTINCT category FROM products;

-- Explanation: The DISTINCT keyword eliminates duplicate values.
-- From the sample data, we have 3 categories: Electronics, Clothing, Home.

-- ===================================================================
-- Q4. Identify the Primary Key of each table (Explanation)
-- ===================================================================
-- Answer:
-- Table         | Primary Key Column
-- ------------- | ------------------
-- customers     | customer_id
-- products      | product_id
-- orders        | order_id
-- order_items   | item_id

-- Why Primary Key must be UNIQUE and NOT NULL:
-- 1. UNIQUE: Ensures no two rows can have the same primary key value.
--    This prevents duplicate records and allows reliable row identification.
-- 2. NOT NULL: A primary key must always have a value. Without it, we
--    cannot uniquely identify a record.
-- 
-- Benefit: Enforces data integrity and enables efficient indexing for
-- fast lookups and joins.

-- ===================================================================
-- Q5. What constraints are applied to the email column?
-- ===================================================================
-- Solution Query to check constraints:
DESCRIBE customers;
-- OR in PostgreSQL:
-- \d customers

-- Answer:
-- Constraints on email column:
-- 1. VARCHAR(100) - Limits string length to 100 characters
-- 2. UNIQUE - No two customers can have the same email
-- 3. NOT NULL - Email must always have a value
--
-- What happens if you try to insert duplicate email?
-- ERROR: Duplicate entry for key 'email'
-- The database will REJECT the insert statement and rollback the operation.
-- This ensures that each customer has a unique email address.

-- ===================================================================
-- Q6. Try inserting a product with unit_price = -50
-- ===================================================================
-- Incorrect INSERT (This will FAIL):
-- INSERT INTO products VALUES
-- (999, 'Test Product', 'Electronics', 'TestBrand', -50.00, 100);
--
-- Error Message:
-- ERROR 3819 (HY000): Check constraint 'products_chk_1' violation
-- OR similar constraint violation message depending on your RDBMS
--
-- Constraint that prevents it:
-- CHECK (unit_price > 0)
-- 
-- Explanation:
-- The CHECK constraint in the products table enforces business logic.
-- A negative price doesn't make sense in a real-world e-commerce scenario.
-- The database automatically validates this constraint before allowing
-- the insert, protecting data integrity at the database level.
--
-- Valid INSERT (This will SUCCEED):
INSERT INTO products VALUES
(999, 'Test Product', 'Electronics', 'TestBrand', 50.00, 100);

-- Verify the insert
SELECT * FROM products WHERE product_id = 999;

-- Clean up (optional):
DELETE FROM products WHERE product_id = 999;

-- ===================================================================
-- SUMMARY OF SECTION A CONCEPTS
-- ===================================================================
-- 1. SELECT * - Retrieves all columns
-- 2. SELECT column1, column2 - Retrieves specific columns
-- 3. DISTINCT - Removes duplicate values
-- 4. PRIMARY KEY - Uniquely identifies each row
-- 5. UNIQUE - Ensures uniqueness of values
-- 6. NOT NULL - Enforces that a column must have a value
-- 7. CHECK - Validates data based on a condition
-- 8. Constraints protect data integrity and enforce business rules

-- ===================================================================
-- END OF SECTION A
-- ===================================================================
