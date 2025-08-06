# COMPLETE FDX WORKFLOW
## RFQ → Negotiation → Adaptation → Order

---

## 🔄 REALISTIC BUSINESS FLOW

### **THE TRUTH: "It never happens on initial price"**

```
RFQ Sent → Quote Received → ❌ Never Accept First Price
         ↓
    NEGOTIATION (3-10 emails)
         ↓
    ACCEPTANCE 
         ↓
    ADAPTATION STAGE (Product customization)
         ↓
    ORDER MODULE
```

---

## 📧 STAGE 1: RFQ & INITIAL QUOTE

### **Email #1 - RFQ to Supplier:**
```
Subject: RFQ - Sunflower Oil 5000 bottles

Dear Supplier,
Buyer needs: Sunflower Oil 1L
Quantity: 5000/month
Target price: $3.00
[Reply with quote]
```

### **Email #2 - Supplier Quotes:**
```
"We can offer $3.50 per bottle, MOQ 2000"
```

### **System Action:**
- AI extracts: Price=$3.50, MOQ=2000
- Status: INITIAL_QUOTE_RECEIVED
- Buyer gets notification

---

## 💬 STAGE 2: NEGOTIATION (The Real Work)

### **Email #3 - Buyer Negotiates:**
```
To: Supplier
"Your price is too high. Competitor offers $3.20.
Can you match? We can commit to 12 months."

[AI Detects: NEGOTIATING_PRICE, VOLUME_COMMITMENT]
```

### **Email #4 - Supplier Counter:**
```
"For 12-month contract, we can do $3.25
Plus free shipping on orders >3000 units"

[AI Detects: COUNTER_OFFER, INCENTIVE_ADDED]
```

### **Email #5-10 - Back & Forth:**
```
Buyer: "Need samples first"
Supplier: "Samples sent via DHL, tracking #123"
Buyer: "Quality good, but need custom labeling"
Supplier: "Custom label adds $0.05/unit"
Buyer: "If you include labeling at $3.25, we have deal"
Supplier: "Agreed. $3.25 with custom label"
```

### **AI Tracking Each Email:**
```python
negotiation_thread = {
    "email_1": {"type": "RFQ", "status": "sent"},
    "email_2": {"type": "QUOTE", "price": 3.50},
    "email_3": {"type": "NEGOTIATE", "target": 3.20},
    "email_4": {"type": "COUNTER", "price": 3.25},
    "email_5": {"type": "SAMPLE_REQUEST"},
    "email_6": {"type": "SAMPLE_SENT"},
    "email_7": {"type": "CUSTOMIZATION_REQUEST"},
    "email_8": {"type": "CUSTOMIZATION_PRICE"},
    "email_9": {"type": "FINAL_NEGOTIATION"},
    "email_10": {"type": "AGREEMENT", "final_price": 3.25}
}
```

---

## ✅ STAGE 3: ACCEPTANCE

### **Buyer Decision Email:**
```
"We accept your offer:
- $3.25/bottle
- Custom labeling included
- 12-month contract
- Monthly orders 5000 units

Please proceed with adaptation."
```

### **System Actions:**
```python
def on_acceptance(email):
    # 1. Lock the price
    agreed_terms = {
        "price": 3.25,
        "quantity": 5000,
        "frequency": "monthly",
        "customization": "labeling",
        "contract_length": "12 months"
    }
    
    # 2. Move to adaptation
    create_adaptation_project(agreed_terms)
    
    # 3. Notify both parties
    send_confirmation_emails()
```

---

## 🔧 STAGE 4: ADAPTATION (Product Customization)

### **What Happens in Adaptation:**

1. **Label Design**
   ```
   Buyer uploads: label_design.pdf
   Supplier reviews: "Need higher resolution"
   Buyer sends: label_design_v2.pdf
   Supplier: "Approved for printing"
   ```

2. **Packaging Specs**
   ```
   - Bottle type: PET clear
   - Cap: White screw cap
   - Box: 12 bottles/box
   - Pallet: 60 boxes/pallet
   ```

3. **Quality Standards**
   ```
   - Acidity: <0.8%
   - Peroxide: <10
   - Certificates: ISO, HACCP
   - Lab tests: Required
   ```

4. **Logistics Details**
   ```
   - Delivery: FOB Shanghai
   - Port: Haifa, Israel
   - Schedule: 15th each month
   - Payment: 30% advance, 70% on BL
   ```

