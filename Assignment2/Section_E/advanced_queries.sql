-- =====================================================================
-- SECTION E: ADVANCED CONCEPTS (CASE, ACID, Transactions)
-- =====================================================================
-- These questions test your understanding of conditional logic, 
-- database reliability principles, and transaction management.
-- =====================================================================

-- ===================================================================
-- Q24. CASE Statement for Price Tier Classification
-- ===================================================================
-- Solution:
SELECT 
    product_id,
    product_name,
    category,
    unit_price,
    CASE 
        WHEN unit_price < 1000 THEN 'Budget'
        WHEN unit_price BETWEEN 1000 AND 3000 THEN 'Mid-Range'
        WHEN unit_price > 3000 THEN 'Premium'
    END AS price_tier
FROM products
ORDER BY unit_price;

-- Explanation:
-- - CASE statement provides conditional logic (like IF-ELSE)
-- - WHEN checks each condition in order
-- - First matching condition is used
-- - ELSE clause is optional (NULLs if no match)
-- - Expected results:
--   Budget (< ₹1000): Cotton T-Shirt, Laptop Stand, Cushion Covers
--   Mid-Range (₹1000-3000): Wireless Earbuds, Bedsheet Set, Smart Watch
--   Premium (> ₹3000): Running Shoes, Bluetooth Speaker

-- Version with ELSE clause:
SELECT 
    product_id,
    product_name,
    unit_price,
    CASE 
        WHEN unit_price < 1000 THEN 'Budget'
        WHEN unit_price BETWEEN 1000 AND 3000 THEN 'Mid-Range'
        WHEN unit_price > 3000 THEN 'Premium'
        ELSE 'Uncategorized'
    END AS price_tier
FROM products
ORDER BY unit_price;

-- ===================================================================
-- Q25. CASE in Aggregate Function - Count Delivered vs Not Delivered
-- ===================================================================
-- Solution:
SELECT 
    SUM(CASE WHEN status = 'Delivered' THEN 1 ELSE 0 END) AS delivered_orders,
    SUM(CASE WHEN status != 'Delivered' THEN 1 ELSE 0 END) AS not_delivered_orders,
    COUNT(*) AS total_orders,
    ROUND(
        SUM(CASE WHEN status = 'Delivered' THEN 1 ELSE 0 END) * 100.0 / COUNT(*),
        2
    ) AS delivery_rate_percent
FROM orders;

-- Explanation:
-- - CASE inside SUM counts matching conditions
-- - CASE returns 1 for match, 0 for non-match
-- - SUM adds up all 1s to get count
-- - Expected result: 6 delivered, 4 not delivered (60% delivery rate)

-- Alternative cleaner syntax:
SELECT 
    SUM(CASE WHEN status = 'Delivered' THEN 1 END) AS delivered_orders,
    SUM(CASE WHEN status != 'Delivered' THEN 1 END) AS not_delivered_orders,
    COUNT(*) AS total_orders
FROM orders;

-- More detailed breakdown by status:
SELECT 
    SUM(CASE WHEN status = 'Delivered' THEN 1 ELSE 0 END) AS delivered,
    SUM(CASE WHEN status = 'Shipped' THEN 1 ELSE 0 END) AS shipped,
    SUM(CASE WHEN status = 'Pending' THEN 1 ELSE 0 END) AS pending,
    SUM(CASE WHEN status = 'Cancelled' THEN 1 ELSE 0 END) AS cancelled,
    COUNT(*) AS total
FROM orders;

-- ===================================================================
-- Q26. Explain ACID Properties with Real-World Examples
-- ===================================================================

-- ANSWER: ACID PROPERTIES EXPLAINED
-- =================================================================

-- A - ATOMICITY
-- =========================================================================
-- Definition: "All or Nothing" - A transaction either completes 
-- entirely or not at all. No partial updates.
--
-- Real-World Example: Bank Transfer
-- ------
-- Scenario: Transfer ₹1000 from Account A to Account B
-- 
-- Steps:
-- 1. Debit ₹1000 from Account A
-- 2. Credit ₹1000 to Account B
--
-- WITHOUT Atomicity (Dangerous):
-- - If server crashes after Step 1, money disappears!
-- - Account A loses ₹1000, Account B doesn't gain it
-- - ₹1000 vanishes from the system
--
-- WITH Atomicity (Safe):
-- - Database treats both steps as ONE unit
-- - If Step 2 fails, Step 1 is rolled back
-- - Either BOTH succeed or BOTH fail
-- - Money never disappears
-- - Integrity of financial records maintained
--
-- Why it matters: Prevents data corruption and financial fraud

