"""
NEGOTIATION SYSTEM - The Real Business Flow
RFQ → Negotiation (3-10 emails) → Adaptation → Orders
"""

from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime
from openai import AzureOpenAI
import os
import json

app = FastAPI(title="FDX Negotiation System")

POLAND_DB = "postgresql://fdxadmin:FoodXchange2024@fdx-poland-db.postgres.database.azure.com/foodxchange?sslmode=require"

# Azure AI for email analysis
client = AzureOpenAI(
    api_key=os.getenv('AZURE_OPENAI_KEY'),
    api_version='2024-02-15-preview',
    azure_endpoint=os.getenv('AZURE_OPENAI_ENDPOINT')
)

def analyze_email_intent(email_content):
    """AI analyzes what the email is about"""
    prompt = f"""
    Analyze this business email and return JSON with:
    - intent: QUOTE|NEGOTIATE|ACCEPT|REJECT|QUESTION|SAMPLE_REQUEST
    - price_mentioned: number or null
    - quantity_mentioned: number or null  
    - urgency: HIGH|MEDIUM|LOW
    - key_points: list of main points
    
    Email: {email_content}
    """
    
    try:
        response = client.chat.completions.create(
            model=os.getenv('AZURE_OPENAI_DEPLOYMENT', 'gpt-4o-mini'),
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"}
        )
        return json.loads(response.choices[0].message.content)
    except:
        return {
            "intent": "UNKNOWN",
            "price_mentioned": None,
            "urgency": "MEDIUM"
        }

