"""
FDX Trading - Simple Workflow Viewer
View the workflow in your browser
"""

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
import psycopg2
from psycopg2.extras import RealDictCursor
import os

app = FastAPI(title="FDX Workflow Viewer")

# Database connection
POLAND_DB = "postgresql://fdxadmin:FoodXchange2024@fdx-poland-db.postgres.database.azure.com/foodxchange?sslmode=require"

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Main workflow dashboard"""
    conn = psycopg2.connect(POLAND_DB)
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    # Get statistics
    cur.execute("""
        SELECT 
            (SELECT COUNT(*) FROM suppliers) as suppliers,
            (SELECT COUNT(*) FROM buyers) as buyers,
            (SELECT COUNT(*) FROM buyer_requests) as requests,
            (SELECT COUNT(*) FROM request_proposals) as proposals,
            (SELECT COUNT(*) FROM orders_raw) as orders,
            (SELECT COUNT(*) FROM shipping_raw) as shipping,
            (SELECT COUNT(*) FROM invoices_raw) as invoices
    """)
    stats = cur.fetchone()
    
    # Get Sunflower Oil project
    cur.execute("""
        SELECT * FROM buyer_requests 
        WHERE id IN (28, 86, 90, 91)
        ORDER BY id DESC
        LIMIT 5
    """)
    recent = cur.fetchall()
    
    cur.close()
    conn.close()
    
    return HTMLResponse(content=f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>FDX Workflow</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
        <style>
            .workflow-step {{
                text-align: center;
                padding: 20px;
                margin: 10px;
                border: 2px solid #ddd;
                border-radius: 10px;
                background: white;
            }}
            .workflow-step.complete {{
                background: #d4edda;
                border-color: #28a745;
            }}
            .workflow-step h3 {{
                margin: 0;
                color: #333;
            }}
            .workflow-step .count {{
                font-size: 36px;
                font-weight: bold;
                color: #007bff;
            }}
            .arrow {{
                font-size: 30px;
                color: #666;
                margin: 20px 0;
            }}
        </style>
    </head>
    <body>
        <nav class="navbar navbar-dark bg-primary">
            <div class="container">
                <a class="navbar-brand" href="/">FDX Trading Workflow</a>
            </div>
        </nav>
        
        <div class="container mt-4">
            <h1>Business Workflow Status</h1>
            
            <!-- Workflow Steps -->
            <div class="row mt-4">
                <div class="col-md-2">
                    <div class="workflow-step complete">
                        <h3>BUYERS</h3>
                        <div class="count">{stats['buyers']}</div>
                        <small>Companies</small>
                    </div>
                </div>
                <div class="col-md-2">
                    <div class="workflow-step complete">
                        <h3>REQUESTS</h3>
                        <div class="count">{stats['requests']}</div>
                        <small>RFQs</small>
                    </div>
                </div>
                <div class="col-md-2">
                    <div class="workflow-step complete">
                        <h3>SUPPLIERS</h3>
                        <div class="count">{stats['suppliers']:,}</div>
                        <small>Available</small>
                    </div>
                </div>
                <div class="col-md-2">
                    <div class="workflow-step complete">
                        <h3>PROPOSALS</h3>
                        <div class="count">{stats['proposals']}</div>
                        <small>Submitted</small>
                    </div>
                </div>
                <div class="col-md-2">
                    <div class="workflow-step">
                        <h3>ORDERS</h3>
                        <div class="count">{stats['orders']}</div>
                        <small>Created</small>
                    </div>
                </div>
                <div class="col-md-2">
                    <div class="workflow-step">
                        <h3>INVOICES</h3>
                        <div class="count">{stats['invoices']}</div>
                        <small>Generated</small>
                    </div>
                </div>
            </div>
            
            <!-- Flow Diagram -->
            <div class="text-center mt-4">
                <h3>Workflow Progress</h3>
                <div style="font-size: 20px; padding: 20px; background: #f8f9fa; border-radius: 10px;">
                    Buyer → Request → Find Suppliers → Get Proposals → Create Order → Ship → Invoice → Payment
                </div>
            </div>
            
            <!-- Recent Projects -->
            <div class="mt-5">
                <h3>Recent Projects</h3>
                <table class="table table-striped">
                    <thead>
                        <tr>
                            <th>ID</th>
                            <th>Buyer</th>
                            <th>Request</th>
                            <th>Status</th>
                        </tr>
                    </thead>
                    <tbody>
                        {"".join([f'''
                        <tr>
                            <td>{r['id']}</td>
                            <td>{r['buyer_name']}</td>
                            <td>{r['request_name'][:50] if r['request_name'] else 'N/A'}</td>
                            <td><span class="badge bg-primary">{r['status']}</span></td>
                        </tr>
                        ''' for r in recent])}
                    </tbody>
                </table>
            </div>
            
            <!-- Sunflower Oil Project -->
            <div class="mt-5">
                <h3>Featured: Sunflower Oil Project</h3>
                <div class="card">
                    <div class="card-body">
                        <h5>Shufersal - Sunflower Oil 1L</h5>
                        <p><strong>Request #28</strong> → <strong>Proposal #63</strong> → <strong>Order SHF-20250806-28</strong></p>
                        <ul>
                            <li>Quantity: 5,000 bottles</li>
                            <li>Total Value: $20,475.00</li>
                            <li>Commission: $525.00</li>
                            <li>Status: Ready for Production</li>
                        </ul>
                    </div>
                </div>
            </div>
            
            <!-- Summary Stats -->
            <div class="mt-5">
                <h3>System Summary</h3>
                <div class="row">
                    <div class="col-md-4">
                        <div class="card text-center">
                            <div class="card-body">
                                <h2>{stats['suppliers']:,}</h2>
                                <p>Total Suppliers</p>
                            </div>
                        </div>
                    </div>
                    <div class="col-md-4">
                        <div class="card text-center">
                            <div class="card-body">
                                <h2>{stats['requests'] + stats['proposals']}</h2>
                                <p>Active Workflows</p>
                            </div>
                        </div>
                    </div>
                    <div class="col-md-4">
                        <div class="card text-center">
                            <div class="card-body">
                                <h2>{stats['orders'] + stats['invoices']}</h2>
                                <p>Completed Transactions</p>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        
        <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    </body>
    </html>
    """)

if __name__ == "__main__":
    import uvicorn
    print("\n" + "="*60)
    print("Starting FDX Workflow Viewer")
    print("="*60)
    print("\nOpen your browser and go to:")
    print("http://localhost:8000")
    print("\nPress Ctrl+C to stop")
    uvicorn.run(app, host="0.0.0.0", port=8000)