-- C - CONSISTENCY
-- =========================================================================
-- Definition: Database moves from one valid state to another.
-- All constraints, rules, and relationships are maintained.
--
-- Real-World Example: Online Shopping Order
-- ------
-- Business Rules:
-- - Customer balance must be sufficient
-- - Product stock must be available
-- - Order total must match item sum
-- - Delivered orders have ship dates
--
-- INCONSISTENT State (Should never happen):
-- - Order created but payment not processed
-- - Stock reduced but order status is "Pending"
-- - Order total doesn't match items
-- - Customer balance is negative
--
-- CONSISTENT State (Database validates):
-- - Order only exists if payment succeeded
-- - Stock only reduced if order is "Confirmed"
-- - Order total = SUM of items
-- - Customer balance always >= 0
-- - All foreign keys point to valid records
--
-- Why it matters: Prevents invalid data and maintains trust

-- I - ISOLATION
-- =========================================================================
-- Definition: Concurrent transactions don't interfere with each other.
-- Each transaction works as if it's the only one running.
--
-- Real-World Example: Airplane Seat Booking
-- ------
-- Scenario: Two customers book Seat 12A simultaneously
--
-- WITHOUT Isolation (Race condition):
-- Time | Customer 1        | Customer 2        | Seat Status
-- -----|-------------------|-------------------|----------
-- 1    | Check Seat 12A    | Check Seat 12A    | Available
-- 2    | See it's available| See it's available| Available  
-- 3    | Book Seat 12A     | (doesn't see C1)  | Booked (C1)
-- 4    | Confirms booking  | Book Seat 12A     | Booked (C2)
--      | OVERBOOKING!      | Confirms booking  | (Both think they have it!)
--
-- WITH Isolation (Locked):
-- - Transaction 1 locks Seat 12A
-- - Transaction 2 waits until Transaction 1 completes
-- - Only one can book the seat
-- - No overbooking
-- - Both customers see accurate availability
--
-- Isolation Levels:
-- - READ UNCOMMITTED: Reads dirty data (dangerous)
-- - READ COMMITTED: Default, safe for most applications
-- - REPEATABLE READ: Prevents phantom reads
-- - SERIALIZABLE: Strictest, slowest
--
-- Why it matters: Prevents race conditions and double-booking

-- D - DURABILITY
-- =========================================================================
-- Definition: Once a transaction is committed, it persists permanently.
-- Data survives system failures, crashes, power outages.
--
-- Real-World Example: Saving a Bank Deposit
-- ------
-- Scenario: You deposit ₹5000 into your account
--
-- WITHOUT Durability (Risky):
-- - Transaction commits
-- - Money appears in your account
-- - Server crashes 2 minutes later
-- - Database loses the transaction
-- - Money disappears from your account
-- - Your account balance goes back to before deposit
-- - Loss of ₹5000 with no proof of transaction
--
-- WITH Durability (Safe):
-- - Transaction commits and writes to persistent storage
-- - Data written to disk/SSD (not just RAM)
-- - Even if server crashes immediately after commit
-- - Data persists and recovers after restart
-- - Your ₹5000 is safe and traceable
-- - Can retrieve transaction logs as proof
--
-- Implementation:
-- - Write-ahead logging (WAL)
-- - Disk mirroring/RAID
-- - Regular backups
-- - Transaction logs
--
-- Why it matters: Guarantees permanent record of critical operations

-- ===================================================================
-- COMPLETE ACID EXAMPLE: Simulated Transfer Transaction
-- ===================================================================

-- Sample Schema for accounts:
-- CREATE TABLE accounts (
--     account_id INT PRIMARY KEY,
--     account_holder VARCHAR(100),
--     balance DECIMAL(12,2) CHECK (balance >= 0)
-- );

-- Example transaction (pseudo-code, actual syntax varies by DB):
-- BEGIN TRANSACTION;  -- Start ACID transaction (Atomicity)
--
-- -- Consistency: Verify preconditions
-- SELECT balance FROM accounts WHERE account_id = 101 FOR UPDATE;
-- -- (Check that balance >= 1000)
--
-- -- Isolation: Locks prevent other transactions from interfering
-- UPDATE accounts SET balance = balance - 1000 WHERE account_id = 101;
-- UPDATE accounts SET balance = balance + 1000 WHERE account_id = 102;
--
-- -- Durability: Once COMMIT completes, changes persist
-- COMMIT;  -- All changes written to disk permanently
--
-- If any step fails:
-- ROLLBACK;  -- Undo all changes, money stays where it is

-- ===================================================================
-- Q27. SQL Transaction - Order with Order Items and Stock Update
-- ===================================================================

-- Important Note: The syntax varies by database system
-- MySQL: Use START TRANSACTION or BEGIN
-- PostgreSQL: Use BEGIN
-- SQL Server: Use BEGIN TRANSACTION

-- SOLUTION FOR MYSQL:
-- ===================================================================

-- Step 1: Check current stock levels BEFORE transaction
SELECT product_id, product_name, stock_qty FROM products WHERE product_id IN (201, 206);

-- Step 2: Execute transaction (Atomically)
START TRANSACTION;

-- Insert new order
INSERT INTO orders (order_id, customer_id, order_date, status, total_amount)
VALUES (1011, 102, CURDATE(), 'Pending', 1598.00);

-- Insert order items (2 products)
INSERT INTO order_items (item_id, order_id, product_id, quantity, unit_price, discount_pct)
VALUES 
(5016, 1011, 201, 1, 1499.00, 0),      -- 1x Wireless Earbuds
(5017, 1011, 206, 1, 1299.00, 0);      -- 1x Bedsheet Set

-- Update stock after purchase (Decrement quantities)
UPDATE products SET stock_qty = stock_qty - 1 WHERE product_id = 201;  -- Earbuds: 250 -> 249
UPDATE products SET stock_qty = stock_qty - 1 WHERE product_id = 206;  -- Bedsheet: 300 -> 299

-- Commit transaction (All changes persist)
COMMIT;

-- Step 3: Verify transaction success
SELECT 'Order after transaction' AS verification;
SELECT * FROM orders WHERE order_id = 1011;
SELECT * FROM order_items WHERE order_id = 1011;
SELECT product_id, product_name, stock_qty FROM products WHERE product_id IN (201, 206);

-- ===================================================================
-- TRANSACTION WITH ERROR HANDLING (ROLLBACK)
-- ===================================================================

-- Scenario: Purchase with error detection and rollback
START TRANSACTION;

DECLARE @order_total DECIMAL(12,2);

-- Insert order
INSERT INTO orders (order_id, customer_id, order_date, status, total_amount)
VALUES (1012, 103, CURDATE(), 'Pending', 2798.00);

-- Check if order insert succeeded (simplified check)
-- In production, you'd validate input more thoroughly

INSERT INTO order_items (item_id, order_id, product_id, quantity, unit_price, discount_pct)
VALUES 
(5018, 1012, 203, 1, 2999.00, 0);  -- Smart Watch (product_id=203)

-- Try to reduce stock, but check for insufficient inventory
-- Simulate error: If stock would go negative, trigger rollback
IF ((SELECT stock_qty FROM products WHERE product_id = 203) < 1) THEN
    -- Insufficient stock - ROLLBACK entire transaction
    ROLLBACK;
    SELECT 'ERROR: Insufficient stock. Transaction rolled back.' AS error_message;
ELSE
    -- Proceed with stock update
    UPDATE products SET stock_qty = stock_qty - 1 WHERE product_id = 203;
    COMMIT;
    SELECT 'SUCCESS: Order completed and stock updated.' AS success_message;
END IF;

-- Verify (should not have created order 1012 if rollback occurred)
SELECT COUNT(*) AS orders_with_id_1012 FROM orders WHERE order_id = 1012;

-- ===================================================================
-- SAVEPOINT EXAMPLE (Nested Transactions)
-- ===================================================================

-- Note: MySQL requires specific settings for savepoints
START TRANSACTION;

INSERT INTO orders (order_id, customer_id, order_date, status, total_amount)
VALUES (1013, 104, CURDATE(), 'Pending', 1500.00);

-- Save a point (can rollback to here without rolling back entire transaction)
SAVEPOINT order_inserted;

INSERT INTO order_items (item_id, order_id, product_id, quantity, unit_price, discount_pct)
VALUES (5019, 1013, 205, 1, 3499.00, 0);

-- If error occurs here, rollback to just before order_items insert
-- ROLLBACK TO SAVEPOINT order_inserted;
-- Then you could insert different items

-- Or commit everything
COMMIT;

-- ===================================================================
-- CLEANUP (Optional - Delete test transactions)
-- ===================================================================
DELETE FROM order_items WHERE order_id IN (1011, 1012, 1013);
DELETE FROM orders WHERE order_id IN (1011, 1012, 1013);

-- ===================================================================
-- BEST PRACTICES FOR TRANSACTIONS
-- ===================================================================
-- 1. Keep transactions short - Lock tables for minimal time
-- 2. Use appropriate isolation levels - Balance consistency vs performance
-- 3. Handle errors gracefully - Use try-catch or error checking
-- 4. Avoid nested transactions when possible - Increases complexity
-- 5. Use savepoints for complex logic - Allow partial rollback
-- 6. Log transactions - For audit trails and debugging
-- 7. Test rollback scenarios - Ensure error handling works
-- 8. Monitor long-running transactions - Prevent table locks

-- ===================================================================
-- END OF SECTION E
-- ===================================================================
