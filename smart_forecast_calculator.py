"""
SMART FORECAST CALCULATOR WITH AI
Automatically calculates container loading, palletization, and optimization
"""

from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, JSONResponse
from typing import Dict, List, Optional
import json
from datetime import datetime

app = FastAPI(title="Smart Forecast Calculator")

# CONTAINER SPECIFICATIONS
CONTAINER_SPECS = {
    "20ft": {
        "internal_length_m": 5.89,
        "internal_width_m": 2.35,
        "internal_height_m": 2.39,
        "volume_cbm": 33.1,
        "max_weight_kg": 21770,
        "door_width_m": 2.34,
        "door_height_m": 2.28
    },
    "40ft": {
        "internal_length_m": 12.03,
        "internal_width_m": 2.35,
        "internal_height_m": 2.39,
        "volume_cbm": 67.5,
        "max_weight_kg": 26680,
        "door_width_m": 2.34,
        "door_height_m": 2.28
    },
    "40ft_hc": {  # High Cube
        "internal_length_m": 12.03,
        "internal_width_m": 2.35,
        "internal_height_m": 2.70,  # Higher!
        "volume_cbm": 76.2,
        "max_weight_kg": 26480,
        "door_width_m": 2.34,
        "door_height_m": 2.58
    },
    "40ft_reefer": {  # Refrigerated
        "internal_length_m": 11.58,  # Less due to refrigeration unit
        "internal_width_m": 2.29,
        "internal_height_m": 2.40,
        "volume_cbm": 63.6,
        "max_weight_kg": 25480,
        "temp_range": "-30°C to +30°C"
    }
}

# PALLET TYPES
PALLET_TYPES = {
    "euro": {
        "length_m": 1.2,
        "width_m": 0.8,
        "height_m": 0.144,
        "weight_kg": 25,
        "max_load_kg": 1500
    },
    "standard": {
        "length_m": 1.2,
        "width_m": 1.0,
        "height_m": 0.15,
        "weight_kg": 30,
        "max_load_kg": 2000
    },
    "american": {
        "length_m": 1.219,
        "width_m": 1.016,
        "height_m": 0.15,
        "weight_kg": 35,
        "max_load_kg": 2200
    }
}

