"""
SUPPLIER FORECAST TEMPLATE
Based on Excel structure - Complete product details, not just price
"""

from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, JSONResponse
import psycopg2
from datetime import datetime
import json

app = FastAPI(title="Supplier Forecast System")

POLAND_DB = "postgresql://fdxadmin:FoodXchange2024@fdx-poland-db.postgres.database.azure.com/foodxchange?sslmode=require"

# FORECAST TEMPLATE STRUCTURE (from Excel)
FORECAST_TEMPLATE = {
    "supplier_info": {
        "company_name": "",
        "contact_person": "",
        "email": "",
        "phone": "",
        "country": "",
        "incoterms": "",  # FOB, CIF, DDP, etc.
        "payment_terms": "",  # 30% advance, Net 30, LC, etc.
        "production_capacity": "",
        "certificates": []  # ISO, HACCP, Kosher, Halal, etc.
    },
    "product_lines": [
        {
            "product_name": "",
            "product_code": "",
            "description": "",
            "unit": "",  # BTL, KG, L, etc.
            "package_size": "",  # 1L, 5L, 20L
            "units_per_case": 0,
            "cases_per_pallet": 0,
            "unit_price": 0.00,
            "currency": "USD",
            "moq": 0,  # Minimum Order Quantity
            "lead_time_days": 0,
            "shelf_life_months": 0,
            "private_label": False,
            "certificates": [],
            "origin_country": ""
        }
    ],
    "pricing_tiers": [
        {"quantity_from": 0, "quantity_to": 1000, "price": 0.00},
        {"quantity_from": 1001, "quantity_to": 5000, "price": 0.00},
        {"quantity_from": 5001, "quantity_to": 10000, "price": 0.00}
    ],
    "additional_costs": {
        "custom_label_cost": 0.00,
        "special_packaging": 0.00,
        "express_shipping": 0.00
    }
}

