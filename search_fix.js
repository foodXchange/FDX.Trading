async function searchSuppliers(event) {
    event.preventDefault();
    
    const query = document.getElementById('searchQuery').value;
    const countries = Array.from(document.getElementById('countries').selectedOptions).map(o => o.value);
    const types = Array.from(document.getElementById('supplierTypes').selectedOptions).map(o => o.value);
    const useAI = document.getElementById('useAI').checked;
    
    document.getElementById('loading').style.display = 'block';
    document.getElementById('results').innerHTML = '';
    document.getElementById('actionBar').style.display = 'none';
    
    try {
        // Use the simple search API instead of AI search
        const formData = new URLSearchParams();
        formData.append('query', query);
        
        const response = await fetch('/api/search', {
            method: 'POST',
            headers: {'Content-Type': 'application/x-www-form-urlencoded'},
            body: formData
        });
        
        const data = await response.json();
        document.getElementById('loading').style.display = 'none';
        
        if (data.error) {
            alert('Error: ' + data.error);
            return;
        }
        
        // Transform simple search results to match AI search format
        const transformedData = {
            suppliers: data.results.map(result => ({
                id: result.supplier_id,
                supplier_name: result.supplier_name,
                company_name: result.company_name,
                country: result.country,
                company_email: result.email,
                company_website: result.website,
                supplier_type: result.supplier_type || 'Supplier',
                products: result.product_preview,
                ai_score: Math.round(result.match_percentage),
                score: result.score || 0
            }))
        };
        
        // Apply country and type filters if selected
        if (countries.length > 0) {
            transformedData.suppliers = transformedData.suppliers.filter(s => 
                countries.includes(s.country)
            );
        }
        
        if (types.length > 0) {
            transformedData.suppliers = transformedData.suppliers.filter(s => 
                types.some(type => s.supplier_type && s.supplier_type.includes(type))
            );
        }
        
        displayResults(transformedData);
        
        // Reload search history after successful search
        setTimeout(loadSearchHistory, 500);
    } catch (error) {
        document.getElementById('loading').style.display = 'none';
        alert('Error: ' + error.message);
    }
}