# Upload Ardo Logo with direct base64

# Ignore SSL certificate errors for testing
add-type @"
    using System.Net;
    using System.Security.Cryptography.X509Certificates;
    public class TrustAllCertsPolicy : ICertificatePolicy {
        public bool CheckValidationResult(
            ServicePoint srvPoint, X509Certificate certificate,
            WebRequest request, int certificateProblem) {
            return true;
        }
    }
"@
[System.Net.ServicePointManager]::CertificatePolicy = New-Object TrustAllCertsPolicy
[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12

$baseUrl = "https://localhost:53812"
$supplierId = 260  # Ardo supplier ID

# Use a placeholder green logo for Ardo (simplified version)
# This is a simple green rectangle with "ARDO" text representation
$base64Logo = "data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMjAwIiBoZWlnaHQ9IjgwIiB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciPgogIDxyZWN0IHdpZHRoPSIyMDAiIGhlaWdodD0iODAiIGZpbGw9IiMzOTkxNDEiLz4KICA8dGV4dCB4PSI1MCUiIHk9IjUwJSIgZm9udC1mYW1pbHk9IkFyaWFsLCBzYW5zLXNlcmlmIiBmb250LXNpemU9IjQwIiBmb250LXdlaWdodD0iYm9sZCIgZmlsbD0id2hpdGUiIHRleHQtYW5jaG9yPSJtaWRkbGUiIGRvbWluYW50LWJhc2VsaW5lPSJtaWRkbGUiPkFSRE88L3RleHQ+Cjwvc3ZnPg=="

Write-Host "Uploading Ardo logo (SVG placeholder)..." -ForegroundColor Green

try {
    # Create request body with base64 logo
    $requestBody = @{
        logo = $base64Logo
    } | ConvertTo-Json
    
    # Upload the logo
    Write-Host "Sending logo to API..." -ForegroundColor Cyan
    $response = Invoke-RestMethod -Uri "$baseUrl/api/suppliers/$supplierId/logo" `
        -Method Post `
        -ContentType "application/json" `
        -Body $requestBody
    
    Write-Host "Response: $($response.message)" -ForegroundColor Green
    
    # Verify the upload
    Write-Host "`nVerifying logo upload..." -ForegroundColor Cyan
    $verifyResponse = Invoke-RestMethod -Uri "$baseUrl/api/suppliers/$supplierId" -Method Get
    
    if ($verifyResponse.details -and $verifyResponse.details.logo) {
        Write-Host "Ardo logo successfully uploaded!" -ForegroundColor Green
        
        if ($verifyResponse.details.logo.StartsWith("data:image")) {
            Write-Host "Logo is stored as base64 data URI - ready for display!" -ForegroundColor Green
        }
    } else {
        Write-Host "Logo not found after upload" -ForegroundColor Red
    }
    
} catch {
    Write-Host "Error uploading logo:" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
}

Write-Host "`nYou can now view the Ardo supplier profile at:" -ForegroundColor Cyan
Write-Host "http://localhost:53813/supplier-profile.html?id=$supplierId" -ForegroundColor Yellow
Write-Host "(Using HTTP to avoid certificate warning)" -ForegroundColor Gray