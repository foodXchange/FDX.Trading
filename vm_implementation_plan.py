"""
VM IMPLEMENTATION PLAN
Poland VM: 74.248.141.31
Database: fdx-poland-db.postgres.database.azure.com

PLANNING FRAMEWORK FOR USER INSTRUCTIONS
Based on: Sunflower Oil Project for Shufersal
"""

# CONNECTION DETAILS
VM_HOST = "74.248.141.31"
VM_USER = "fdxadmin"
VM_PATH = "/home/fdxadmin/fdx/app"
POLAND_DB = "postgresql://fdxadmin:FoodXchange2024@fdx-poland-db.postgres.database.azure.com/foodxchange?sslmode=require"

# WORKFLOW TEMPLATE - Sunflower Oil to Shufersal
SUNFLOWER_PROJECT = {
    "request_id": 28,
    "proposal_id": 63,
    "order_id": "SHF-20250806-28",
    "buyer": "Shufersal",
    "product": "Sunflower Oil 1L",
    "quantity": 5000,
    "price": 3.20,
    "total": 16000.00,
    "commission": 480.00
}

# IMPLEMENTATION PHASES
PHASES = {
    "PHASE_1": {
        "name": "Core Workflow Engine",
        "tasks": [
            "Deploy workflow_app.py to VM",
            "Set up FastAPI service",
            "Configure PostgreSQL connection",
            "Test with Sunflower Oil project"
        ],
        "files": [
            "workflow_app.py",
            "sunflower_oil_project.py",
            "workflow_template.py"
        ]
    },
    
    "PHASE_2": {
        "name": "User Interface",
        "tasks": [
            "Create Bootstrap dashboard",
            "Add Jinja2 templates",
            "Show workflow progress",
            "Display Sunflower Oil project"
        ],
        "components": [
            "Dashboard view",
            "Request form",
            "Supplier search",
            "Proposal management",
            "Order tracking"
        ]
    },
    
    "PHASE_3": {
        "name": "Azure AI Integration",
        "tasks": [
            "Connect Azure OpenAI",
            "Auto-match suppliers",
            "Generate proposals",
            "Smart pricing"
        ],
        "features": [
            "AI supplier matching",
            "Price optimization",
            "Document generation",
            "Email automation"
        ]
    },
    
    "PHASE_4": {
        "name": "Complete Workflow",
        "tasks": [
            "Request -> Proposal flow",
            "Proposal -> Order flow",
            "Order -> Invoice flow",
            "Commission calculation"
        ],
        "endpoints": [
            "/api/create-request",
            "/api/find-suppliers",
            "/api/create-proposal",
            "/api/approve-order",
            "/api/generate-invoice"
        ]
    }
}

# USER INSTRUCTION TEMPLATE
INSTRUCTION_TEMPLATE = """
TO IMPLEMENT: [Your specific task]

CURRENT STATE:
- Sunflower Oil Request #28 exists
- Proposal #63 from supplier
- Order SHF-20250806-28 ready

WHAT TO BUILD:
1. [First component]
2. [Second component]
3. [Third component]

REQUIREMENTS:
- Use Python, FastAPI, Bootstrap, Jinja2
- Connect to Poland PostgreSQL
- Very light implementation
- Based on Sunflower Oil workflow

EXPECTED RESULT:
[What you want to see]
"""

# VM DEPLOYMENT COMMANDS
DEPLOYMENT = {
    "ssh_connect": f"ssh {VM_USER}@{VM_HOST}",
    "copy_files": f"scp *.py {VM_USER}@{VM_HOST}:{VM_PATH}/",
    "install_deps": "pip install fastapi uvicorn psycopg2-binary jinja2 python-multipart",
    "run_app": "python3 -m uvicorn workflow_app:app --host 0.0.0.0 --port 8000",
    "test_api": "curl http://74.248.141.31:8000/"
}

# PLANNING QUESTIONS FOR USER
PLANNING_QUESTIONS = """
READY TO IMPLEMENT ON VM. Please provide instructions for:

1. PRIORITY: What should I implement first?
   [ ] Dashboard to view Sunflower Oil project
   [ ] API to create new requests like Sunflower Oil
   [ ] Supplier matching for oil products
   [ ] Complete workflow automation

2. UI STYLE: How should it look?
   [ ] Simple table view (very light)
   [ ] Card-based layout
   [ ] Workflow pipeline view
   [ ] Minimal forms

3. FEATURES: What's most important?
   [ ] View existing Sunflower Oil workflow
   [ ] Duplicate workflow for other products
   [ ] Auto-match suppliers
   [ ] Generate documents

4. AZURE AI: How to use it?
   [ ] Auto-suggest suppliers
   [ ] Generate emails
   [ ] Price optimization
   [ ] Quality matching

Your instructions:
"""

def show_current_state():
    """Show what's ready"""
    print("\n=== CURRENT STATE ===")
    print(f"Project: Sunflower Oil for Shufersal")
    print(f"Request: #{SUNFLOWER_PROJECT['request_id']}")
    print(f"Proposal: #{SUNFLOWER_PROJECT['proposal_id']}")
    print(f"Order: {SUNFLOWER_PROJECT['order_id']}")
    print(f"Value: ${SUNFLOWER_PROJECT['total']:,.2f}")
    print("\nReady to implement your instructions on VM!")

def show_vm_info():
    """Show VM connection details"""
    print("\n=== VM CONNECTION ===")
    print(f"Host: {VM_HOST}")
    print(f"User: {VM_USER}")
    print(f"Path: {VM_PATH}")
    print(f"SSH: ssh {VM_USER}@{VM_HOST}")
    print(f"Database: Poland PostgreSQL (connected)")

def show_tech_stack():
    """Show what we'll use"""
    print("\n=== TECH STACK ===")
    print("- Python 3.x")
    print("- FastAPI (web framework)")
    print("- Bootstrap 5 (UI)")
    print("- Jinja2 (templates)")
    print("- PostgreSQL (Poland)")
    print("- Azure OpenAI (if needed)")

if __name__ == "__main__":
    print("="*70)
    print("VM IMPLEMENTATION PLANNING")
    print("="*70)
    
    show_current_state()
    show_vm_info()
    show_tech_stack()
    
    print("\n" + "="*70)
    print("WAITING FOR YOUR INSTRUCTIONS")
    print("="*70)
    print(PLANNING_QUESTIONS)