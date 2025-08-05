"""
Integrated Search Interface for FoodXchange
==========================================
Combines AI search, project management, and email campaign tracking
"""

from flask import Flask, render_template, request, jsonify, session
import psycopg2
from psycopg2.extras import RealDictCursor
import os
from dotenv import load_dotenv
from datetime import datetime
import json
from ai_search_system import AISearchSystem
from sourcing_campaign_system import SourcingCampaignSystem
from email_response_analyzer import EmailResponseAnalyzer
import sys

# Fix Windows encoding
sys.stdout.reconfigure(encoding='utf-8')

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'your-secret-key-here')

# Initialize systems
search_system = AISearchSystem()
campaign_system = SourcingCampaignSystem()
response_analyzer = EmailResponseAnalyzer()

@app.route('/')
def index():
    """Main search interface"""
    return render_template('search_interface.html')

@app.route('/api/search', methods=['POST'])
def search_suppliers():
    """Execute AI-powered search"""
    
    data = request.json
    query = data.get('query', '')
    filters = data.get('filters', {})
    user_email = session.get('user_email', 'user@foodxchange.com')
    
    # Execute search
    results = search_system.ai_search_suppliers(
        query=query,
        user_email=user_email,
        filters=filters,
        limit=50
    )
    
    return jsonify(results)

@app.route('/api/projects', methods=['GET'])
def get_projects():
    """Get user's projects"""
    
    user_email = session.get('user_email', 'user@foodxchange.com')
    
    conn = psycopg2.connect(os.getenv('DATABASE_URL'), cursor_factory=RealDictCursor)
    cur = conn.cursor()
    
    cur.execute("""
        SELECT p.*, COUNT(ps.id) as supplier_count
        FROM projects p
        LEFT JOIN project_suppliers ps ON p.id = ps.project_id
        WHERE p.user_email = %s
        GROUP BY p.id
        ORDER BY p.created_at DESC
    """, (user_email,))
    
    projects = cur.fetchall()
    cur.close()
    conn.close()
    
    return jsonify({'projects': projects})

@app.route('/api/add-to-project', methods=['POST'])
def add_to_project():
    """Add selected suppliers to project"""
    
    data = request.json
    supplier_ids = data.get('supplier_ids', [])
    project_id = data.get('project_id')
    project_name = data.get('project_name')
    user_email = session.get('user_email', 'user@foodxchange.com')
    
    result = search_system.add_suppliers_to_project(
        supplier_ids=supplier_ids,
        project_id=project_id,
        project_name=project_name,
        user_email=user_email
    )
    
    return jsonify(result)

@app.route('/api/save-search', methods=['POST'])
def save_search():
    """Save search for later"""
    
    data = request.json
    user_email = session.get('user_email', 'user@foodxchange.com')
    
    saved_id = search_system.save_search(
        user_email=user_email,
        search_name=data.get('name'),
        query=data.get('query'),
        filters=data.get('filters'),
        alert_enabled=data.get('alert_enabled', False)
    )
    
    return jsonify({'saved_id': saved_id, 'success': True})

@app.route('/api/search-history', methods=['GET'])
def search_history():
    """Get user's search history"""
    
    user_email = session.get('user_email', 'user@foodxchange.com')
    history = search_system.get_search_history(user_email, limit=20)
    
    return jsonify({'history': history})

@app.route('/api/popular-searches', methods=['GET'])
def popular_searches():
    """Get trending searches"""
    
    popular = search_system.get_popular_searches(limit=10)
    return jsonify({'popular': popular})

@app.route('/api/campaign-analytics/<campaign_id>', methods=['GET'])
def campaign_analytics(campaign_id):
    """Get email campaign analytics"""
    
    analytics = response_analyzer.get_campaign_analytics(campaign_id)
    return jsonify(analytics)

