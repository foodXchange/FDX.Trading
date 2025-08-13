# Supplier Matching System - User Instructions

## How to Use Supplier Matching

The supplier matching system has been successfully implemented and fixed. To see matched suppliers for a sourcing brief:

### Steps:

1. **Navigate to Sourcing Brief Page**
   - Go to: http://localhost:53813/sourcing-brief.html
   - Or access via the main dashboard

2. **Select a Brief**
   - Click on any sourcing brief from the list
   - Or go directly to: http://localhost:53813/sourcing-brief.html?briefId=4

3. **Find Matching Suppliers**
   - In the brief details view, locate the "Matched Suppliers" section
   - Click the **"Find Matching Suppliers"** button (blue button with search icon)
   - The system will search and display matching suppliers

### What You'll See:

- **Supplier Name**: Company name of the matched supplier
- **Match Score**: Percentage score (0-100%) indicating match quality
- **Matched Products**: Number of products the supplier offers that match your requirements
- **Product List**: First 3 matching products from the supplier's catalog

### Match Scoring Levels:

- **100%**: Exact Product Match - Supplier has the exact product you need
- **80%**: Category Match - Supplier operates in the same product category
- **60%**: Business Type Match - Supplier has relevant business capabilities
- **40%**: Product Family Match - Supplier offers related products
- **20%**: Keyword Match - Basic relevance based on keywords

### Example:

For Brief ID 4 (Sunflower Oil):
1. Go to: http://localhost:53813/sourcing-brief.html?briefId=4
2. Click "Find Matching Suppliers" button
3. View the list of suppliers with scores and matching products

### Notes:

- The matching is performed in real-time when you click the button
- Results are sorted by match score (highest first)
- Maximum of 30 suppliers are shown
- Minimum match threshold is 20%

## Technical Details

The system uses a comprehensive 5-level matching algorithm that analyzes:
- Product catalogs
- Supplier categories
- Business types
- Product families
- Keywords and descriptions

All scores are properly normalized to 0-100% range and suppliers are displayed with their company names (not "undefined").