def calculate_container_loading(product_data: Dict) -> Dict:
    """
    AI calculates optimal container loading based on product specs
    """
    
    # Extract product dimensions
    carton_length = product_data.get("carton_length_cm", 40) / 100  # Convert to meters
    carton_width = product_data.get("carton_width_cm", 30) / 100
    carton_height = product_data.get("carton_height_cm", 25) / 100
    carton_weight = product_data.get("carton_weight_kg", 15)
    units_per_carton = product_data.get("units_per_carton", 12)
    
    # Pallet configuration
    use_pallets = product_data.get("use_pallets", True)
    pallet_type = product_data.get("pallet_type", "euro")
    can_double_stack = product_data.get("can_double_stack", False)
    
    results = {}
    
    for container_type, specs in CONTAINER_SPECS.items():
        # Calculate without pallets (floor loading)
        cartons_per_layer_length = int(specs["internal_length_m"] / carton_length)
        cartons_per_layer_width = int(specs["internal_width_m"] / carton_width)
        cartons_per_layer = cartons_per_layer_length * cartons_per_layer_width
        
        # Height calculation
        available_height = specs["internal_height_m"]
        layers = int(available_height / carton_height)
        
        # Total cartons without pallets
        total_cartons_no_pallet = cartons_per_layer * layers
        total_units_no_pallet = total_cartons_no_pallet * units_per_carton
        total_weight_no_pallet = total_cartons_no_pallet * carton_weight
        
        # Calculate with pallets
        if use_pallets:
            pallet = PALLET_TYPES[pallet_type]
            
            # Pallets per container
            pallets_per_row_length = int(specs["internal_length_m"] / pallet["length_m"])
            pallets_per_row_width = int(specs["internal_width_m"] / pallet["width_m"])
            total_pallets = pallets_per_row_length * pallets_per_row_width
            
            # Cartons per pallet
            cartons_per_pallet_length = int(pallet["length_m"] / carton_length)
            cartons_per_pallet_width = int(pallet["width_m"] / carton_width)
            cartons_per_pallet_base = cartons_per_pallet_length * cartons_per_pallet_width
            
            # Height on pallet
            available_pallet_height = available_height - pallet["height_m"]
            if can_double_stack:
                available_pallet_height = (available_height - 2 * pallet["height_m"]) / 2
            
            layers_on_pallet = int(available_pallet_height / carton_height)
            cartons_per_pallet = cartons_per_pallet_base * layers_on_pallet
            
            # Total with pallets
            if can_double_stack:
                total_pallets *= 2  # Double stacked
            
            total_cartons_pallet = total_pallets * cartons_per_pallet
            total_units_pallet = total_cartons_pallet * units_per_carton
            total_weight_pallet = (total_cartons_pallet * carton_weight) + (total_pallets * pallet["weight_kg"])
        else:
            total_pallets = 0
            total_cartons_pallet = 0
            total_units_pallet = 0
            total_weight_pallet = 0
        
        # Check weight limits
        weight_ok_no_pallet = total_weight_no_pallet <= specs["max_weight_kg"]
        weight_ok_pallet = total_weight_pallet <= specs["max_weight_kg"]
        
        results[container_type] = {
            "without_pallets": {
                "cartons": total_cartons_no_pallet,
                "units": total_units_no_pallet,
                "weight_kg": total_weight_no_pallet,
                "weight_ok": weight_ok_no_pallet,
                "utilization": round((total_cartons_no_pallet * carton_length * carton_width * carton_height) / specs["volume_cbm"] * 100, 1)
            },
            "with_pallets": {
                "pallets": total_pallets,
                "cartons": total_cartons_pallet,
                "units": total_units_pallet,
                "weight_kg": total_weight_pallet,
                "weight_ok": weight_ok_pallet,
                "double_stacked": can_double_stack
            }
        }
    
    return results

