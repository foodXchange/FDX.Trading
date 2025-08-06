# FDX Trading - Database Workflow & Relationships Plan

## 📊 Current Database Status
- **Total Tables**: 39
- **Total Records**: 26,306+ records
- **Location**: Poland Central (fdx-poland-db)

## 🔄 Core Business Workflow

### 1️⃣ **SOURCING WORKFLOW**
```
Buyers → Requests → Request Line Items → Suppliers
```

**Tables Involved:**
- `buyers` (22 records) - Companies requesting products
- `requests` (85 records) - RFQs from buyers
- `request_line_items` (218 records) - Specific products needed
- `suppliers` (23,206 records) - Potential suppliers

**Key Relationships:**
- Request belongs to Buyer (buyer_id)
- Request has many Request Line Items (request_id)
- Request Line Items describe Products needed

---

### 2️⃣ **PROPOSAL WORKFLOW**
```
Requests → Proposals → Proposal Line Items → Sampling
```

**Tables Involved:**
- `proposals_samples` (56 records) - Supplier responses to RFQs
- `proposal_line_items` (77 records) - Specific product offers
- `sampling_request` (77 records) - Sample requests for testing

**Key Relationships:**
- Proposal responds to Request (request_id)
- Proposal from Supplier (supplier_id)
- Proposal has many Line Items (proposal_id)
- Samples linked to Proposals

---

### 3️⃣ **PRODUCT MANAGEMENT**
```
Products Category → Products → Price Book
```

**Tables Involved:**
- `products_category` (430 records) - Product categorization
- `products` (224 records) - Product catalog
- `price_book` (218 records) - Pricing information

**Key Relationships:**
- Product belongs to Category (category_id)
- Price Book references Product (product_id)
- Price Book has Supplier pricing (supplier_id)

---

### 4️⃣ **ADAPTATION WORKFLOW**
```
Proposals → Adaptation Process → Compliance/Kosher/Graphics
```

**Tables Involved:**
- `adaptation_process` (67 records) - Main adaptation tracking
- `compliance_process` (88 records) - Regulatory compliance
- `kosher_process` (74 records) - Kosher certification
- `graphics_process` (96 records) - Packaging/labeling
- `adaptation_steps` (22 records) - Process steps

**Key Relationships:**
- Adaptation linked to Product (product_id)
- Sub-processes linked to main Adaptation (adaptation_id)
- Steps track progress

---

### 5️⃣ **ORDER FULFILLMENT**
```
Proposals → Contracts → Orders → Order Line Items → Shipping
```

**Tables Involved:**
- `contracts` (2 records) - Signed agreements
- `orders` (166 records) - Purchase orders
- `order_line_items` (549 records) - Order details
- `shipping` (271 records) - Logistics tracking

**Key Relationships:**
- Contract between Buyer and Supplier
- Order references Contract (contract_id)
- Order has many Line Items (order_id)
- Shipping tracks Order delivery (order_id)

---

### 6️⃣ **FINANCIAL WORKFLOW**
```
Orders → Invoices → Commission Rates
```

**Tables Involved:**
- `invoices` (263 records) - Billing documents
- `commission_rates` (49 records) - Commission structure

**Key Relationships:**
- Invoice for Order (order_id)
- Commission calculated from Order value
- Commission Rate per Buyer/Supplier pair

---

### 7️⃣ **SUPPORTING ENTITIES**
```
Contractors - External service providers (46 records)
```

---

## 🎯 Next Steps for Implementation

### Phase 1: Core Relationships
1. Link Buyers ↔ Requests
2. Link Suppliers ↔ Products
3. Link Requests ↔ Proposals

### Phase 2: Product Flow
1. Link Products ↔ Categories
2. Link Products ↔ Price Book
3. Link Proposals ↔ Products

### Phase 3: Order Management
1. Link Orders ↔ Buyers/Suppliers
2. Link Orders ↔ Products
3. Link Orders ↔ Shipping

### Phase 4: Compliance & Adaptation
1. Link Adaptation ↔ Products
2. Link Sub-processes ↔ Main Adaptation
3. Track status workflows

### Phase 5: Financial
1. Link Invoices ↔ Orders
2. Calculate commissions
3. Track payments

---

## 🔑 Key Questions to Address:

1. **Primary Keys**: What are the unique identifiers in each table?
2. **Status Tracking**: How do we track workflow progress?
3. **User Roles**: Who can access/modify what?
4. **Automation**: Which workflows should be automated?
5. **Reporting**: What analytics/dashboards are needed?

---

## 📈 Workflow Priority

**High Priority:**
- Buyer → Request → Proposal → Order flow
- Product catalog and pricing
- Supplier management

**Medium Priority:**
- Adaptation/compliance tracking
- Shipping and logistics
- Invoice management

**Low Priority:**
- Commission calculations
- Contractor management
- Advanced analytics

---

## 🚀 Implementation Approach

We'll build this step-by-step:
1. **Map existing data** - Understand current structure
2. **Create foreign keys** - Link related tables
3. **Build views** - Simplify complex queries
4. **Add indexes** - Optimize performance
5. **Create APIs** - Enable application access
6. **Build UI** - User-friendly interfaces
7. **Add automation** - Workflow triggers

Ready to start with Phase 1?