@app.get("/supplier/forecast/{request_id}", response_class=HTMLResponse)
async def supplier_forecast_form(request_id: int):
    """Complete forecast form for suppliers"""
    
    return f"""
<!DOCTYPE html>
<html>
<head>
    <title>Supplier Forecast - Complete Details</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ 
            font-family: -apple-system, BlinkMacSystemFont, sans-serif;
            background: #f5f7fa;
            padding: 20px;
        }}
        
        .container {{
            max-width: 1200px;
            margin: 0 auto;
        }}
        
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            border-radius: 12px 12px 0 0;
        }}
        
        .form-section {{
            background: white;
            padding: 30px;
            margin-bottom: 2px;
        }}
        
        .section-title {{
            font-size: 18px;
            font-weight: 600;
            color: #333;
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 2px solid #667eea;
        }}
        
        .form-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
        }}
        
        .form-group {{
            display: flex;
            flex-direction: column;
        }}
        
        label {{
            font-size: 13px;
            color: #666;
            margin-bottom: 5px;
            font-weight: 600;
        }}
        
        input, select, textarea {{
            padding: 10px;
            border: 1px solid #ddd;
            border-radius: 6px;
            font-size: 14px;
        }}
        
        input:focus {{
            outline: none;
            border-color: #667eea;
        }}
        
        .product-table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
        }}
        
        .product-table th {{
            background: #f8f9fa;
            padding: 12px;
            text-align: left;
            font-size: 13px;
            font-weight: 600;
            color: #666;
            border-bottom: 2px solid #e0e0e0;
        }}
        
        .product-table td {{
            padding: 10px;
            border-bottom: 1px solid #f0f0f0;
        }}
        
        .product-table input {{
            width: 100%;
            padding: 8px;
            border: 1px solid #e0e0e0;
        }}
        
        .add-row-btn {{
            margin-top: 10px;
            padding: 10px 20px;
            background: #f8f9fa;
            border: 2px dashed #ddd;
            border-radius: 6px;
            cursor: pointer;
            color: #666;
        }}
        
        .add-row-btn:hover {{
            background: #e9ecef;
        }}
        
        .pricing-tiers {{
            background: #f8f9fa;
            padding: 20px;
            border-radius: 8px;
            margin-top: 20px;
        }}
        
        .tier-row {{
            display: grid;
            grid-template-columns: 1fr 1fr 1fr;
            gap: 15px;
            margin-bottom: 15px;
        }}
        
        .submit-section {{
            background: white;
            padding: 30px;
            border-radius: 0 0 12px 12px;
            text-align: center;
        }}
        
        .btn-submit {{
            padding: 15px 40px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 8px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
        }}
        
        .btn-submit:hover {{
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
        }}
        
        .required {{
            color: red;
        }}
        
        .info-box {{
            background: #e3f2fd;
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 20px;
            font-size: 14px;
            color: #1976d2;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📊 Complete Forecast Submission</h1>
            <p>Request #${request_id} - Sunflower Oil 5000 bottles/month</p>
        </div>
        
        <form id="forecast-form" method="post" action="/supplier/submit-forecast">
            <input type="hidden" name="request_id" value="{request_id}">
            
            <!-- Company Information -->
            <div class="form-section">
                <div class="section-title">1. Company Information</div>
                <div class="form-grid">
                    <div class="form-group">
                        <label>Company Name <span class="required">*</span></label>
                        <input type="text" name="company_name" required>
                    </div>
                    <div class="form-group">
                        <label>Contact Person <span class="required">*</span></label>
                        <input type="text" name="contact_person" required>
                    </div>
                    <div class="form-group">
                        <label>Email <span class="required">*</span></label>
                        <input type="email" name="email" required>
                    </div>
                    <div class="form-group">
                        <label>Phone</label>
                        <input type="tel" name="phone">
                    </div>
                    <div class="form-group">
                        <label>Country <span class="required">*</span></label>
                        <input type="text" name="country" required>
                    </div>
                    <div class="form-group">
                        <label>Payment Terms <span class="required">*</span></label>
                        <select name="payment_terms" required>
                            <option value="">Select...</option>
                            <option>30% Advance, 70% on BL</option>
                            <option>Net 30 days</option>
                            <option>Net 60 days</option>
                            <option>Letter of Credit</option>
                            <option>100% Advance</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label>Incoterms <span class="required">*</span></label>
                        <select name="incoterms" required>
                            <option value="">Select...</option>
                            <option>EXW - Ex Works</option>
                            <option>FOB - Free on Board</option>
                            <option>CIF - Cost Insurance Freight</option>
                            <option>DDP - Delivered Duty Paid</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label>Monthly Capacity</label>
                        <input type="text" name="capacity" placeholder="e.g., 50,000 bottles">
                    </div>
                </div>
            </div>
            
            <!-- Product Details -->
            <div class="form-section">
                <div class="section-title">2. Product Details</div>
                <div class="info-box">
                    📌 Add all product variations you can supply (different sizes, packaging, etc.)
                </div>
                
                <table class="product-table">
                    <thead>
                        <tr>
                            <th>Product</th>
                            <th>Package</th>
                            <th>Unit</th>
                            <th>Price/Unit</th>
                            <th>MOQ</th>
                            <th>Lead Time</th>
                            <th>Origin</th>
                        </tr>
                    </thead>
                    <tbody id="product-rows">
                        <tr>
                            <td><input type="text" name="product_name_1" placeholder="Sunflower Oil" required></td>
                            <td><input type="text" name="package_1" placeholder="1L Bottle" required></td>
                            <td>
                                <select name="unit_1" required>
                                    <option>BTL</option>
                                    <option>L</option>
                                    <option>KG</option>
                                    <option>DRUM</option>
                                </select>
                            </td>
                            <td><input type="number" name="price_1" step="0.01" placeholder="3.20" required></td>
                            <td><input type="number" name="moq_1" placeholder="1000" required></td>
                            <td><input type="text" name="lead_1" placeholder="21 days" required></td>
                            <td><input type="text" name="origin_1" placeholder="Spain"></td>
                        </tr>
                        <tr>
                            <td><input type="text" name="product_name_2" placeholder="Sunflower Oil"></td>
                            <td><input type="text" name="package_2" placeholder="5L Bottle"></td>
                            <td>
                                <select name="unit_2">
                                    <option>BTL</option>
                                    <option>L</option>
                                    <option>KG</option>
                                    <option>DRUM</option>
                                </select>
                            </td>
                            <td><input type="number" name="price_2" step="0.01" placeholder="15.00"></td>
                            <td><input type="number" name="moq_2" placeholder="500"></td>
                            <td><input type="text" name="lead_2" placeholder="21 days"></td>
                            <td><input type="text" name="origin_2" placeholder="Spain"></td>
                        </tr>
                    </tbody>
                </table>
                <button type="button" class="add-row-btn" onclick="addProductRow()">
                    + Add Another Product
                </button>
            </div>
            
            <!-- Volume Pricing -->
            <div class="form-section">
                <div class="section-title">3. Volume Pricing (Optional)</div>
                <div class="pricing-tiers">
                    <div class="tier-row">
                        <div class="form-group">
                            <label>1-1000 units</label>
                            <input type="number" name="tier1_price" step="0.01" placeholder="3.50">
                        </div>
                        <div class="form-group">
                            <label>1001-5000 units</label>
                            <input type="number" name="tier2_price" step="0.01" placeholder="3.20">
                        </div>
                        <div class="form-group">
                            <label>5001+ units</label>
                            <input type="number" name="tier3_price" step="0.01" placeholder="3.00">
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- Certifications -->
            <div class="form-section">
                <div class="section-title">4. Certifications & Quality</div>
                <div class="form-grid">
                    <div class="form-group">
                        <label>Available Certificates</label>
                        <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 10px; margin-top: 10px;">
                            <label><input type="checkbox" name="cert_iso"> ISO 22000</label>
                            <label><input type="checkbox" name="cert_haccp"> HACCP</label>
                            <label><input type="checkbox" name="cert_kosher"> Kosher</label>
                            <label><input type="checkbox" name="cert_halal"> Halal</label>
                            <label><input type="checkbox" name="cert_organic"> Organic</label>
                            <label><input type="checkbox" name="cert_brc"> BRC</label>
                        </div>
                    </div>
                    <div class="form-group">
                        <label>Private Label Available?</label>
                        <select name="private_label">
                            <option value="yes">Yes - Can customize label</option>
                            <option value="no">No - Our brand only</option>
                            <option value="moq">Yes - With MOQ requirement</option>
                        </select>
                    </div>
                </div>
            </div>
            
            <!-- Additional Information -->
            <div class="form-section">
                <div class="section-title">5. Additional Information</div>
                <div class="form-group">
                    <label>Special Notes / Terms</label>
                    <textarea name="notes" rows="4" placeholder="Any special conditions, discounts, or additional information..."></textarea>
                </div>
            </div>
            
            <!-- Submit -->
            <div class="submit-section">
                <button type="submit" class="btn-submit">
                    Submit Complete Forecast
                </button>
                <p style="margin-top: 15px; color: #666; font-size: 14px;">
                    Your forecast will be sent to the buyer for review
                </p>
            </div>
        </form>
    </div>
    
    <script>
        let productCount = 2;
        
        function addProductRow() {
            productCount++;
            const tbody = document.getElementById('product-rows');
            const newRow = document.createElement('tr');
            newRow.innerHTML = `
                <td><input type="text" name="product_name_${{productCount}}" placeholder="Product name"></td>
                <td><input type="text" name="package_${{productCount}}" placeholder="Package size"></td>
                <td>
                    <select name="unit_${{productCount}}">
                        <option>BTL</option>
                        <option>L</option>
                        <option>KG</option>
                        <option>DRUM</option>
                    </select>
                </td>
                <td><input type="number" name="price_${{productCount}}" step="0.01" placeholder="0.00"></td>
                <td><input type="number" name="moq_${{productCount}}" placeholder="MOQ"></td>
                <td><input type="text" name="lead_${{productCount}}" placeholder="Lead time"></td>
                <td><input type="text" name="origin_${{productCount}}" placeholder="Origin"></td>
            `;
            tbody.appendChild(newRow);
        }
        
        document.getElementById('forecast-form').addEventListener('submit', function(e) {
            e.preventDefault();
            alert('Forecast submitted successfully! Buyer will receive complete details.');
            // Would submit to API
        });
    </script>
</body>
</html>
"""

