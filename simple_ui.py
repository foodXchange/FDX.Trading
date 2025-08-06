"""
VERY SIMPLE UI - Minimal graphics
Just forms and tables, no fancy styling
"""

from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime

app = FastAPI()

POLAND_DB = "postgresql://fdxadmin:FoodXchange2024@fdx-poland-db.postgres.database.azure.com/foodxchange?sslmode=require"

@app.get("/", response_class=HTMLResponse)
async def home():
    """Super simple search"""
    return """
<html>
<head>
    <title>FDX</title>
    <style>
        body { font-family: Arial; margin: 20px; }
        input, button { padding: 10px; margin: 5px; }
        table { border-collapse: collapse; width: 100%; }
        td, th { border: 1px solid #ddd; padding: 8px; text-align: left; }
        th { background: #f2f2f2; }
    </style>
</head>
<body>
    <h1>FDX Trading</h1>
    
    <form action="/search" method="post">
        <input type="text" name="query" placeholder="What product?" required size="50">
        <button type="submit">Search</button>
    </form>
</body>
</html>
"""

@app.post("/search", response_class=HTMLResponse)
async def search(query: str = Form(...)):
    """Search results - very simple table"""
    
    conn = psycopg2.connect(POLAND_DB, cursor_factory=RealDictCursor)
    cur = conn.cursor()
    
    # Simple search
    cur.execute("""
        SELECT id, supplier_name, country, products, company_email
        FROM suppliers
        WHERE products ILIKE %s OR supplier_name ILIKE %s
        LIMIT 25
    """, (f'%{query}%', f'%{query}%'))
    
    suppliers = cur.fetchall()
    cur.close()
    conn.close()
    
    # Build simple table
    rows = ""
    for s in suppliers:
        rows += f"""
        <tr>
            <td><input type="checkbox" name="s_{s['id']}" value="{s['id']}"></td>
            <td>{s['supplier_name'] or '-'}</td>
            <td>{s['country'] or '-'}</td>
            <td>{(s['products'] or '-')[:100]}</td>
            <td>{s['company_email'] or '-'}</td>
        </tr>
        """
    
    return f"""
<html>
<head>
    <title>Results</title>
    <style>
        body {{ font-family: Arial; margin: 20px; }}
        table {{ border-collapse: collapse; width: 100%; }}
        td, th {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
        th {{ background: #f2f2f2; }}
        button {{ padding: 10px; margin: 10px; }}
    </style>
</head>
<body>
    <h1>Results for: {query}</h1>
    <p>Found {len(suppliers)} suppliers</p>
    
    <form action="/email" method="post">
        <table>
            <tr>
                <th>Select</th>
                <th>Supplier</th>
                <th>Country</th>
                <th>Products</th>
                <th>Email</th>
            </tr>
            {rows}
        </table>
        
        <button type="submit">Email Selected</button>
    </form>
    
    <a href="/">New Search</a>
</body>
</html>
"""

@app.post("/email", response_class=HTMLResponse)
async def email_suppliers(request: Request):
    """Email confirmation - very simple"""
    
    form_data = await request.form()
    selected = [k.split('_')[1] for k in form_data.keys() if k.startswith('s_')]
    
    return f"""
<html>
<head>
    <title>Emails Sent</title>
    <style>
        body {{ font-family: Arial; margin: 20px; }}
    </style>
</head>
<body>
    <h1>Emails Sent</h1>
    <p>Sent to {len(selected)} suppliers</p>
    
    <h2>Email Thread:</h2>
    <div style="border: 1px solid #ddd; padding: 10px;">
        <p><b>You:</b> We need sunflower oil. Please send quote.</p>
        <p style="color: gray;"><b>Supplier:</b> Awaiting response...</p>
    </div>
    
    <a href="/">New Search</a>
</body>
</html>
"""

