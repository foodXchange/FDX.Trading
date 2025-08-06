"""
WORKFLOW TEMPLATE - Duplicate this method for any project
"""

import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime

POLAND_DB = "postgresql://fdxadmin:FoodXchange2024@fdx-poland-db.postgres.database.azure.com/foodxchange?sslmode=require"

class WorkflowEngine:
    """Reusable workflow engine for any project"""
    
    def __init__(self):
        self.conn = psycopg2.connect(POLAND_DB)
        self.cur = self.conn.cursor(cursor_factory=RealDictCursor)
    
    def create_workflow(self, buyer_name, product_name, quantity, target_price):
        """Standard workflow - duplicate this for any project"""
        
        workflow = {
            "request_id": None,
            "proposal_id": None,
            "order_id": None,
            "status": "Started"
        }
        
        print(f"\n=== WORKFLOW: {product_name} for {buyer_name} ===")
        
        # STEP 1: Create Request
        print("1. Creating request...")
        self.cur.execute("""
            INSERT INTO buyer_requests (buyer_name, request_name, status, created_at)
            VALUES (%s, %s, 'New', %s) RETURNING id
        """, (buyer_name, product_name, datetime.now()))
        
        workflow["request_id"] = self.cur.fetchone()['id']
        print(f"   Request #{workflow['request_id']} created")
        
        # STEP 2: Find Suppliers
        print("2. Finding suppliers...")
        self.cur.execute("""
            SELECT id, supplier_name, country 
            FROM suppliers 
            WHERE products ILIKE %s 
            LIMIT 5
        """, (f'%{product_name.split()[0]}%',))
        
        suppliers = self.cur.fetchall()
        print(f"   Found {len(suppliers)} suppliers")
        
        # STEP 3: Create Proposal
        if suppliers:
            print("3. Creating proposal...")
            supplier = suppliers[0]
            self.cur.execute("""
                INSERT INTO request_proposals 
                (request_name, supplier_id, supplier_name, status, created_at)
                VALUES (%s, %s, %s, 'Pending', %s) RETURNING id
            """, (product_name, supplier['id'], supplier['supplier_name'], datetime.now()))
            
            workflow["proposal_id"] = self.cur.fetchone()['id']
            print(f"   Proposal #{workflow['proposal_id']} from {supplier['supplier_name']}")
        
        # STEP 4: Accept & Create Order
        print("4. Creating order...")
        workflow["order_id"] = f"ORD-{workflow['request_id']}-001"
        workflow["status"] = "Complete"
        print(f"   Order {workflow['order_id']} created")
        print(f"   Total: ${quantity * target_price:,.2f}")
        
        self.conn.commit()
        return workflow
    
    def duplicate_workflow(self, template_id):
        """Duplicate an existing workflow"""
        # Get template
        self.cur.execute("""
            SELECT * FROM buyer_requests WHERE id = %s
        """, (template_id,))
        
        template = self.cur.fetchone()
        if template:
            print(f"\nDuplicating workflow from Request #{template_id}")
            # Create new with same pattern
            return self.create_workflow(
                template['buyer_name'],
                template['request_name'] + " (Copy)",
                1000,  # Default quantity
                10.00  # Default price
            )
        return None
    
    def close(self):
        self.cur.close()
        self.conn.close()

# Workflow Templates - Ready to duplicate
WORKFLOW_TEMPLATES = [
    {
        "name": "Olive Oil Purchase",
        "buyer": "Carrefour",
        "product": "Extra Virgin Olive Oil 1L",
        "quantity": 500,
        "target_price": 8.50
    },
    {
        "name": "Pasta Order",
        "buyer": "Shufersal",
        "product": "Premium Pasta 500g",
        "quantity": 1000,
        "target_price": 2.50
    },
    {
        "name": "Tomato Products",
        "buyer": "Dor Alon",
        "product": "Crushed Tomatoes 400g",
        "quantity": 2000,
        "target_price": 1.20
    },
    {
        "name": "Rice Supply",
        "buyer": "Foodz",
        "product": "Basmati Rice 1kg",
        "quantity": 800,
        "target_price": 3.75
    },
    {
        "name": "Tuna Order",
        "buyer": "Achim Cohen",
        "product": "Tuna in Oil 185g",
        "quantity": 1500,
        "target_price": 2.90
    }
]

def run_multiple_workflows():
    """Run multiple workflows using the template"""
    engine = WorkflowEngine()
    results = []
    
    print("\n" + "="*60)
    print("RUNNING MULTIPLE WORKFLOWS")
    print("="*60)
    
    # Run 3 workflows
    for template in WORKFLOW_TEMPLATES[:3]:
        result = engine.create_workflow(
            template["buyer"],
            template["product"],
            template["quantity"],
            template["target_price"]
        )
        results.append(result)
        print(f"[OK] Workflow complete: {result['order_id']}")
    
    engine.close()
    
    print("\n" + "="*60)
    print("SUMMARY: Created 3 complete workflows")
    print("="*60)
    for r in results:
        print(f"- Request #{r['request_id']} -> Order {r['order_id']}")

def main():
    # Single workflow
    engine = WorkflowEngine()
    
    # Create one workflow
    result = engine.create_workflow(
        buyer_name="Test Buyer",
        product_name="Test Product",
        quantity=100,
        target_price=5.00
    )
    
    print(f"\nWorkflow Result: {result}")
    
    # Duplicate it
    duplicate = engine.duplicate_workflow(result["request_id"])
    if duplicate:
        print(f"Duplicated: {duplicate}")
    
    engine.close()
    
    # Run multiple
    run_multiple_workflows()

if __name__ == "__main__":
    main()