# Create the HTML template
html_template = '''
<!DOCTYPE html>
<html>
<head>
    <title>FoodXchange AI Search</title>
    <meta charset="UTF-8">
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body { font-family: Arial, sans-serif; background: #f5f5f5; }
        .container { max-width: 1400px; margin: 0 auto; padding: 20px; }
        .header { background: white; padding: 20px; border-radius: 8px; margin-bottom: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .search-box { display: flex; gap: 10px; margin-bottom: 20px; }
        .search-input { flex: 1; padding: 12px; border: 2px solid #ddd; border-radius: 4px; font-size: 16px; }
        .search-button { padding: 12px 24px; background: #2c3e50; color: white; border: none; border-radius: 4px; cursor: pointer; font-size: 16px; }
        .search-button:hover { background: #34495e; }
        .filters { display: flex; gap: 15px; margin-bottom: 20px; flex-wrap: wrap; }
        .filter-group { display: flex; align-items: center; gap: 5px; }
        .results-container { display: flex; gap: 20px; }
        .results-panel { flex: 1; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .sidebar { width: 300px; }
        .result-item { border: 1px solid #eee; padding: 15px; margin-bottom: 10px; border-radius: 4px; position: relative; }
        .result-item:hover { background: #f9f9f9; }
        .result-checkbox { position: absolute; top: 15px; right: 15px; width: 20px; height: 20px; cursor: pointer; }
        .result-header { display: flex; justify-content: space-between; margin-bottom: 10px; }
        .supplier-name { font-weight: bold; font-size: 16px; color: #2c3e50; }
        .match-score { background: #27ae60; color: white; padding: 4px 8px; border-radius: 4px; font-size: 12px; }
        .supplier-details { color: #666; font-size: 14px; margin-bottom: 8px; }
        .matched-terms { display: flex; gap: 5px; flex-wrap: wrap; margin-top: 8px; }
        .term-badge { background: #e8f4f8; color: #2980b9; padding: 3px 8px; border-radius: 3px; font-size: 12px; }
        .action-buttons { position: fixed; bottom: 20px; right: 20px; display: flex; gap: 10px; }
        .action-button { padding: 12px 20px; background: #27ae60; color: white; border: none; border-radius: 4px; cursor: pointer; font-size: 14px; }
        .action-button:hover { background: #229954; }
        .selected-count { background: #e74c3c; color: white; padding: 8px 15px; border-radius: 20px; }
        .stats-card { background: #f8f9fa; padding: 15px; border-radius: 4px; margin-bottom: 15px; }
        .stats-card h4 { margin-bottom: 10px; color: #2c3e50; }
        .trending-item { padding: 8px 0; border-bottom: 1px solid #eee; cursor: pointer; }
        .trending-item:hover { color: #2980b9; }
        .history-item { padding: 10px; background: #f8f9fa; margin-bottom: 5px; border-radius: 4px; font-size: 14px; cursor: pointer; }
        .history-item:hover { background: #e8f4f8; }
        .loading { text-align: center; padding: 40px; color: #666; }
        .no-results { text-align: center; padding: 40px; color: #999; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔍 FoodXchange AI Product Search</h1>
            <p style="margin-top: 10px; color: #666;">Search 16,963 verified suppliers with AI-powered matching</p>
        </div>
        
        <div class="search-box">
            <input type="text" class="search-input" id="searchInput" 
                   placeholder="Search for products (e.g., 'organic olive oil extra virgin', 'chocolate wafer biscuits')" 
                   value="{{ request.args.get('q', '') }}">
            <button class="search-button" onclick="performSearch()">Search Suppliers</button>
        </div>
        
        <div class="filters">
            <div class="filter-group">
                <input type="checkbox" id="verifiedOnly">
                <label for="verifiedOnly">Verified Only</label>
            </div>
            <div class="filter-group">
                <label>Min Rating:</label>
                <select id="minRating">
                    <option value="">Any</option>
                    <option value="3.5">3.5+</option>
                    <option value="4.0">4.0+</option>
                    <option value="4.5">4.5+</option>
                </select>
            </div>
            <div class="filter-group">
                <label>Country:</label>
                <select id="countryFilter" multiple style="width: 200px;">
                    <option value="Italy">Italy</option>
                    <option value="Spain">Spain</option>
                    <option value="Turkey">Turkey</option>
                    <option value="Greece">Greece</option>
                    <option value="USA">USA</option>
                    <option value="Germany">Germany</option>
                    <option value="Poland">Poland</option>
                    <option value="Netherlands">Netherlands</option>
                </select>
            </div>
        </div>
        
        <div class="results-container">
            <div class="sidebar">
                <div class="stats-card">
                    <h4>📊 Search History</h4>
                    <div id="searchHistory"></div>
                </div>
                
                <div class="stats-card">
                    <h4>🔥 Trending Searches</h4>
                    <div id="trendingSearches"></div>
                </div>
                
                <div class="stats-card">
                    <h4>📁 Your Projects</h4>
                    <div id="projectsList"></div>
                </div>
            </div>
            
            <div class="results-panel">
                <div id="resultsHeader" style="margin-bottom: 20px; display: none;">
                    <h3>Search Results</h3>
                    <p id="resultStats" style="color: #666; margin-top: 5px;"></p>
                </div>
                <div id="searchResults">
                    <div class="no-results">
                        Enter a search query to find suppliers
                    </div>
                </div>
            </div>
        </div>
        
        <div class="action-buttons" id="actionButtons" style="display: none;">
            <div class="selected-count" id="selectedCount">0 selected</div>
            <button class="action-button" onclick="addToProject()">Add to Project</button>
            <button class="action-button" style="background: #3498db;" onclick="saveSearch()">Save Search</button>
        </div>
    </div>
    
    <script>
        let currentResults = [];
        let selectedSuppliers = new Set();
        
        // Load initial data
        window.onload = function() {
            loadSearchHistory();
            loadTrendingSearches();
            loadProjects();
            
            // Check if there's a query parameter
            const urlParams = new URLSearchParams(window.location.search);
            const query = urlParams.get('q');
            if (query) {
                document.getElementById('searchInput').value = query;
                performSearch();
            }
        };
        
        function performSearch() {
            const query = document.getElementById('searchInput').value;
            if (!query.trim()) return;
            
            const filters = {
                verified_only: document.getElementById('verifiedOnly').checked,
                min_rating: document.getElementById('minRating').value,
                countries: Array.from(document.getElementById('countryFilter').selectedOptions).map(o => o.value)
            };
            
            document.getElementById('searchResults').innerHTML = '<div class="loading">Searching...</div>';
            document.getElementById('resultsHeader').style.display = 'block';
            
            fetch('/api/search', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({query, filters})
            })
            .then(response => response.json())
            .then(data => {
                currentResults = data.results;
                displayResults(data);
                loadSearchHistory(); // Refresh history
            });
        }
        
        function displayResults(data) {
            const container = document.getElementById('searchResults');
            document.getElementById('resultStats').textContent = 
                `Found ${data.total_results} suppliers in ${data.execution_time_ms}ms`;
            
            if (data.results.length === 0) {
                container.innerHTML = '<div class="no-results">No suppliers found. Try different search terms.</div>';
                return;
            }
            
            container.innerHTML = data.results.map(result => `
                <div class="result-item" data-id="${result.supplier_id}">
                    <input type="checkbox" class="result-checkbox" 
                           onchange="toggleSelection(${result.supplier_id})"
                           ${selectedSuppliers.has(result.supplier_id) ? 'checked' : ''}>
                    
                    <div class="result-header">
                        <div>
                            <div class="supplier-name">${result.supplier_name}</div>
                            <div class="supplier-details">
                                ${result.country} • ${result.email} 
                                ${result.verified ? '• ✓ Verified' : ''}
                                ${result.rating ? `• ⭐ ${result.rating}` : ''}
                            </div>
                        </div>
                        <div class="match-score">${result.match_percentage}% Match</div>
                    </div>
                    
                    <div style="color: #444; font-size: 14px; margin: 10px 0;">
                        ${result.product_preview}...
                    </div>
                    
                    <div class="matched-terms">
                        ${result.matched_terms.map(term => 
                            `<span class="term-badge">${term}</span>`
                        ).join('')}
                    </div>
                    
                    <div style="margin-top: 10px; font-size: 12px; color: #999;">
                        Score breakdown: Product match (${result.scoring_breakdown.product_match}), 
                        Term matches (${result.scoring_breakdown.term_matches}), 
                        Quality (${result.scoring_breakdown.quality_indicators})
                    </div>
                </div>
            `).join('');
            
            updateActionButtons();
        }
        
        function toggleSelection(supplierId) {
            if (selectedSuppliers.has(supplierId)) {
                selectedSuppliers.delete(supplierId);
            } else {
                selectedSuppliers.add(supplierId);
            }
            updateActionButtons();
        }
        
        function updateActionButtons() {
            const count = selectedSuppliers.size;
            if (count > 0) {
                document.getElementById('actionButtons').style.display = 'flex';
                document.getElementById('selectedCount').textContent = `${count} selected`;
            } else {
                document.getElementById('actionButtons').style.display = 'none';
            }
        }
        
        function addToProject() {
            if (selectedSuppliers.size === 0) return;
            
            const projectName = prompt('Enter project name (or leave empty to select existing):');
            
            fetch('/api/add-to-project', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    supplier_ids: Array.from(selectedSuppliers),
                    project_name: projectName
                })
            })
            .then(response => response.json())
            .then(data => {
                alert(`Added ${data.suppliers_added} suppliers to project`);
                selectedSuppliers.clear();
                updateActionButtons();
                loadProjects();
            });
        }
        
        function saveSearch() {
            const query = document.getElementById('searchInput').value;
            const name = prompt('Name this search:');
            if (!name) return;
            
            fetch('/api/save-search', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    name,
                    query,
                    filters: {
                        verified_only: document.getElementById('verifiedOnly').checked,
                        min_rating: document.getElementById('minRating').value
                    }
                })
            })
            .then(response => response.json())
            .then(data => {
                alert('Search saved successfully!');
                loadSearchHistory();
            });
        }
        
        function loadSearchHistory() {
            fetch('/api/search-history')
                .then(response => response.json())
                .then(data => {
                    const container = document.getElementById('searchHistory');
                    container.innerHTML = data.history.slice(0, 5).map(h => `
                        <div class="history-item" onclick="rerunSearch('${h.search_query}')">
                            ${h.search_query} (${h.result_count} results)
                        </div>
                    `).join('');
                });
        }
        
        function loadTrendingSearches() {
            fetch('/api/popular-searches')
                .then(response => response.json())
                .then(data => {
                    const container = document.getElementById('trendingSearches');
                    container.innerHTML = data.popular.map(p => `
                        <div class="trending-item" onclick="rerunSearch('${p.search_term}')">
                            ${p.search_term} (${p.search_count} searches)
                        </div>
                    `).join('');
                });
        }
        
        function loadProjects() {
            fetch('/api/projects')
                .then(response => response.json())
                .then(data => {
                    const container = document.getElementById('projectsList');
                    container.innerHTML = data.projects.map(p => `
                        <div class="history-item">
                            ${p.project_name} (${p.supplier_count} suppliers)
                        </div>
                    `).join('');
                });
        }
        
        function rerunSearch(query) {
            document.getElementById('searchInput').value = query;
            performSearch();
        }
        
        // Enter key support
        document.getElementById('searchInput').addEventListener('keypress', function(e) {
            if (e.key === 'Enter') performSearch();
        });
    </script>
</body>
</html>
'''

# Save the template
os.makedirs('templates', exist_ok=True)
with open('templates/search_interface.html', 'w', encoding='utf-8') as f:
    f.write(html_template)

if __name__ == '__main__':
    print("🚀 Starting FoodXchange AI Search Interface...")
    print("📍 Access at: http://localhost:5000")
    app.run(debug=True, port=5000)