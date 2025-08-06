# FDX Trading - Light Workflow Plan

## Core Components (Minimal)

### 1. Database (Azure PostgreSQL)
```
Already have:
- 23,206 suppliers
- 224 products  
- 85 requests
- 56 proposals
- All connected
```

### 2. Simple Python Functions
```python
# Just 5 basic functions:
search_product(term)      # Find products
match_suppliers(request)  # Match request to suppliers
create_proposal(data)     # Create proposal
track_status(id)         # Check status
generate_report()        # Simple report
```

### 3. Minimal UI Structure
```
/                   # Dashboard (1 page)
/search            # Search (1 page)
/workflow          # Workflow view (1 page)
/api/...           # API endpoints
```

### 4. Azure AI Integration
```python
# Simple AI functions:
ai_enhance(query)          # Enhance search
ai_match(request, supplier) # Match score
ai_suggest(data)           # Suggestions
```

## File Structure (Light)
```
FoodXchange/
├── app.py              # Main FastAPI app (100 lines)
├── db.py               # Database functions (50 lines)
├── ai.py               # Azure AI functions (30 lines)
├── templates/
│   ├── base.html       # Base template
│   ├── index.html      # Dashboard
│   └── search.html     # Search page
└── requirements.txt    # Dependencies
```

## Quick Start Plan

### Step 1: Core Functions (Today)
```python
# db.py - Just essentials
def get_connection()
def search(table, term)
def insert(table, data)
def update(table, id, data)
```

### Step 2: Simple API (Tomorrow)
```python
# app.py - Minimal endpoints
@app.get("/")           # Dashboard
@app.get("/search")     # Search
@app.post("/match")     # AI match
```

### Step 3: Basic UI (Day 3)
```html
<!-- Just Bootstrap + simple forms -->
<form>
  <input type="text" name="search">
  <button>Search</button>
</form>
```

## Workflow Steps (Simple)

```
1. SEARCH
   User types -> Search database -> Show results

2. MATCH  
   Request -> Find suppliers -> AI rank -> Show top 5

3. TRACK
   ID -> Get status -> Show progress
```

## Next Actions

- [ ] Create db.py with 4 functions
- [ ] Create app.py with 3 endpoints
- [ ] Create 1 HTML template
- [ ] Test with real data
- [ ] Add AI when ready

Keep it simple, make it work, then improve!