@app.get("/", response_class=HTMLResponse)
async def smart_forecast_form():
    """Smart forecast form with minimal questions"""
    
    return """
<!DOCTYPE html>
<html>
<head>
    <title>Smart Forecast Calculator</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: -apple-system, BlinkMacSystemFont, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 20px;
            overflow: hidden;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
        }
        
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }
        
        .two-column {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 2px;
            background: #e0e0e0;
        }
        
        .input-section {
            background: white;
            padding: 30px;
        }
        
        .results-section {
            background: #f8f9fa;
            padding: 30px;
        }
        
        .section-title {
            font-size: 18px;
            font-weight: 600;
            margin-bottom: 20px;
            color: #333;
            border-bottom: 2px solid #667eea;
            padding-bottom: 10px;
        }
        
        .form-group {
            margin-bottom: 20px;
        }
        
        label {
            display: block;
            font-size: 13px;
            color: #666;
            margin-bottom: 5px;
            font-weight: 600;
        }
        
        input, select {
            width: 100%;
            padding: 10px;
            border: 1px solid #ddd;
            border-radius: 6px;
            font-size: 14px;
        }
        
        input:focus {
            outline: none;
            border-color: #667eea;
            box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
        }
        
        .radio-group {
            display: flex;
            gap: 20px;
            margin-top: 10px;
        }
        
        .btn-calculate {
            width: 100%;
            padding: 15px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 8px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            margin-top: 20px;
        }
        
        .btn-calculate:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
        }
        
        .container-result {
            background: white;
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 15px;
            border: 2px solid #e0e0e0;
        }
        
        .container-name {
            font-weight: 600;
            color: #667eea;
            margin-bottom: 10px;
            font-size: 16px;
        }
        
        .result-grid {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 10px;
            font-size: 14px;
        }
        
        .result-item {
            padding: 8px;
            background: #f8f9fa;
            border-radius: 4px;
        }
        
        .result-label {
            color: #666;
            font-size: 12px;
        }
        
        .result-value {
            font-weight: 600;
            color: #333;
            font-size: 16px;
        }
        
        .best-option {
            background: #d4edda;
            border-color: #28a745;
        }
        
        .warning {
            background: #fff3cd;
            border-color: #ffc107;
        }
        
        .ai-suggestions {
            background: linear-gradient(135deg, #e3f2fd, #f3e5f5);
            padding: 20px;
            border-radius: 8px;
            margin-top: 20px;
        }
        
        .suggestion-title {
            font-weight: 600;
            color: #1976d2;
            margin-bottom: 10px;
        }
        
        .suggestion-item {
            margin: 5px 0;
            font-size: 14px;
        }
        
        .temperature-warning {
            background: #ffebee;
            color: #c62828;
            padding: 10px;
            border-radius: 6px;
            margin-top: 10px;
            font-size: 13px;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🤖 Smart Forecast Calculator</h1>
            <p>AI-powered container loading optimization</p>
        </div>
        
        <div class="two-column">
            <!-- Input Section -->
            <div class="input-section">
                <div class="section-title">📦 Product Information (Minimal Questions)</div>
                
                <div class="form-group">
                    <label>Product Name</label>
                    <input type="text" id="product_name" placeholder="e.g., Sunflower Oil 1L" value="Sunflower Oil 1L">
                </div>
                
                <div class="form-group">
                    <label>Price per Unit (USD)</label>
                    <input type="number" id="unit_price" step="0.01" placeholder="3.20" value="3.20">
                </div>
                
                <div class="form-group">
                    <label>Units per Master Carton</label>
                    <input type="number" id="units_per_carton" placeholder="12" value="12">
                </div>
                
                <div class="form-group">
                    <label>Master Carton Dimensions (cm)</label>
                    <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px;">
                        <input type="number" id="carton_length" placeholder="Length" value="40">
                        <input type="number" id="carton_width" placeholder="Width" value="30">
                        <input type="number" id="carton_height" placeholder="Height" value="25">
                    </div>
                </div>
                
                <div class="form-group">
                    <label>Carton Weight (kg)</label>
                    <input type="number" id="carton_weight" step="0.1" placeholder="15" value="15">
                </div>
                
                <div class="form-group">
                    <label>Delivery Method</label>
                    <div class="radio-group">
                        <label><input type="radio" name="pallets" value="yes" checked> With Pallets</label>
                        <label><input type="radio" name="pallets" value="no"> Floor Loading</label>
                    </div>
                </div>
                
                <div class="form-group" id="pallet-options">
                    <label>Pallet Type</label>
                    <select id="pallet_type">
                        <option value="euro">Euro Pallet (120x80cm)</option>
                        <option value="standard">Standard (120x100cm)</option>
                        <option value="american">American (48x40")</option>
                    </select>
                </div>
                
                <div class="form-group">
                    <label>Can Double Stack?</label>
                    <div class="radio-group">
                        <label><input type="radio" name="double_stack" value="yes"> Yes</label>
                        <label><input type="radio" name="double_stack" value="no" checked> No</label>
                    </div>
                </div>
                
                <div class="form-group">
                    <label>Temperature Requirements</label>
                    <select id="temp_requirement">
                        <option value="ambient">Ambient (No cooling)</option>
                        <option value="chilled">Chilled (2-8°C)</option>
                        <option value="frozen">Frozen (-18°C)</option>
                        <option value="controlled">Controlled (specify)</option>
                    </select>
                </div>
                
                <button class="btn-calculate" onclick="calculateLoading()">
                    🚀 Calculate Container Loading
                </button>
            </div>
            
            <!-- Results Section -->
            <div class="results-section">
                <div class="section-title">📊 Container Loading Results</div>
                
                <div id="results">
                    <div style="text-align: center; padding: 40px; color: #999;">
                        Enter product details and click Calculate
                    </div>
                </div>
                
                <div class="ai-suggestions" style="display: none;" id="ai-suggestions">
                    <div class="suggestion-title">🤖 AI Recommendations</div>
                    <div id="suggestions-content"></div>
                </div>
            </div>
        </div>
    </div>
    
    <script>
        // Show/hide pallet options
        document.querySelectorAll('input[name="pallets"]').forEach(radio => {
            radio.addEventListener('change', function() {
                document.getElementById('pallet-options').style.display = 
                    this.value === 'yes' ? 'block' : 'none';
            });
        });
        
        function calculateLoading() {
            // Gather input data
            const data = {
                product_name: document.getElementById('product_name').value,
                unit_price: parseFloat(document.getElementById('unit_price').value),
                units_per_carton: parseInt(document.getElementById('units_per_carton').value),
                carton_length_cm: parseInt(document.getElementById('carton_length').value),
                carton_width_cm: parseInt(document.getElementById('carton_width').value),
                carton_height_cm: parseInt(document.getElementById('carton_height').value),
                carton_weight_kg: parseFloat(document.getElementById('carton_weight').value),
                use_pallets: document.querySelector('input[name="pallets"]:checked').value === 'yes',
                pallet_type: document.getElementById('pallet_type').value,
                can_double_stack: document.querySelector('input[name="double_stack"]:checked').value === 'yes',
                temp_requirement: document.getElementById('temp_requirement').value
            };
            
            // Calculate loading for all container types
            const results = calculateContainerLoading(data);
            displayResults(results, data);
        }
        
        function calculateContainerLoading(data) {
            // This would call the Python backend
            // For demo, using simplified calculations
            
            const containers = {
                '20ft': { volume: 33.1, maxWeight: 21770 },
                '40ft': { volume: 67.5, maxWeight: 26680 },
                '40ft HC': { volume: 76.2, maxWeight: 26480 },
                '40ft Reefer': { volume: 63.6, maxWeight: 25480 }
            };
            
            const results = {};
            
            for (const [type, specs] of Object.entries(containers)) {
                // Skip non-reefer if temperature required
                if (data.temp_requirement !== 'ambient' && !type.includes('Reefer')) {
                    continue;
                }
                
                // Simple calculation for demo
                const cartonVolume = (data.carton_length_cm * data.carton_width_cm * data.carton_height_cm) / 1000000;
                const maxCartons = Math.floor(specs.volume / cartonVolume * 0.85); // 85% efficiency
                const totalWeight = maxCartons * data.carton_weight_kg;
                const weightOk = totalWeight <= specs.maxWeight;
                
                results[type] = {
                    cartons: maxCartons,
                    units: maxCartons * data.units_per_carton,
                    weight_kg: totalWeight,
                    weight_ok: weightOk,
                    pallets: data.use_pallets ? Math.floor(maxCartons / 60) : 0
                };
            }
            
            return results;
        }
        
        function displayResults(results, data) {
            let html = '';
            let bestOption = null;
            let maxUnits = 0;
            
            for (const [container, stats] of Object.entries(results)) {
                const isWarning = !stats.weight_ok;
                const units = stats.units;
                
                if (units > maxUnits && stats.weight_ok) {
                    maxUnits = units;
                    bestOption = container;
                }
                
                html += `
                    <div class="container-result ${bestOption === container ? 'best-option' : ''} ${isWarning ? 'warning' : ''}">
                        <div class="container-name">${container}</div>
                        <div class="result-grid">
                            <div class="result-item">
                                <div class="result-label">Units</div>
                                <div class="result-value">${stats.units.toLocaleString()}</div>
                            </div>
                            <div class="result-item">
                                <div class="result-label">Cartons</div>
                                <div class="result-value">${stats.cartons.toLocaleString()}</div>
                            </div>
                            <div class="result-item">
                                <div class="result-label">Weight</div>
                                <div class="result-value">${(stats.weight_kg/1000).toFixed(1)}t</div>
                            </div>
                            <div class="result-item">
                                <div class="result-label">Pallets</div>
                                <div class="result-value">${stats.pallets || 'Floor'}</div>
                            </div>
                        </div>
                        ${isWarning ? '<div class="temperature-warning">⚠️ Weight limit exceeded!</div>' : ''}
                    </div>
                `;
            }
            
            document.getElementById('results').innerHTML = html;
            
            // AI Suggestions
            const suggestions = generateAISuggestions(results, data, bestOption);
            document.getElementById('suggestions-content').innerHTML = suggestions;
            document.getElementById('ai-suggestions').style.display = 'block';
        }
        
        function generateAISuggestions(results, data, bestOption) {
            let suggestions = '<ul style="margin: 0; padding-left: 20px;">';
            
            // Best container suggestion
            suggestions += `<li>✅ Best option: <strong>${bestOption}</strong> with ${results[bestOption].units.toLocaleString()} units</li>`;
            
            // Palletization advice
            if (data.use_pallets) {
                suggestions += '<li>💡 Consider floor loading for 15-20% more capacity</li>';
            } else if (data.product_name.toLowerCase().includes('glass')) {
                suggestions += '<li>⚠️ Glass products should use pallets for safety</li>';
            }
            
            // Temperature advice
            if (data.temp_requirement !== 'ambient') {
                suggestions += '<li>🌡️ Use 40ft Reefer container for temperature control</li>';
            }
            
            // Weight optimization
            const weight40 = results['40ft'] ? results['40ft'].weight_kg : 0;
            if (weight40 > 24000) {
                suggestions += '<li>⚖️ Consider reducing quantity to stay under 24 tons</li>';
            }
            
            // Double stacking
            if (!data.can_double_stack && data.carton_weight_kg < 20) {
                suggestions += '<li>📦 Ask supplier about double-stacking possibility</li>';
            }
            
            suggestions += '</ul>';
            
            // Cost calculation
            const totalValue = results[bestOption].units * data.unit_price;
            suggestions += `
                <div style="margin-top: 15px; padding: 10px; background: white; border-radius: 6px;">
                    <strong>Container Value:</strong> $${totalValue.toLocaleString()}<br>
                    <strong>Cost per unit delivered:</strong> $${(totalValue / results[bestOption].units).toFixed(3)}
                </div>
            `;
            
            return suggestions;
        }
    </script>
</body>
</html>
"""

