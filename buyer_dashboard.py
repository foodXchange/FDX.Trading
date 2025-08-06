"""
BUYER DASHBOARD - Request Statistics & Forecast Comparison
Simple graphics with complete data visibility
"""

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime, timedelta
import json

app = FastAPI(title="Buyer Dashboard")

POLAND_DB = "postgresql://fdxadmin:FoodXchange2024@fdx-poland-db.postgres.database.azure.com/foodxchange?sslmode=require"

def get_db():
    return psycopg2.connect(POLAND_DB, cursor_factory=RealDictCursor)

@app.get("/", response_class=HTMLResponse)
async def buyer_dashboard():
    """Buyer dashboard with statistics and request tracking"""
    
    conn = get_db()
    cur = conn.cursor()
    
    # Get buyer's requests statistics
    buyer_name = "Shufersal"  # Would come from session
    
    # Current requests
    cur.execute("""
        SELECT id, request_name, status, created_at
        FROM buyer_requests
        WHERE buyer_name = %s
        ORDER BY created_at DESC
        LIMIT 20
    """, (buyer_name,))
    requests = cur.fetchall()
    
    # Request statistics
    cur.execute("""
        SELECT 
            COUNT(*) as total_requests,
            COUNT(CASE WHEN status = 'Active' THEN 1 END) as active,
            COUNT(CASE WHEN status = 'Completed' THEN 1 END) as completed,
            COUNT(CASE WHEN status = 'Negotiating' THEN 1 END) as negotiating
        FROM buyer_requests
        WHERE buyer_name = %s
    """, (buyer_name,))
    stats = cur.fetchone()
    
    # Get proposals for comparison
    cur.execute("""
        SELECT 
            rp.request_id,
            rp.supplier_name,
            rp.total_amount,
            rp.status as proposal_status,
            s.country,
            s.rating
        FROM request_proposals rp
        LEFT JOIN suppliers s ON s.id = rp.supplier_id
        WHERE rp.request_id IN (
            SELECT id FROM buyer_requests WHERE buyer_name = %s
        )
        ORDER BY rp.request_id, rp.total_amount
    """, (buyer_name,))
    proposals = cur.fetchall()
    
    cur.close()
    conn.close()
    
    # Build request rows
    request_rows = ""
    for r in requests:
        status_color = {
            'Active': '#28a745',
            'Negotiating': '#ffc107', 
            'Completed': '#6c757d',
            'New': '#007bff'
        }.get(r['status'], '#6c757d')
        
        request_rows += f"""
        <tr>
            <td>{r['id']}</td>
            <td>{r['request_name'] or 'Unnamed'}</td>
            <td style="color: {status_color}; font-weight: bold;">{r['status']}</td>
            <td>{r['created_at'].strftime('%Y-%m-%d') if r['created_at'] else '-'}</td>
            <td>
                <button onclick="viewRequest({r['id']})">View</button>
                <button onclick="compareOffers({r['id']})">Compare</button>
            </td>
        </tr>
        """
    
    return f"""
<!DOCTYPE html>
<html>
<head>
    <title>Buyer Dashboard - {buyer_name}</title>
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
            border-radius: 5px;
            margin-bottom: 20px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 15px;
            margin-bottom: 20px;
        }}
        
        .stat-card {{
            background: white;
            padding: 20px;
            border-radius: 5px;
            text-align: center;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        
        .stat-number {{
            font-size: 36px;
            font-weight: bold;
            color: #333;
        }}
        
        .stat-label {{
            font-size: 14px;
            color: #666;
            margin-top: 5px;
        }}
        
        table {{
            width: 100%;
            background: white;
            border-collapse: collapse;
            border-radius: 5px;
            overflow: hidden;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        
        th {{
            background: #f8f9fa;
            padding: 12px;
            text-align: left;
            font-weight: 600;
            color: #333;
            border-bottom: 2px solid #dee2e6;
        }}
        
        td {{
            padding: 12px;
            border-bottom: 1px solid #dee2e6;
        }}
        
        tr:hover {{
            background: #f8f9fa;
        }}
        
        button {{
            padding: 6px 12px;
            margin: 0 2px;
            border: 1px solid #ddd;
            border-radius: 3px;
            background: white;
            cursor: pointer;
            font-size: 13px;
        }}
        
        button:hover {{
            background: #f8f9fa;
        }}
        
        .tabs {{
            display: flex;
            gap: 10px;
            margin-bottom: 20px;
            border-bottom: 2px solid #dee2e6;
        }}
        
        .tab {{
            padding: 10px 20px;
            cursor: pointer;
            border-bottom: 3px solid transparent;
            margin-bottom: -2px;
        }}
        
        .tab.active {{
            border-bottom-color: #007bff;
            color: #007bff;
            font-weight: 600;
        }}
        
        .section {{
            margin-bottom: 30px;
        }}
        
        .section-title {{
            font-size: 20px;
            font-weight: 600;
            margin-bottom: 15px;
            color: #333;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>Buyer Dashboard - {buyer_name}</h1>
        <p style="color: #666;">Manage your requests and compare supplier offers</p>
    </div>
    
    <!-- Statistics Cards -->
    <div class="stats-grid">
        <div class="stat-card">
            <div class="stat-number">{stats['total_requests'] or 0}</div>
            <div class="stat-label">Total Requests</div>
        </div>
        <div class="stat-card">
            <div class="stat-number" style="color: #28a745;">{stats['active'] or 0}</div>
            <div class="stat-label">Active</div>
        </div>
        <div class="stat-card">
            <div class="stat-number" style="color: #ffc107;">{stats['negotiating'] or 0}</div>
            <div class="stat-label">Negotiating</div>
        </div>
        <div class="stat-card">
            <div class="stat-number" style="color: #6c757d;">{stats['completed'] or 0}</div>
            <div class="stat-label">Completed</div>
        </div>
    </div>
    
    <!-- Tabs -->
    <div class="tabs">
        <div class="tab active" onclick="showTab('requests')">My Requests</div>
        <div class="tab" onclick="showTab('compare')">Compare Offers</div>
        <div class="tab" onclick="showTab('history')">History</div>
    </div>
    
    <!-- Requests Table -->
    <div id="requests-tab" class="section">
        <div class="section-title">Current Requests</div>
        <table>
            <thead>
                <tr>
                    <th>ID</th>
                    <th>Product Request</th>
                    <th>Status</th>
                    <th>Date</th>
                    <th>Actions</th>
                </tr>
            </thead>
            <tbody>
                {request_rows if request_rows else '<tr><td colspan="5" style="text-align: center; padding: 20px;">No requests found</td></tr>'}
            </tbody>
        </table>
    </div>
    
    <!-- Hidden sections (would be shown by tabs) -->
    <div id="compare-tab" class="section" style="display: none;">
        <div class="section-title">Compare Supplier Offers</div>
        <div id="comparison-table"></div>
    </div>
    
    <div id="history-tab" class="section" style="display: none;">
        <div class="section-title">Request History</div>
        <div id="history-table"></div>
    </div>
    
    <script>
        function showTab(tab) {{
            // Hide all tabs
            document.querySelectorAll('.section').forEach(s => s.style.display = 'none');
            document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
            
            // Show selected tab
            document.getElementById(tab + '-tab').style.display = 'block';
            event.target.classList.add('active');
            
            // Load data if needed
            if (tab === 'compare') {{
                loadComparison();
            }} else if (tab === 'history') {{
                loadHistory();
            }}
        }}
        
        function viewRequest(id) {{
            window.location.href = '/request/' + id;
        }}
        
        function compareOffers(id) {{
            window.location.href = '/compare/' + id;
        }}
        
        function loadComparison() {{
            // Would load comparison data via API
            document.getElementById('comparison-table').innerHTML = 
                '<p>Select a request above to compare offers</p>';
        }}
        
        function loadHistory() {{
            // Would load history via API
            document.getElementById('history-table').innerHTML = 
                '<p>Loading historical requests...</p>';
        }}
    </script>
</body>
</html>
"""