@app.get("/", response_class=HTMLResponse)
async def negotiation_dashboard():
    """Show all negotiations in progress"""
    
    return """
<!DOCTYPE html>
<html>
<head>
    <title>FDX Negotiation Center</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: -apple-system, BlinkMacSystemFont, sans-serif;
            background: #f5f7fa;
            padding: 20px;
        }
        
        .header {
            background: white;
            padding: 30px;
            border-radius: 12px;
            margin-bottom: 20px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        }
        
        .workflow-progress {
            display: flex;
            justify-content: space-between;
            padding: 20px;
            background: white;
            border-radius: 12px;
            margin-bottom: 20px;
        }
        
        .stage {
            text-align: center;
            flex: 1;
            position: relative;
        }
        
        .stage::after {
            content: '→';
            position: absolute;
            right: -20px;
            top: 20px;
            color: #ddd;
            font-size: 20px;
        }
        
        .stage:last-child::after {
            display: none;
        }
        
        .stage.active {
            color: #667eea;
            font-weight: bold;
        }
        
        .stage.complete {
            color: #28a745;
        }
        
        .stage-icon {
            font-size: 30px;
            margin-bottom: 10px;
        }
        
        .negotiation-card {
            background: white;
            padding: 20px;
            border-radius: 12px;
            margin-bottom: 15px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        }
        
        .negotiation-header {
            display: flex;
            justify-content: space-between;
            margin-bottom: 15px;
        }
        
        .product-name {
            font-size: 18px;
            font-weight: 600;
            color: #333;
        }
        
        .negotiation-status {
            padding: 6px 12px;
            border-radius: 20px;
            font-size: 13px;
            font-weight: 600;
        }
        
        .status-negotiating {
            background: #fff3cd;
            color: #856404;
        }
        
        .status-accepted {
            background: #d4edda;
            color: #155724;
        }
        
        .email-thread {
            border-left: 3px solid #e0e0e0;
            padding-left: 15px;
            margin: 15px 0;
        }
        
        .email-item {
            margin-bottom: 10px;
            padding: 10px;
            background: #f8f9fa;
            border-radius: 6px;
        }
        
        .email-buyer {
            background: #e3f2fd;
            margin-left: 30px;
        }
        
        .email-supplier {
            background: #f3e5f5;
            margin-right: 30px;
        }
        
        .email-meta {
            font-size: 12px;
            color: #666;
            margin-bottom: 5px;
        }
        
        .ai-analysis {
            background: #ffeaa7;
            padding: 10px;
            border-radius: 6px;
            margin-top: 10px;
            font-size: 13px;
        }
        
        .price-tracking {
            display: flex;
            align-items: center;
            gap: 10px;
            padding: 15px;
            background: #f8f9fa;
            border-radius: 8px;
        }
        
        .price-change {
            font-size: 24px;
            font-weight: bold;
        }
        
        .price-down {
            color: #28a745;
        }
        
        .actions {
            display: flex;
            gap: 10px;
            margin-top: 15px;
        }
        
        .btn {
            padding: 10px 20px;
            border: none;
            border-radius: 6px;
            cursor: pointer;
            font-size: 14px;
            font-weight: 600;
        }
        
        .btn-primary {
            background: #667eea;
            color: white;
        }
        
        .btn-success {
            background: #28a745;
            color: white;
        }
        
        .btn-secondary {
            background: #6c757d;
            color: white;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>🤝 Negotiation Center</h1>
        <p style="color: #666; margin-top: 10px;">Track all ongoing negotiations with suppliers</p>
    </div>
    
    <!-- Workflow Progress -->
    <div class="workflow-progress">
        <div class="stage complete">
            <div class="stage-icon">📧</div>
            <div>RFQ Sent</div>
        </div>
        <div class="stage active">
            <div class="stage-icon">💬</div>
            <div>NEGOTIATION</div>
            <small>3-10 emails</small>
        </div>
        <div class="stage">
            <div class="stage-icon">🔧</div>
            <div>ADAPTATION</div>
            <small>Customization</small>
        </div>
        <div class="stage">
            <div class="stage-icon">📦</div>
            <div>ORDERS</div>
            <small>Monthly</small>
        </div>
    </div>
    
    <!-- Active Negotiation Example -->
    <div class="negotiation-card">
        <div class="negotiation-header">
            <div>
                <div class="product-name">Sunflower Oil 1L - Shufersal</div>
                <div style="color: #666; font-size: 14px;">5000 bottles/month • 12-month contract</div>
            </div>
            <div class="negotiation-status status-negotiating">
                Negotiating
            </div>
        </div>
        
        <div class="price-tracking">
            <span>Price Movement:</span>
            <span class="price-change price-down">$3.50 → $3.25</span>
            <span style="color: #28a745;">↓ 7.1%</span>
            <span style="color: #666;">Target: $3.00</span>
        </div>
        
        <div class="email-thread">
            <div class="email-item email-buyer">
                <div class="email-meta">Buyer • 2 hours ago</div>
                <div>We need 5000 bottles monthly. Target price $3.00. Can you meet this?</div>
            </div>
            
            <div class="email-item email-supplier">
                <div class="email-meta">Supplier • 1 hour ago</div>
                <div>We can offer $3.50 per bottle for 5000 units monthly.</div>
                <div class="ai-analysis">
                    🤖 AI: Initial quote provided. Price 17% above target.
                </div>
            </div>
            
            <div class="email-item email-buyer">
                <div class="email-meta">Buyer • 30 min ago</div>
                <div>Too high. Competitor offers $3.20. Can you match for 12-month contract?</div>
                <div class="ai-analysis">
                    🤖 AI: Buyer negotiating with competitor price + volume commitment
                </div>
            </div>
            
            <div class="email-item email-supplier">
                <div class="email-meta">Supplier • 10 min ago</div>
                <div>For 12-month contract, best price $3.25 with free shipping over 3000 units.</div>
                <div class="ai-analysis">
                    🤖 AI: Counter-offer with incentive. Close to acceptable range.
                </div>
            </div>
        </div>
        
        <div style="padding: 15px; background: #e8f5e9; border-radius: 8px;">
            <strong>📊 Negotiation Summary:</strong><br>
            • Emails exchanged: 4<br>
            • Price reduction: $0.25 (7.1%)<br>
            • Added benefits: Free shipping<br>
            • Recommendation: Consider accepting or push for $3.20
        </div>
        
        <div class="actions">
            <button class="btn btn-primary" onclick="sendReply()">Reply to Supplier</button>
            <button class="btn btn-success" onclick="acceptOffer()">Accept & Move to Adaptation</button>
            <button class="btn btn-secondary" onclick="requestApproval()">Request Manager Approval</button>
        </div>
    </div>
    
    <!-- Another Negotiation -->
    <div class="negotiation-card">
        <div class="negotiation-header">
            <div>
                <div class="product-name">Extra Virgin Olive Oil - Carrefour</div>
                <div style="color: #666; font-size: 14px;">1000 bottles/month</div>
            </div>
            <div class="negotiation-status status-accepted">
                Ready for Adaptation
            </div>
        </div>
        
        <div class="price-tracking">
            <span>Final Agreement:</span>
            <span class="price-change price-down">$8.50 → $7.90</span>
            <span style="color: #28a745;">✓ Accepted</span>
        </div>
        
        <div style="padding: 15px; background: #d4edda; border-radius: 8px;">
            <strong>✅ Terms Agreed:</strong><br>
            • Price: $7.90/bottle<br>
            • MOQ: 500 bottles<br>
            • Custom labeling included<br>
            • 6-month contract<br>
            <button class="btn btn-primary" style="margin-top: 10px;">Start Adaptation Process</button>
        </div>
    </div>
    
    <script>
        function sendReply() {
            const reply = prompt('Type your reply to supplier:');
            if (reply) {
                alert('Email sent: ' + reply);
                // Would send via API
            }
        }
        
        function acceptOffer() {
            if (confirm('Accept $3.25 per bottle with 12-month contract?')) {
                alert('Moving to Adaptation Stage...');
                window.location.href = '/adaptation/1';
            }
        }
        
        function requestApproval() {
            alert('Approval request sent to manager');
        }
    </script>
</body>
</html>
"""

