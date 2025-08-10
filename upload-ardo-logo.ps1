# Upload Ardo Logo Script

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

# Ardo logo URL (you provided the image)
$logoUrl = "https://www.ardo.com/sites/default/files/2021-04/ardo-logo.png"

Write-Host "Uploading Ardo logo to supplier profile..." -ForegroundColor Green

try {
    # Create request body with logo URL
    $requestBody = @{
        logo = $logoUrl
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
        Write-Host "Logo URL stored: $($verifyResponse.details.logo)" -ForegroundColor Yellow
    } else {
        Write-Host "Logo not found after upload" -ForegroundColor Red
    }
    
} catch {
    Write-Host "Error uploading logo:" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
}

Write-Host "`nYou can now view the Ardo supplier profile at:" -ForegroundColor Cyan
Write-Host "$baseUrl/supplier-profile.html?id=$supplierId" -ForegroundColor Yellow