@app.get("/forecast", response_class=HTMLResponse)
async def forecast_form():
    """Simple forecast calculator"""
    return """
<html>
<head>
    <title>Container Calculator</title>
    <style>
        body { font-family: Arial; margin: 20px; }
        input { padding: 5px; margin: 5px; }
        button { padding: 10px; margin: 10px; }
        .result { border: 1px solid #ddd; padding: 10px; margin: 10px 0; }
    </style>
</head>
<body>
    <h1>Container Calculator</h1>
    
    <form method="post" action="/calculate">
        <p>Product: <input type="text" name="product" value="Sunflower Oil 1L"></p>
        <p>Price per unit: $<input type="number" name="price" step="0.01" value="3.20"></p>
        <p>Units per carton: <input type="number" name="units" value="12"></p>
        <p>Carton weight (kg): <input type="number" name="weight" value="15"></p>
        
        <p>
            Pallets? 
            <input type="radio" name="pallets" value="yes" checked> Yes
            <input type="radio" name="pallets" value="no"> No
        </p>
        
        <button type="submit">Calculate</button>
    </form>
</body>
</html>
"""

@app.post("/calculate", response_class=HTMLResponse)
async def calculate(
    product: str = Form(...),
    price: float = Form(...),
    units: int = Form(...),
    weight: float = Form(...),
    pallets: str = Form(...)
):
    """Simple calculation results"""
    
    # Simple calculations
    cartons_20ft = 1100 if pallets == "no" else 960
    cartons_40ft = 2350 if pallets == "no" else 2080
    
    units_20ft = cartons_20ft * units
    units_40ft = cartons_40ft * units
    
    weight_20ft = cartons_20ft * weight / 1000  # Convert to tons
    weight_40ft = cartons_40ft * weight / 1000
    
    return f"""
<html>
<head>
    <title>Results</title>
    <style>
        body {{ font-family: Arial; margin: 20px; }}
        table {{ border-collapse: collapse; }}
        td, th {{ border: 1px solid #ddd; padding: 8px; }}
        th {{ background: #f2f2f2; }}
    </style>
</head>
<body>
    <h1>Container Loading: {product}</h1>
    
    <table>
        <tr>
            <th>Container</th>
            <th>Units</th>
            <th>Cartons</th>
            <th>Weight</th>
            <th>Value</th>
        </tr>
        <tr>
            <td>20ft</td>
            <td>{units_20ft:,}</td>
            <td>{cartons_20ft}</td>
            <td>{weight_20ft:.1f} tons</td>
            <td>${units_20ft * price:,.2f}</td>
        </tr>
        <tr>
            <td>40ft</td>
            <td>{units_40ft:,}</td>
            <td>{cartons_40ft}</td>
            <td>{weight_40ft:.1f} tons</td>
            <td>${units_40ft * price:,.2f}</td>
        </tr>
    </table>
    
    <p>Method: {'With pallets' if pallets == 'yes' else 'Floor loading'}</p>
    
    <a href="/forecast">New Calculation</a>
</body>
</html>
"""

@app.get("/admin", response_class=HTMLResponse)
async def admin():
    """Simple admin page"""
    return """
<html>
<head>
    <title>Admin</title>
    <style>
        body { font-family: Arial; margin: 20px; }
        button { padding: 10px; margin: 5px; }
    </style>
</head>
<body>
    <h1>Admin Panel</h1>
    
    <h2>Act as:</h2>
    <button onclick="alert('Acting as Buyer')">Buyer - Shufersal</button>
    <button onclick="alert('Acting as Supplier')">Supplier - Global Oils</button>
    
    <h2>Quick Links:</h2>
    <p><a href="/">Buyer Search</a></p>
    <p><a href="/forecast">Container Calculator</a></p>
    
    <h2>Stats:</h2>
    <p>Suppliers: 18,031</p>
    <p>Buyers: 17</p>
    <p>Requests: 170</p>
</body>
</html>
"""

if __name__ == "__main__":
    import uvicorn
    print("\nVERY SIMPLE UI - Minimal Graphics")
    print("="*40)
    print("Pages:")
    print("/         - Search")
    print("/forecast - Calculator")
    print("/admin    - Admin")
    print("\nNo fancy styling, just simple forms and tables")
    uvicorn.run(app, host="0.0.0.0", port=8000)