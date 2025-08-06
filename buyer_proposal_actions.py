"""
BUYER PROPOSAL ACTIONS
Approve, Disapprove, Ask Questions, Order Samples
"""

from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, JSONResponse
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime
import json

app = FastAPI(title="Buyer Proposal Management")

POLAND_DB = "postgresql://fdxadmin:FoodXchange2024@fdx-poland-db.postgres.database.azure.com/foodxchange?sslmode=require"

def get_db():
    return psycopg2.connect(POLAND_DB, cursor_factory=RealDictCursor)

@app.get("/proposals/{request_id}", response_class=HTMLResponse)
async def view_proposals(request_id: int):
    """View all proposals for a request with action buttons"""
    
    conn = get_db()
    cur = conn.cursor()
    
    # Get request details
    cur.execute("SELECT * FROM buyer_requests WHERE id = %s", (request_id,))
    request = cur.fetchone()
    
    # Get proposals (simulated with real supplier data)
    cur.execute("""
        SELECT 
            s.id as supplier_id,
            s.supplier_name,
            s.country,
            s.company_email,
            s.products,
            s.rating
        FROM suppliers s
        WHERE s.products ILIKE '%oil%'
        LIMIT 5
    """)
    suppliers = cur.fetchall()
    
    cur.close()
    conn.close()
    
    # Build proposal cards with actions
    proposal_cards = ""
    for i, s in enumerate(suppliers, 1):
        # Simulated pricing
        price = 3.20 + (i * 0.15)
        moq = 1000 * i
        
        proposal_cards += f"""
        <div class="proposal-card" id="proposal-{s['supplier_id']}">
            <div class="proposal-header">
                <div class="supplier-info">
                    <h3>{s['supplier_name']}</h3>
                    <p>{s['country']} | Rating: ⭐ {s['rating'] or 'N/A'} | {s['company_email'] or 'No email'}</p>
                </div>
                <div class="proposal-status" id="status-{s['supplier_id']}">
                    <span class="status-badge pending">PENDING REVIEW</span>
                </div>
            </div>
            
            <div class="proposal-details">
                <div class="detail-grid">
                    <div class="detail">
                        <label>Price per Unit:</label>
                        <strong>${price:.2f}</strong>
                    </div>
                    <div class="detail">
                        <label>MOQ:</label>
                        <strong>{moq:,} units</strong>
                    </div>
                    <div class="detail">
                        <label>Payment:</label>
                        <strong>30% advance</strong>
                    </div>
                    <div class="detail">
                        <label>Delivery:</label>
                        <strong>21 days</strong>
                    </div>
                </div>
                
                <div class="products-section">
                    <label>Products Offered:</label>
                    <p>{(s['products'] or 'Various food products')[:200]}...</p>
                </div>
            </div>
            
            <!-- ACTION BUTTONS -->
            <div class="action-section">
                <div class="main-actions">
                    <button class="btn btn-approve" onclick="approveProposal({s['supplier_id']}, '{s['supplier_name']}')">
                        ✓ Approve
                    </button>
                    <button class="btn btn-reject" onclick="rejectProposal({s['supplier_id']}, '{s['supplier_name']}')">
                        ✗ Reject
                    </button>
                    <button class="btn btn-question" onclick="askQuestion({s['supplier_id']}, '{s['supplier_name']}')">
                        ? Ask Question
                    </button>
                </div>
                
                <div class="sample-action">
                    <button class="btn btn-sample" onclick="orderSample({s['supplier_id']}, '{s['supplier_name']}')">
                        📦 Order Sample
                    </button>
                    <span class="sample-note">Free sample available</span>
                </div>
            </div>
            
            <!-- QUESTION/COMMENT SECTION (Hidden by default) -->
            <div class="question-section" id="question-{s['supplier_id']}" style="display: none;">
                <textarea id="question-text-{s['supplier_id']}" placeholder="Type your question or comment..."></textarea>
                <button onclick="sendQuestion({s['supplier_id']})">Send Question</button>
                <button onclick="cancelQuestion({s['supplier_id']})">Cancel</button>
            </div>
            
            <!-- SAMPLE ORDER FORM (Hidden by default) -->
            <div class="sample-section" id="sample-{s['supplier_id']}" style="display: none;">
                <h4>Sample Order Details</h4>
                <input type="number" id="sample-qty-{s['supplier_id']}" placeholder="Sample quantity" value="1">
                <input type="text" id="sample-address-{s['supplier_id']}" placeholder="Delivery address" value="123 Main St, Tel Aviv">
                <textarea id="sample-notes-{s['supplier_id']}" placeholder="Special requirements..."></textarea>
                <button onclick="confirmSample({s['supplier_id']})">Confirm Sample Order</button>
                <button onclick="cancelSample({s['supplier_id']})">Cancel</button>
            </div>
            
            <!-- ACTION HISTORY -->
            <div class="action-history" id="history-{s['supplier_id']}">
                <!-- Will be populated when actions are taken -->
            </div>
        </div>
        """
    
    return f"""
<!DOCTYPE html>
<html>
<head>
    <title>Proposal Management - Request #{request_id}</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 20px;
            background: #f5f5f5;
        }}
        
        .header {{
            background: white;
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 20px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        
        .proposal-card {{
            background: white;
            border-radius: 8px;
            padding: 20px;
            margin-bottom: 20px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            border: 2px solid #e0e0e0;
        }}
        
        .proposal-card.approved {{
            border-color: #28a745;
            background: #f8fff9;
        }}
        
        .proposal-card.rejected {{
            border-color: #dc3545;
            background: #fff8f8;
        }}
        
        .proposal-header {{
            display: flex;
            justify-content: space-between;
            align-items: start;
            margin-bottom: 20px;
            padding-bottom: 15px;
            border-bottom: 1px solid #e0e0e0;
        }}
        
        .supplier-info h3 {{
            margin: 0 0 5px 0;
            color: #333;
        }}
        
        .supplier-info p {{
            margin: 0;
            color: #666;
            font-size: 14px;
        }}
        
        .status-badge {{
            padding: 6px 12px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: bold;
        }}
        
        .status-badge.pending {{
            background: #fff3cd;
            color: #856404;
        }}
        
        .status-badge.approved {{
            background: #d4edda;
            color: #155724;
        }}
        
        .status-badge.rejected {{
            background: #f8d7da;
            color: #721c24;
        }}
        
        .status-badge.sample-ordered {{
            background: #d1ecf1;
            color: #0c5460;
        }}
        
        .detail-grid {{
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 15px;
            margin-bottom: 15px;
        }}
        
        .detail label {{
            display: block;
            font-size: 12px;
            color: #666;
            margin-bottom: 3px;
        }}
        
        .detail strong {{
            font-size: 16px;
            color: #333;
        }}
        
        .products-section {{
            margin: 15px 0;
            padding: 10px;
            background: #f8f9fa;
            border-radius: 5px;
        }}
        
        .products-section label {{
            font-weight: bold;
            color: #333;
        }}
        
        .action-section {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-top: 20px;
            padding-top: 20px;
            border-top: 1px solid #e0e0e0;
        }}
        
        .main-actions {{
            display: flex;
            gap: 10px;
        }}
        
        .sample-action {{
            display: flex;
            align-items: center;
            gap: 10px;
        }}
        
        .sample-note {{
            font-size: 12px;
            color: #666;
        }}
        
        .btn {{
            padding: 10px 20px;
            border: none;
            border-radius: 5px;
            font-size: 14px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.2s;
        }}
        
        .btn:hover {{
            transform: translateY(-1px);
            box-shadow: 0 2px 4px rgba(0,0,0,0.2);
        }}
        
        .btn-approve {{
            background: #28a745;
            color: white;
        }}
        
        .btn-reject {{
            background: #dc3545;
            color: white;
        }}
        
        .btn-question {{
            background: #ffc107;
            color: #333;
        }}
        
        .btn-sample {{
            background: #17a2b8;
            color: white;
        }}
        
        .question-section, .sample-section {{
            background: #f8f9fa;
            padding: 15px;
            border-radius: 5px;
            margin-top: 15px;
        }}
        
        .question-section textarea, .sample-section textarea {{
            width: 100%;
            padding: 10px;
            border: 1px solid #ddd;
            border-radius: 5px;
            margin-bottom: 10px;
            min-height: 80px;
            font-family: Arial;
        }}
        
        .sample-section input {{
            width: 100%;
            padding: 10px;
            border: 1px solid #ddd;
            border-radius: 5px;
            margin-bottom: 10px;
        }}
        
        .action-history {{
            margin-top: 15px;
            padding: 10px;
            background: #f0f0f0;
            border-radius: 5px;
            font-size: 13px;
            display: none;
        }}
        
        .action-history.has-content {{
            display: block;
        }}
        
        .history-item {{
            padding: 5px 0;
            border-bottom: 1px solid #ddd;
        }}
        
        .history-item:last-child {{
            border-bottom: none;
        }}
        
        .summary-bar {{
            background: white;
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 20px;
            display: flex;
            justify-content: space-around;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        
        .summary-item {{
            text-align: center;
        }}
        
        .summary-number {{
            font-size: 24px;
            font-weight: bold;
            color: #333;
        }}
        
        .summary-label {{
            font-size: 14px;
            color: #666;
            margin-top: 5px;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>Manage Proposals</h1>
        <p>Request #{request_id}: {request['request_name'] if request else 'Sunflower Oil 5000 units'}</p>
        <a href="/">← Back to Dashboard</a>
    </div>
    
    <!-- Summary Bar -->
    <div class="summary-bar">
        <div class="summary-item">
            <div class="summary-number" id="total-count">{len(suppliers)}</div>
            <div class="summary-label">Total Proposals</div>
        </div>
        <div class="summary-item">
            <div class="summary-number" id="pending-count">{len(suppliers)}</div>
            <div class="summary-label">Pending Review</div>
        </div>
        <div class="summary-item">
            <div class="summary-number" id="approved-count">0</div>
            <div class="summary-label">Approved</div>
        </div>
        <div class="summary-item">
            <div class="summary-number" id="rejected-count">0</div>
            <div class="summary-label">Rejected</div>
        </div>
        <div class="summary-item">
            <div class="summary-number" id="sample-count">0</div>
            <div class="summary-label">Samples Ordered</div>
        </div>
    </div>
    
    <!-- Proposal Cards -->
    {proposal_cards}
    
    <script>
        let pendingCount = {len(suppliers)};
        let approvedCount = 0;
        let rejectedCount = 0;
        let sampleCount = 0;
        
        function updateCounts() {{
            document.getElementById('pending-count').textContent = pendingCount;
            document.getElementById('approved-count').textContent = approvedCount;
            document.getElementById('rejected-count').textContent = rejectedCount;
            document.getElementById('sample-count').textContent = sampleCount;
        }}
        
        function approveProposal(supplierId, supplierName) {{
            if (confirm('Approve proposal from ' + supplierName + '?')) {{
                // Update UI
                const card = document.getElementById('proposal-' + supplierId);
                card.classList.add('approved');
                card.classList.remove('rejected');
                
                const status = document.getElementById('status-' + supplierId);
                status.innerHTML = '<span class="status-badge approved">✓ APPROVED</span>';
                
                // Update counts
                pendingCount--;
                approvedCount++;
                updateCounts();
                
                // Add to history
                addHistory(supplierId, '✓ Proposal approved');
                
                // Send to backend (would be API call)
                alert('Proposal approved! Moving to negotiation stage with ' + supplierName);
            }}
        }}
        
        function rejectProposal(supplierId, supplierName) {{
            const reason = prompt('Reason for rejection (optional):');
            if (reason !== null) {{
                // Update UI
                const card = document.getElementById('proposal-' + supplierId);
                card.classList.add('rejected');
                card.classList.remove('approved');
                
                const status = document.getElementById('status-' + supplierId);
                status.innerHTML = '<span class="status-badge rejected">✗ REJECTED</span>';
                
                // Update counts
                pendingCount--;
                rejectedCount++;
                updateCounts();
                
                // Add to history
                addHistory(supplierId, '✗ Proposal rejected' + (reason ? ': ' + reason : ''));
                
                alert('Proposal rejected. Supplier will be notified.');
            }}
        }}
        
        function askQuestion(supplierId, supplierName) {{
            // Show question form
            document.getElementById('question-' + supplierId).style.display = 'block';
        }}
        
        function sendQuestion(supplierId) {{
            const question = document.getElementById('question-text-' + supplierId).value;
            if (question) {{
                // Add to history
                addHistory(supplierId, '❓ Question sent: ' + question);
                
                // Hide form and clear
                document.getElementById('question-' + supplierId).style.display = 'none';
                document.getElementById('question-text-' + supplierId).value = '';
                
                alert('Question sent to supplier. You will be notified when they respond.');
            }}
        }}
        
        function cancelQuestion(supplierId) {{
            document.getElementById('question-' + supplierId).style.display = 'none';
            document.getElementById('question-text-' + supplierId).value = '';
        }}
        
        function orderSample(supplierId, supplierName) {{
            // Show sample form
            document.getElementById('sample-' + supplierId).style.display = 'block';
        }}
        
        function confirmSample(supplierId) {{
            const qty = document.getElementById('sample-qty-' + supplierId).value;
            const address = document.getElementById('sample-address-' + supplierId).value;
            const notes = document.getElementById('sample-notes-' + supplierId).value;
            
            if (qty && address) {{
                // Update sample count
                sampleCount++;
                updateCounts();
                
                // Add sample badge to status
                const status = document.getElementById('status-' + supplierId);
                status.innerHTML += ' <span class="status-badge sample-ordered">📦 SAMPLE ORDERED</span>';
                
                // Add to history
                addHistory(supplierId, '📦 Sample ordered: ' + qty + ' units to ' + address);
                
                // Hide form
                document.getElementById('sample-' + supplierId).style.display = 'none';
                
                alert('Sample order confirmed! Expected delivery in 5-7 days.');
            }} else {{
                alert('Please fill in quantity and address');
            }}
        }}
        
        function cancelSample(supplierId) {{
            document.getElementById('sample-' + supplierId).style.display = 'none';
        }}
        
        function addHistory(supplierId, action) {{
            const history = document.getElementById('history-' + supplierId);
            history.classList.add('has-content');
            
            const timestamp = new Date().toLocaleString();
            const historyItem = document.createElement('div');
            historyItem.className = 'history-item';
            historyItem.innerHTML = '<strong>' + timestamp + '</strong>: ' + action;
            
            history.insertBefore(historyItem, history.firstChild);
        }}
    </script>
</body>
</html>
"""

