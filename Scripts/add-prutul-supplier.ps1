# PowerShell script to add Prutul supplier via API

$baseUrl = "https://localhost:53812"

# Create Prutul supplier user
$supplierData = @{
    username = "prutul_sa"
    password = "TempPassword123!"
    email = "office@prutul.ro"
    companyName = "Prutul S.A."
    type = 3  # Supplier
    country = "Romania"
    phoneNumber = "+40 236 466 100"
    website = "www.prutul.ro"
    address = "Galati Commercial Harbor, Galati County, Romania"
    category = "Vegetable Oil Producer"
    categoryId = 1  # Manufacturer
    businessType = "Vegetable Oil Manufacturer & Exporter"
}

# First, let's create the user via API
$jsonBody = $supplierData | ConvertTo-Json
Write-Host "Creating Prutul supplier account..." -ForegroundColor Green

try {
    # Note: Using -SkipCertificateCheck for self-signed cert
    $response = Invoke-RestMethod -Uri "$baseUrl/api/Users/register-supplier" `
        -Method Post `
        -Body $jsonBody `
        -ContentType "application/json" `
        -SkipCertificateCheck
    
    $supplierId = $response.id
    Write-Host "Created supplier with ID: $supplierId" -ForegroundColor Green
    
    # Now add products to the catalog
    $products = @(
        @{
            productName = "Refined Sunflower Oil - Conventional (Linoleic) 1L"
            productCode = "PRUT-SUN-1L"
            category = "Vegetable Oils"
            subCategory = "Sunflower Oil"
            brand = "Prutul"
            description = "Premium quality refined sunflower oil, conventional type with high linoleic acid content. Perfect for cooking, frying, and salad dressing."
            minOrderQuantity = 1000
            unit = "Bottles (1L)"
            pricePerUnit = 2.50
            currency = "EUR"
            isAvailable = $true
            leadTimeDays = 14
            countryOfOrigin = "Romania"
            qualityScore = 95
        },
        @{
            productName = "High Oleic Sunflower Oil - Spornic Premium/Omega 9 1L"
            productCode = "PRUT-HO-1L"
            category = "Vegetable Oils"
            subCategory = "Sunflower Oil"
            brand = "Spornic Premium"
            description = "First 100% Romanian High Oleic sunflower oil with min. 75% oleic acid. Premium quality for household consumers."
            minOrderQuantity = 1000
            unit = "Bottles (1L)"
            pricePerUnit = 3.20
            currency = "EUR"
            isAvailable = $true
            leadTimeDays = 14
            countryOfOrigin = "Romania"
            qualityScore = 98
        },
        @{
            productName = "Refined Sunflower Oil - Family Pack 5L"
            productCode = "PRUT-SUN-5L"
            category = "Vegetable Oils"
            subCategory = "Sunflower Oil"
            brand = "Prutul"
            description = "Economy family pack refined sunflower oil. Ideal for households and small restaurants."
            minOrderQuantity = 500
            unit = "Bottles (5L)"
            pricePerUnit = 11.50
            currency = "EUR"
            isAvailable = $true
            leadTimeDays = 14
            countryOfOrigin = "Romania"
            qualityScore = 95
        }
    )
    
    foreach ($product in $products) {
        $product.supplierId = $supplierId
        $productJson = $product | ConvertTo-Json
        
        Write-Host "Adding product: $($product.productName)" -ForegroundColor Yellow
        
        $productResponse = Invoke-RestMethod -Uri "$baseUrl/api/SupplierProductCatalog" `
            -Method Post `
            -Body $productJson `
            -ContentType "application/json" `
            -SkipCertificateCheck
        
        Write-Host "Added product successfully" -ForegroundColor Green
    }
    
    Write-Host "`nSuccessfully added Prutul S.A. with sunflower oil products!" -ForegroundColor Green
    Write-Host "Supplier ID: $supplierId" -ForegroundColor Cyan
    
} catch {
    Write-Host "Error: $_" -ForegroundColor Red
}