@app.get("/adaptation/{workflow_id}", response_class=HTMLResponse)
async def adaptation_stage(workflow_id: int):
    """Adaptation stage after negotiation acceptance"""
    
    return f"""
<!DOCTYPE html>
<html>
<head>
    <title>Adaptation Stage - Workflow {workflow_id}</title>
    <style>
        /* Same styles as above */
        body {{ font-family: -apple-system, BlinkMacSystemFont, sans-serif; background: #f5f7fa; padding: 20px; }}
        .header {{ background: white; padding: 30px; border-radius: 12px; margin-bottom: 20px; }}
        .checklist {{ background: white; padding: 20px; border-radius: 12px; }}
        .task {{ padding: 15px; border-bottom: 1px solid #e0e0e0; display: flex; align-items: center; }}
        .task input[type="checkbox"] {{ margin-right: 15px; width: 20px; height: 20px; }}
        .task.complete {{ opacity: 0.6; }}
        .upload-box {{ border: 2px dashed #ddd; padding: 20px; text-align: center; margin: 10px 0; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🔧 Adaptation Stage</h1>
        <p>Customize product specifications before first order</p>
    </div>
    
    <div class="checklist">
        <h3>Sunflower Oil - Adaptation Checklist</h3>
        
        <div class="task">
            <input type="checkbox" checked>
            <div>
                <strong>Label Design</strong><br>
                <small>Custom label approved ✓</small>
            </div>
        </div>
        
        <div class="task">
            <input type="checkbox">
            <div>
                <strong>Packaging Specifications</strong><br>
                <div class="upload-box">
                    <input type="file">
                    <p>Upload packaging requirements</p>
                </div>
            </div>
        </div>
        
        <div class="task">
            <input type="checkbox">
            <div>
                <strong>Quality Certificates</strong><br>
                <small>ISO, HACCP, Kosher required</small>
            </div>
        </div>
        
        <div class="task">
            <input type="checkbox">
            <div>
                <strong>Delivery Schedule</strong><br>
                <small>15th of each month to Haifa port</small>
            </div>
        </div>
        
        <div class="task">
            <input type="checkbox">
            <div>
                <strong>Payment Terms</strong><br>
                <small>30% advance, 70% on Bill of Lading</small>
            </div>
        </div>
        
        <button class="btn btn-success" style="margin-top: 20px;">
            Complete Adaptation → Create First Order
        </button>
    </div>
</body>
</html>
"""

if __name__ == "__main__":
    import uvicorn
    print("\n" + "="*60)
    print("NEGOTIATION SYSTEM - Real Business Flow")
    print("="*60)
    print("\nStages:")
    print("1. RFQ → Initial Quote")
    print("2. NEGOTIATION (3-10 emails)")
    print("3. ADAPTATION (Customization)")
    print("4. ORDERS (Monthly recurring)")
    print("\nStarting at: http://localhost:8000")
    uvicorn.run(app, host="0.0.0.0", port=8000)