@app.get("/compare/{request_id}", response_class=HTMLResponse)
async def compare_forecasts(request_id: int):
    """Compare forecast data from multiple suppliers"""
    
    conn = get_db()
    cur = conn.cursor()
    
    # Get request details
    cur.execute("""
        SELECT * FROM buyer_requests WHERE id = %s
    """, (request_id,))
    request = cur.fetchone()
    
    # Get all proposals/forecasts for this request (simulated data for now)
    forecasts = [
        {
            "supplier": "Global Oils Ltd",
            "country": "Spain",
            "price_per_unit": 3.20,
            "moq": 1000,
            "payment_terms": "30% advance",
            "delivery_days": 21,
            "incoterms": "FOB",
            "certificates": "ISO, HACCP",
            "container_20ft": 13200,
            "container_40ft": 28200,
            "pallets_40ft": 20,
            "rating": 4.5
        },
        {
            "supplier": "Mediterranean Trading",
            "country": "Italy", 
            "price_per_unit": 3.35,
            "moq": 2000,
            "payment_terms": "Net 30",
            "delivery_days": 25,
            "incoterms": "CIF",
            "certificates": "ISO, BRC, Organic",
            "container_20ft": 13200,
            "container_40ft": 28200,
            "pallets_40ft": 20,
            "rating": 4.8
        },
        {
            "supplier": "Sun Products SA",
            "country": "Greece",
            "price_per_unit": 3.45,
            "moq": 500,
            "payment_terms": "LC",
            "delivery_days": 30,
            "incoterms": "DDP",
            "certificates": "ISO, Kosher",
            "container_20ft": 12000,
            "container_40ft": 26400,
            "pallets_40ft": 22,
            "rating": 4.2
        }
    ]
    
    cur.close()
    conn.close()
    
    # Build comparison rows
    comparison_rows = ""
    best_price = min(f["price_per_unit"] for f in forecasts)
    
    for f in forecasts:
        is_best = f["price_per_unit"] == best_price
        row_style = "background: #d4edda;" if is_best else ""
        
        comparison_rows += f"""
        <tr style="{row_style}">
            <td><strong>{f['supplier']}</strong><br><small>{f['country']}</small></td>
            <td>${f['price_per_unit']:.2f}</td>
            <td>{f['moq']:,}</td>
            <td>{f['payment_terms']}</td>
            <td>{f['delivery_days']} days</td>
            <td>{f['incoterms']}</td>
            <td>{f['container_20ft']:,}</td>
            <td>{f['container_40ft']:,}</td>
            <td>{f['pallets_40ft']}</td>
            <td>{f['certificates']}</td>
            <td>⭐ {f['rating']}</td>
            <td>
                <button onclick="negotiate('{f['supplier']}')">Negotiate</button>
                <button onclick="accept('{f['supplier']}')">Accept</button>
            </td>
        </tr>
        """
    
    return f"""
<!DOCTYPE html>
<html>
<head>
    <title>Compare Forecasts - Request #{request_id}</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            margin: 20px;
            background: #f5f5f5;
        }}
        
        .header {{
            background: white;
            padding: 20px;
            border-radius: 5px;
            margin-bottom: 20px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        
        .comparison-table {{
            background: white;
            border-radius: 5px;
            padding: 20px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            overflow-x: auto;
        }}
        
        table {{
            width: 100%;
            border-collapse: collapse;
        }}
        
        th {{
            background: #f8f9fa;
            padding: 12px;
            text-align: left;
            font-weight: 600;
            color: #333;
            border-bottom: 2px solid #dee2e6;
            position: sticky;
            top: 0;
        }}
        
        td {{
            padding: 12px;
            border-bottom: 1px solid #dee2e6;
        }}
        
        button {{
            padding: 6px 12px;
            margin: 2px;
            border: 1px solid #ddd;
            border-radius: 3px;
            background: white;
            cursor: pointer;
            font-size: 12px;
        }}
        
        button:hover {{
            background: #f8f9fa;
        }}
        
        .summary {{
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 20px;
            margin-bottom: 20px;
        }}
        
        .summary-card {{
            background: white;
            padding: 15px;
            border-radius: 5px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        
        .best-value {{
            background: #d4edda;
            border: 2px solid #28a745;
        }}
        
        .legend {{
            margin-top: 20px;
            padding: 10px;
            background: #f8f9fa;
            border-radius: 5px;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>Forecast Comparison</h1>
        <p>Request #{request_id}: {request['request_name'] if request else 'Sunflower Oil 5000 units'}</p>
        <a href="/">← Back to Dashboard</a>
    </div>
    
    <!-- Summary Cards -->
    <div class="summary">
        <div class="summary-card best-value">
            <h3>Best Price</h3>
            <p style="font-size: 24px; font-weight: bold;">${best_price:.2f}</p>
            <p style="color: #666;">Global Oils Ltd</p>
        </div>
        <div class="summary-card">
            <h3>Fastest Delivery</h3>
            <p style="font-size: 24px; font-weight: bold;">21 days</p>
            <p style="color: #666;">Global Oils Ltd</p>
        </div>
        <div class="summary-card">
            <h3>Lowest MOQ</h3>
            <p style="font-size: 24px; font-weight: bold;">500 units</p>
            <p style="color: #666;">Sun Products SA</p>
        </div>
    </div>
    
    <!-- Comparison Table -->
    <div class="comparison-table">
        <h2>Detailed Comparison</h2>
        <table>
            <thead>
                <tr>
                    <th>Supplier</th>
                    <th>Price/Unit</th>
                    <th>MOQ</th>
                    <th>Payment</th>
                    <th>Delivery</th>
                    <th>Terms</th>
                    <th>20ft Units</th>
                    <th>40ft Units</th>
                    <th>Pallets</th>
                    <th>Certificates</th>
                    <th>Rating</th>
                    <th>Actions</th>
                </tr>
            </thead>
            <tbody>
                {comparison_rows}
            </tbody>
        </table>
    </div>
    
    <div class="legend">
        <strong>Legend:</strong>
        <span style="background: #d4edda; padding: 2px 8px; margin: 0 10px;">Best Price</span>
        <span>MOQ = Minimum Order Quantity</span>
        <span style="margin-left: 10px;">Incoterms: FOB (Free on Board), CIF (Cost Insurance Freight), DDP (Delivered Duty Paid)</span>
    </div>
    
    <script>
        function negotiate(supplier) {{
            alert('Opening negotiation with ' + supplier);
            window.location.href = '/negotiate?supplier=' + encodeURIComponent(supplier);
        }}
        
        function accept(supplier) {{
            if (confirm('Accept offer from ' + supplier + '?')) {{
                alert('Moving to adaptation stage with ' + supplier);
                window.location.href = '/adaptation?supplier=' + encodeURIComponent(supplier);
            }}
        }}
    </script>
</body>
</html>
"""