@app.get("/buyer/view-forecasts", response_class=HTMLResponse)
async def buyer_view_forecasts():
    """Buyer sees all supplier forecasts with complete details"""
    
    return """
<!DOCTYPE html>
<html>
<head>
    <title>Supplier Forecasts - Buyer View</title>
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, sans-serif; background: #f5f7fa; padding: 20px; }
        .header { background: white; padding: 30px; border-radius: 12px; margin-bottom: 20px; }
        
        .forecast-summary {
            background: white;
            padding: 20px;
            border-radius: 12px;
            margin-bottom: 20px;
        }
        
        .supplier-forecasts {
            display: grid;
            gap: 20px;
        }
        
        .forecast-card {
            background: white;
            border: 2px solid #e0e0e0;
            border-radius: 12px;
            overflow: hidden;
        }
        
        .forecast-header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
        }
        
        .forecast-body {
            padding: 20px;
        }
        
        .comparison-table {
            width: 100%;
            border-collapse: collapse;
        }
        
        .comparison-table th {
            background: #f8f9fa;
            padding: 10px;
            text-align: left;
            font-size: 13px;
        }
        
        .comparison-table td {
            padding: 10px;
            border-bottom: 1px solid #f0f0f0;
        }
        
        .best-price {
            background: #d4edda;
            font-weight: bold;
        }
        
        .btn-negotiate {
            padding: 10px 20px;
            background: #667eea;
            color: white;
            border: none;
            border-radius: 6px;
            cursor: pointer;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>📊 Supplier Forecasts Received</h1>
        <p>Complete details from 3 suppliers for Sunflower Oil RFQ</p>
    </div>
    
    <div class="forecast-summary">
        <h3>Quick Comparison</h3>
        <table class="comparison-table">
            <thead>
                <tr>
                    <th>Supplier</th>
                    <th>Product</th>
                    <th>Price/Unit</th>
                    <th>MOQ</th>
                    <th>Payment</th>
                    <th>Delivery</th>
                    <th>Certificates</th>
                    <th>Action</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td><strong>Global Oils Ltd</strong><br>Spain</td>
                    <td>Sunflower Oil 1L</td>
                    <td class="best-price">$3.20</td>
                    <td>1000</td>
                    <td>30% advance</td>
                    <td>21 days</td>
                    <td>ISO, HACCP</td>
                    <td><button class="btn-negotiate">Negotiate</button></td>
                </tr>
                <tr>
                    <td><strong>Mediterranean Trading</strong><br>Italy</td>
                    <td>Sunflower Oil 1L</td>
                    <td>$3.35</td>
                    <td>2000</td>
                    <td>Net 30</td>
                    <td>25 days</td>
                    <td>ISO, BRC, Organic</td>
                    <td><button class="btn-negotiate">Negotiate</button></td>
                </tr>
                <tr>
                    <td><strong>Sun Products SA</strong><br>Greece</td>
                    <td>Sunflower Oil 1L</td>
                    <td>$3.45</td>
                    <td>500</td>
                    <td>LC</td>
                    <td>30 days</td>
                    <td>ISO, Kosher</td>
                    <td><button class="btn-negotiate">Negotiate</button></td>
                </tr>
            </tbody>
        </table>
    </div>
    
    <!-- Detailed Forecast Cards -->
    <div class="supplier-forecasts">
        <div class="forecast-card">
            <div class="forecast-header">
                <h3>Global Oils Ltd - Complete Forecast</h3>
                <p>Best Price: $3.20/bottle</p>
            </div>
            <div class="forecast-body">
                <h4>Product Variations Available:</h4>
                <table class="comparison-table">
                    <tr>
                        <td>Sunflower Oil 1L Bottle</td>
                        <td>$3.20</td>
                        <td>MOQ: 1000</td>
                    </tr>
                    <tr>
                        <td>Sunflower Oil 5L Bottle</td>
                        <td>$15.00</td>
                        <td>MOQ: 500</td>
                    </tr>
                    <tr>
                        <td>Sunflower Oil 20L Drum</td>
                        <td>$58.00</td>
                        <td>MOQ: 100</td>
                    </tr>
                </table>
                
                <h4>Volume Pricing:</h4>
                <p>1-1000: $3.50 | 1001-5000: $3.20 | 5000+: $3.00</p>
                
                <h4>Additional Terms:</h4>
                <p>✓ Private label available | ✓ Free samples | ✓ Monthly capacity: 50,000L</p>
            </div>
        </div>
    </div>
</body>
</html>
"""

if __name__ == "__main__":
    import uvicorn
    print("\n" + "="*60)
    print("SUPPLIER FORECAST SYSTEM")
    print("="*60)
    print("\nComplete forecast details, not just price!")
    print("\nSupplier form: http://localhost:8000/supplier/forecast/1")
    print("Buyer view: http://localhost:8000/buyer/view-forecasts")
    uvicorn.run(app, host="0.0.0.0", port=8000)