@app.post("/api/proposal/action", response_class=JSONResponse)
async def proposal_action(request: Request):
    """Handle proposal actions (approve/reject/question/sample)"""
    
    data = await request.json()
    action = data.get("action")  # approve, reject, question, sample
    supplier_id = data.get("supplier_id")
    request_id = data.get("request_id")
    details = data.get("details", {})
    
    conn = get_db()
    cur = conn.cursor()
    
    # Log the action
    cur.execute("""
        INSERT INTO proposal_actions 
        (request_id, supplier_id, action, details, created_at)
        VALUES (%s, %s, %s, %s, %s)
    """, (request_id, supplier_id, action, json.dumps(details), datetime.now()))
    
    # Update proposal status if needed
    if action == "approve":
        cur.execute("""
            UPDATE request_proposals 
            SET status = 'Approved' 
            WHERE supplier_id = %s AND request_id = %s
        """, (supplier_id, str(request_id)))
        
    elif action == "reject":
        cur.execute("""
            UPDATE request_proposals 
            SET status = 'Rejected' 
            WHERE supplier_id = %s AND request_id = %s
        """, (supplier_id, str(request_id)))
    
    conn.commit()
    cur.close()
    conn.close()
    
    return {"status": "success", "action": action, "supplier_id": supplier_id}

if __name__ == "__main__":
    import uvicorn
    print("\n" + "="*60)
    print("BUYER PROPOSAL ACTION SYSTEM")
    print("="*60)
    print("\nActions Available:")
    print("✓ APPROVE - Accept supplier proposal")
    print("✗ REJECT - Decline with reason")
    print("? ASK QUESTION - Send questions to supplier")
    print("📦 ORDER SAMPLE - Request samples (independent of price approval)")
    print("\nFeatures:")
    print("• Each proposal has all 4 action buttons")
    print("• Sample ordering works even if price rejected")
    print("• Question/comment system for clarifications")
    print("• Action history tracking")
    print("• Visual status updates")
    print("\nStarting at: http://localhost:8000/proposals/1")
    uvicorn.run(app, host="0.0.0.0", port=8000)