@app.post("/api/calculate", response_class=JSONResponse)
async def api_calculate_loading(request: Request):
    """API endpoint for container calculations"""
    data = await request.json()
    results = calculate_container_loading(data)
    
    # Add AI recommendations
    recommendations = {
        "best_container": max(results.items(), key=lambda x: x[1]["without_pallets"]["units"])[0],
        "palletization_advice": "Use pallets for fragile goods" if "glass" in data.get("product_name", "").lower() else "Floor loading maximizes space",
        "weight_warning": any(r["without_pallets"]["weight_kg"] > 24000 for r in results.values()),
        "temperature_needs": data.get("temp_requirement", "ambient") != "ambient"
    }
    
    return {
        "results": results,
        "recommendations": recommendations,
        "timestamp": datetime.now().isoformat()
    }

if __name__ == "__main__":
    import uvicorn
    print("\n" + "="*60)
    print("SMART FORECAST CALCULATOR")
    print("="*60)
    print("\nFeatures:")
    print("✓ Minimal questions for suppliers")
    print("✓ Auto-calculates container loading")
    print("✓ Palletization optimization")
    print("✓ Weight limit checks (24 tons)")
    print("✓ Temperature requirements")
    print("✓ AI recommendations")
    print("\nOpen: http://localhost:8000")
    uvicorn.run(app, host="0.0.0.0", port=8000)