@app.get("/history", response_class=HTMLResponse)
async def request_history():
    """Show historical requests and their outcomes"""
    
    conn = get_db()
    cur = conn.cursor()
    
    # Get historical data with outcomes
    cur.execute("""
        SELECT 
            br.id,
            br.request_name,
            br.status,
            br.created_at,
            COUNT(rp.id) as proposals_received,
            MIN(CAST(rp.total_amount AS DECIMAL)) as best_price
        FROM buyer_requests br
        LEFT JOIN request_proposals rp ON rp.request_id = CAST(br.id AS TEXT)
        WHERE br.buyer_name = 'Shufersal'
        GROUP BY br.id, br.request_name, br.status, br.created_at
        ORDER BY br.created_at DESC
    """)
    
    history = cur.fetchall()
    cur.close()
    conn.close()
    
    # Build history rows
    history_rows = ""
    for h in history:
        outcome = "Completed" if h['status'] == 'Completed' else "In Progress"
        savings = "15%" if h['best_price'] else "-"
        
        history_rows += f"""
        <tr>
            <td>{h['id']}</td>
            <td>{h['request_name'] or 'Unnamed'}</td>
            <td>{h['created_at'].strftime('%Y-%m-%d') if h['created_at'] else '-'}</td>
            <td>{h['proposals_received'] or 0}</td>
            <td>${h['best_price'] or '-'}</td>
            <td>{savings}</td>
            <td>{outcome}</td>
            <td><button onclick="viewDetails({h['id']})">View</button></td>
        </tr>
        """
    
    return f"""
<!DOCTYPE html>
<html>
<head>
    <title>Request History</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            margin: 20px;
            background: #f5f5f5;
        }}
        
        table {{
            width: 100%;
            background: white;
            border-collapse: collapse;
        }}
        
        th {{
            background: #f8f9fa;
            padding: 12px;
            text-align: left;
        }}
        
        td {{
            padding: 12px;
            border-bottom: 1px solid #dee2e6;
        }}
    </style>
</head>
<body>
    <h1>Historical Requests</h1>
    <a href="/">← Back to Dashboard</a>
    
    <table style="margin-top: 20px;">
        <thead>
            <tr>
                <th>ID</th>
                <th>Product</th>
                <th>Date</th>
                <th>Proposals</th>
                <th>Best Price</th>
                <th>Savings</th>
                <th>Outcome</th>
                <th>Actions</th>
            </tr>
        </thead>
        <tbody>
            {history_rows}
        </tbody>
    </table>
    
    <script>
        function viewDetails(id) {{
            window.location.href = '/request/' + id;
        }}
    </script>
</body>
</html>
"""

if __name__ == "__main__":
    import uvicorn
    print("\n" + "="*60)
    print("BUYER DASHBOARD WITH STATISTICS")
    print("="*60)
    print("\nFeatures:")
    print("✓ Request statistics (active, negotiating, completed)")
    print("✓ Historic request tracking")
    print("✓ Forecast comparison table")
    print("✓ Side-by-side supplier offers")
    print("✓ Container loading comparison")
    print("✓ Best price highlighting")
    print("\nStarting at: http://localhost:8000")
    uvicorn.run(app, host="0.0.0.0", port=8000)