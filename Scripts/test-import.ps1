# Test CSV Product Import Script
$baseUrl = "http://localhost:5000"
$csvPath = "C:\Users\fdxadmin\Downloads\Products 9_8_2025.csv"

# Check if API is running
try {
    $response = Invoke-RestMethod -Uri "$baseUrl/api/products/stats" -Method Get
    Write-Host "API is running. Current stats:" -ForegroundColor Green
    Write-Host "Total products: $($response.totalProducts)"
    Write-Host "Total suppliers with products: $($response.suppliersWithProducts)"
} catch {
    Write-Host "API is not running. Please start the application first." -ForegroundColor Red
    exit 1
}

# Import CSV
Write-Host "`nImporting products from CSV..." -ForegroundColor Yellow

$importRequest = @{
    filePath = $csvPath
} | ConvertTo-Json

try {
    $result = Invoke-RestMethod -Uri "$baseUrl/api/products/import-csv" `
        -Method Post `
        -Body $importRequest `
        -ContentType "application/json"
    
    Write-Host "`nImport Result:" -ForegroundColor Green
    Write-Host "Success: $($result.success)"
    Write-Host "Message: $($result.message)"
    Write-Host "Total Rows: $($result.totalRows)"
    Write-Host "Processed: $($result.processedRows)"
    Write-Host "Products Created: $($result.productsCreated)"
    Write-Host "Products Updated: $($result.productsUpdated)"
    Write-Host "Suppliers Created: $($result.suppliersCreated)"
    
    if ($result.errors -and $result.errors.Count -gt 0) {
        Write-Host "`nErrors:" -ForegroundColor Yellow
        $result.errors | Select-Object -First 10 | ForEach-Object { Write-Host "  - $_" }
    }
    
    # Get catalog summary
    Write-Host "`nFetching supplier catalog summary..." -ForegroundColor Yellow
    $suppliers = Invoke-RestMethod -Uri "$baseUrl/api/products/suppliers/catalog-summary" -Method Get
    
    Write-Host "`nTop Suppliers by Product Count:" -ForegroundColor Green
    $suppliers | Select-Object -First 10 | ForEach-Object {
        Write-Host "  $($_.companyName) ($($_.country)): $($_.productCount) products"
    }
    
} catch {
    Write-Host "Import failed: $_" -ForegroundColor Red
    Write-Host $_.Exception.Response.StatusDescription -ForegroundColor Red
}