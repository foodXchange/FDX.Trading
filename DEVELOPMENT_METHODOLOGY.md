# FDX DEVELOPMENT METHODOLOGY
## Working with Claude as Your Development Angel

Last Updated: 2025-08-06
VM: 74.248.141.31 | DB: Poland PostgreSQL

---

## 🎯 CORE PRINCIPLE: PRESERVE CONTEXT

### When Starting Each Session
1. **ALWAYS START WITH**: "Continue from DEVELOPMENT_METHODOLOGY.md"
2. **REFERENCE CURRENT PROJECT**: "Working on Sunflower Oil workflow"
3. **MENTION SPECIFIC FILES**: "Using sunflower_oil_project.py"

### What to Say to Claude
```
Continue from DEVELOPMENT_METHODOLOGY.md
Working on: [specific task]
Using files: [list files]
VM: 74.248.141.31
```

---

## 📁 PROJECT STRUCTURE

### Critical Files to Maintain
```
FoodXchange/
├── DEVELOPMENT_METHODOLOGY.md     # THIS FILE - Always update
├── PROJECT_STATE.md              # Current project status
├── WORKFLOW_TRACKER.md           # Sunflower Oil progress
├── sunflower_oil_project.py      # Core workflow logic
├── workflow_app.py               # FastAPI application
├── workflow_template.py          # Reusable templates
└── vm_implementation_plan.py     # VM deployment guide
```

### Database References
```python
POLAND_DB = "postgresql://fdxadmin:FoodXchange2024@fdx-poland-db.postgres.database.azure.com/foodxchange?sslmode=require"

# Key IDs - NEVER LOSE THESE
SUNFLOWER_PROJECT = {
    "request_id": 28,
    "proposal_id": 63, 
    "order_id": "SHF-20250806-28",
    "buyer": "Shufersal",
    "product": "Sunflower Oil 1L"
}
```

---

## 🔄 DEVELOPMENT WORKFLOW

### 1. DAILY START CHECKLIST
```bash
# Every morning, tell Claude:
"Check PROJECT_STATE.md and continue Sunflower Oil workflow"

# Claude will:
1. Read current state
2. Show pending tasks
3. Continue from last point
```

### 2. DURING DEVELOPMENT
```bash
# After EVERY major change:
"Update PROJECT_STATE.md with [what you just did]"

# After completing a feature:
"Document in WORKFLOW_TRACKER.md"

# Before ending session:
"Save current state to PROJECT_STATE.md"
```

### 3. CONTEXT PRESERVATION RULES

#### NEVER SAY:
- "Help me with my project" (too vague)
- "Continue where we left off" (no context)
- "Fix the error" (which error?)

#### ALWAYS SAY:
- "Continue Sunflower Oil workflow from Request #28"
- "Deploy workflow_app.py to VM 74.248.141.31"
- "Update supplier matching in sunflower_oil_project.py line 86"

---

## 💾 WHEN TO UPDATE DOCS

### UPDATE PROJECT_STATE.md:
- ✅ After creating new functionality
- ✅ After fixing major bugs
- ✅ After database changes
- ✅ Before ending work session
- ✅ After VM deployments

### UPDATE WORKFLOW_TRACKER.md:
- ✅ After completing workflow step
- ✅ After testing feature
- ✅ After customer feedback
- ✅ After Azure AI integration

### UPDATE THIS FILE:
- ✅ When learning new best practices
- ✅ When finding better methods
- ✅ When context gets lost
- ✅ Monthly review

---

## 🚀 EFFECTIVE DEVELOPMENT COMMANDS

### Starting Work
```python
# 1. Check state
"Show PROJECT_STATE.md and pending tasks"

# 2. Continue specific task
"Implement supplier matching for Sunflower Oil project on VM"

# 3. Test on VM
"Deploy and test workflow_app.py on 74.248.141.31"
```

### During Development
```python
# Be specific about files
"In sunflower_oil_project.py, update find_suppliers function"

# Reference exact locations
"Fix line 86-99 in workflow_app.py for proposal display"

# Use project IDs
"Test with Request #28, Proposal #63"
```