### **Adaptation Tracking:**
```python
adaptation_checklist = {
    "label_design": "approved",
    "packaging_specs": "confirmed",
    "quality_standards": "agreed",
    "logistics": "arranged",
    "sample_approval": "pending",
    "production_ready": False
}
```

---

## 📦 STAGE 5: ORDERS MODULE

### **After Adaptation Complete:**

**First Order Creation:**
```python
order = {
    "number": "PO-2024-001",
    "supplier": "Global Oils Ltd",
    "buyer": "Shufersal",
    "product": "Sunflower Oil 1L Custom Label",
    "quantity": 5000,
    "unit_price": 3.25,
    "total": 16250.00,
    "terms": agreed_terms,
    "status": "pending_production"
}
```

### **Order Lifecycle:**
```
Created → Confirmed → Production → Shipping → Delivered → Paid
```

### **Monthly Repeat Orders:**
```python
def create_monthly_order():
    # Automatic based on contract
    new_order = copy(master_agreement)
    new_order["number"] = generate_po_number()
    new_order["delivery_date"] = next_month_15th()
    return new_order
```

---

## 🎯 COMPLETE WORKFLOW IN SYSTEM

### **Database Structure:**
```sql
-- Main workflow tracking
CREATE TABLE workflows (
    id SERIAL PRIMARY KEY,
    buyer_id INT,
    supplier_id INT,
    product TEXT,
    stage VARCHAR(50), -- 'rfq', 'negotiation', 'adaptation', 'ordering'
    status VARCHAR(50),
    created_at TIMESTAMP
);

-- Negotiation emails
CREATE TABLE negotiation_threads (
    workflow_id INT,
    email_number INT,
    sender VARCHAR(20), -- 'buyer' or 'supplier'
    content TEXT,
    ai_intent VARCHAR(50),
    extracted_data JSONB,
    timestamp TIMESTAMP
);

-- Agreed terms
CREATE TABLE agreements (
    workflow_id INT,
    final_price DECIMAL,
    quantity INT,
    terms JSONB,
    accepted_at TIMESTAMP
);

-- Adaptation tasks
CREATE TABLE adaptation_tasks (
    workflow_id INT,
    task_name VARCHAR(100),
    status VARCHAR(50),
    documents JSONB,
    completed_at TIMESTAMP
);

-- Orders
CREATE TABLE orders (
    workflow_id INT,
    order_number VARCHAR(50),
    amount DECIMAL,
    status VARCHAR(50),
    created_at TIMESTAMP
);
```

---

## 🚀 MVP IMPLEMENTATION PLAN

### **Phase 1: Email Negotiation (NOW)**
- Capture email threads
- AI intent detection
- Price extraction
- Show negotiation progress

### **Phase 2: Acceptance Flow**
- "Accept" button after negotiation
- Lock agreed terms
- Generate agreement document

### **Phase 3: Simple Adaptation**
- Checklist of requirements
- Document uploads
- Status tracking

### **Phase 4: Order Generation**
- Create from agreement
- Monthly recurrence
- Order tracking

---

## 📊 BUYER DASHBOARD VIEW

```
PROJECT: Sunflower Oil - Shufersal

[====|-------|---------|--------]
  RFQ  NEGOT   ADAPT    ORDERS
       ↑ Current Stage

NEGOTIATION PROGRESS:
📧 10 emails exchanged
💰 Price: $3.50 → $3.25 (7% reduction)
📦 Terms: 12-month contract agreed
✅ Ready for adaptation

[View Thread] [Accept Terms] [Request Changes]
```

---

## 🤖 AI PROMPTS FOR EACH STAGE

### **Negotiation Analysis:**
```python
prompt = """
Analyze this email and determine:
1. Is buyer negotiating price? (YES/NO)
2. What's the target price mentioned?
3. Any conditions offered? (volume, duration)
4. Urgency level (HIGH/MEDIUM/LOW)
5. Next recommended action
"""
```

### **Acceptance Detection:**
```python
prompt = """
Does this email indicate acceptance?
Extract:
- Accepted price
- Quantity commitment
- Special terms
- Start date
Return: ACCEPTED or STILL_NEGOTIATING
```
```

---

**This is the REAL workflow - negotiation always happens, then adaptation, then orders!**