# Step-by-Step Workflow Implementation Plan

## Current Status Check

### ✅ What's Working Now:
1. **Database Connection**: Poland PostgreSQL is live
2. **Data Imported**: All 46 tables with 26,306+ records
3. **Basic Links**: 222 supplier-product connections established
4. **Views Created**: v_buyer_activity, v_supplier_catalog

### 🔍 Let's Test Each Component Step by Step

---

## STEP 1: Test Database Connection
```python
# Test if we can connect and query
psql "postgresql://fdxadmin:FoodXchange2024@fdx-poland-db.postgres.database.azure.com/foodxchange?sslmode=require"

# Check tables
\dt

# Count records
SELECT COUNT(*) FROM suppliers;  -- Should show 23,206
SELECT COUNT(*) FROM buyers;      -- Should show 22
```

---

## STEP 2: Test Buyer Workflow

### 2.1 Check Buyers
```sql
-- See all buyers
SELECT id, buyer_name, company_name, country 
FROM buyers 
LIMIT 5;
```

### 2.2 Check Requests
```sql
-- See requests (RFQs)
SELECT data->>'Buyer' as buyer, 
       data->>'Request' as request,
       data->>'Status' as status
FROM requests_raw 
LIMIT 5;
```

### 2.3 Link Buyers to Requests
```python
# Small test: Link first 5 buyers to their requests
# We'll create a simple script to test this
```

---

## STEP 3: Test Supplier Workflow

### 3.1 Check Suppliers
```sql
-- Top suppliers by country
SELECT country, COUNT(*) as count 
FROM suppliers 
WHERE country IS NOT NULL 
GROUP BY country 
ORDER BY count DESC 
LIMIT 5;
```

### 3.2 Check Products
```sql
-- Products with suppliers
SELECT spl.product_data->>'Product Name' as product,
       s.supplier_name,
       s.country
FROM supplier_product_links spl
JOIN suppliers s ON s.id = spl.supplier_id
LIMIT 10;
```

---

## STEP 4: Small Working Examples

### Example 1: Find Italian Food Suppliers
```python
# Query: Show me Italian suppliers with products
SELECT s.supplier_name, s.country,
       COUNT(spl.id) as product_count
FROM suppliers s
JOIN supplier_product_links spl ON s.id = spl.supplier_id
WHERE s.country = 'Italy'
GROUP BY s.supplier_name, s.country
ORDER BY product_count DESC
LIMIT 10;
```

### Example 2: Track a Request Pipeline
```python
# Follow one request from buyer to proposal
SELECT 
    data->>'Buyer' as buyer,
    data->>'Request' as request_name,
    data->>'Status' as status,
    data->>'Request Date' as request_date
FROM requests_raw
WHERE data->>'Buyer' IS NOT NULL
LIMIT 1;
```

### Example 3: Product Catalog for One Supplier
```python
# Show all products from La Doria
SELECT 
    product_data->>'Product Name' as product,
    product_data->>'Unit Wholesale Price (latest)' as price,
    product_data->>'Unit of Measure' as unit
FROM supplier_product_links spl
JOIN suppliers s ON s.id = spl.supplier_id
WHERE s.supplier_name LIKE '%La Doria%';
```

---

## STEP 5: Build One Complete Workflow

### Mini Project: "Olive Oil Request"

#### Step 5.1: Create a Request
```python
# A buyer wants olive oil
# 1. Find olive oil suppliers
SELECT DISTINCT s.supplier_name, s.country, s.company_email
FROM suppliers s
WHERE s.products LIKE '%olive oil%'
   OR s.product_categories LIKE '%oil%'
LIMIT 10;
```

#### Step 5.2: Check Prices
```python
# 2. Get olive oil prices
SELECT 
    data->>'Product' as product,
    data->>'Supplier' as supplier,
    data->>'Unit Wholesale Price (latest)' as price
FROM price_book_raw
WHERE data->>'Product' LIKE '%olive%'
   OR data->>'Product' LIKE '%oil%';
```

#### Step 5.3: Create Proposal
```python
# 3. Match suppliers to request
# This would create a new proposal linking:
# - Buyer (from buyers table)
# - Request (from requests)
# - Supplier (from suppliers)
# - Product & Price (from products/price_book)
```

---

## STEP 6: Verification Checklist

### Quick Health Checks:
- [ ] Can connect to database
- [ ] Can query suppliers table
- [ ] Can query buyers table
- [ ] Can see product links
- [ ] Can search by country
- [ ] Can search by product type
- [ ] Can track a request

### Data Quality Checks:
- [ ] Buyers have names and emails
- [ ] Suppliers have products listed
- [ ] Products have prices
- [ ] Requests have buyers
- [ ] Orders have suppliers

---

## STEP 7: Next Small Steps

### Immediate Actions (10 minutes each):

1. **Fix Missing Buyer Links**
   - Many requests don't have buyer links
   - Need to improve matching algorithm

2. **Add Search Function**
   - Create simple product search
   - Search suppliers by product type

3. **Create Price Comparison**
   - Compare prices for same product
   - Different suppliers

4. **Build Status Dashboard**
   - How many open requests?
   - How many pending proposals?
   - How many active orders?

---

## Commands to Run Now:

```bash
# 1. Connect to database
psql "postgresql://fdxadmin:FoodXchange2024@fdx-poland-db.postgres.database.azure.com/foodxchange?sslmode=require"

# 2. Check basic counts
SELECT 
    (SELECT COUNT(*) FROM suppliers) as suppliers,
    (SELECT COUNT(*) FROM buyers) as buyers,
    (SELECT COUNT(*) FROM products_raw) as products,
    (SELECT COUNT(*) FROM orders_raw) as orders;

# 3. Test a view
SELECT * FROM v_supplier_catalog LIMIT 5;

# 4. Find specific product
SELECT * FROM supplier_product_links 
WHERE product_data::text ILIKE '%pasta%' 
LIMIT 5;
```

---

## Ready to Test?

Let's start with **Step 1** - test the database connection and verify our counts are correct.