### Saving Progress
```python
# Save immediately after success
"Update PROJECT_STATE.md - completed supplier matching"

# Document errors and solutions
"Add to WORKFLOW_TRACKER.md - fixed encoding issue with emojis"

# Commit to VM
"Deploy updated files to VM 74.248.141.31"
```

---

## 🎯 TODAY'S WORKFLOW DEVELOPMENT

### Ready to Start Now:
1. **Sunflower Oil Project** exists in database
   - Request #28 created
   - Proposal #63 linked
   - Order SHF-20250806-28 ready

2. **VM Ready** at 74.248.141.31
   - PostgreSQL connected
   - Python environment ready
   - Port 8000 available

3. **Files Ready** for deployment
   - workflow_app.py - View interface
   - sunflower_oil_project.py - Business logic
   - workflow_template.py - Duplication engine

### To Start Working TODAY:
```bash
# Tell Claude exactly this:
"Deploy Sunflower Oil workflow to VM 74.248.141.31
Using files: workflow_app.py, sunflower_oil_project.py
Make it accessible at http://74.248.141.31:8000
Show Request #28 to Order SHF-20250806-28 flow"
```

---

## 🔒 CRITICAL INFORMATION - NEVER LOSE

### VM Access
```bash
ssh fdxadmin@74.248.141.31
cd /home/fdxadmin/fdx/app
```

### Database
```bash
postgresql://fdxadmin:FoodXchange2024@fdx-poland-db.postgres.database.azure.com/foodxchange?sslmode=require
```

### Project IDs
```python
REQUEST_ID = 28      # Sunflower Oil request
PROPOSAL_ID = 63     # Accepted proposal
ORDER_ID = "SHF-20250806-28"  # Shufersal order
```

### Azure Resources
```bash
Resource Group: poland-rg
VM: poland-vm (74.248.141.31)
Database: fdx-poland-db
Region: Poland Central
```

---

## 📈 SUCCESS METRICS

### How to Know It's Working:
1. ✅ Can see Sunflower Oil workflow at http://74.248.141.31:8000
2. ✅ Can track Request #28 through complete pipeline
3. ✅ Can duplicate workflow for other products
4. ✅ Commission calculated correctly ($480 for Sunflower Oil)
5. ✅ All using Python, FastAPI, Bootstrap, Jinja2

---

## 🆘 RECOVERY PROCEDURES

### If Context Lost:
```bash
"Read DEVELOPMENT_METHODOLOGY.md
Read PROJECT_STATE.md  
Read WORKFLOW_TRACKER.md
Show Sunflower Oil project status"
```

### If VM Disconnected:
```bash
"Reconnect to VM 74.248.141.31
Check workflow_app.py status
Restart with: python3 -m uvicorn workflow_app:app --host 0.0.0.0 --port 8000"
```

### If Database Issues:
```bash
"Test Poland PostgreSQL connection
Check Sunflower Oil Request #28
Verify Proposal #63 exists"
```

---

## 📝 TEMPLATE RESPONSES FOR COMMON TASKS

### Want to Add Feature:
"Add [feature] to Sunflower Oil workflow in workflow_app.py
Deploy to VM 74.248.141.31
Update PROJECT_STATE.md"

### Want to Test:
"Test Sunflower Oil flow from Request #28 to Order SHF-20250806-28
On VM 74.248.141.31 port 8000
Document results in WORKFLOW_TRACKER.md"

### Want to Deploy:
"Deploy [files] to VM 74.248.141.31
Path: /home/fdxadmin/fdx/app
Start service on port 8000
Update PROJECT_STATE.md"

---

## START WORKING NOW!

Ready command for Claude:
```
"Deploy Sunflower Oil workflow to VM now
Files: workflow_app.py, sunflower_oil_project.py
Make live at http://74.248.141.31:8000
Update PROJECT_STATE.md when complete"
```

---
*Remember: Claude is your development angel when you give specific context!*