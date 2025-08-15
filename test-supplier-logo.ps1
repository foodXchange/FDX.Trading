# Test Supplier Logo Upload API

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

# Test image in base64 format (a simple 1x1 pixel red image)
$testImageBase64 = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8DwHwAFBQIAX8jx0gAAAABJRU5ErkJggg=="

# Use an existing supplier ID (Ardo - Belgium supplier)
$supplierId = 260

# Create the request body
$requestBody = @{
    logo = $testImageBase64
} | ConvertTo-Json

Write-Host "Testing Supplier Logo Upload API..." -ForegroundColor Green
Write-Host "Supplier ID: $supplierId" -ForegroundColor Yellow

try {
    # First, let's get the supplier details to see current state
    Write-Host "`nFetching current supplier details..." -ForegroundColor Cyan
    $getResponse = Invoke-RestMethod -Uri "$baseUrl/api/suppliers/$supplierId" -Method Get
    
    if ($getResponse.details -and $getResponse.details.logo) {
        Write-Host "Current logo exists: Yes (length: $($getResponse.details.logo.Length) chars)" -ForegroundColor Yellow
    } else {
        Write-Host "Current logo exists: No" -ForegroundColor Yellow
    }
    
    # Upload the new logo
    Write-Host "`nUploading new logo..." -ForegroundColor Cyan
    $uploadResponse = Invoke-RestMethod -Uri "$baseUrl/api/suppliers/$supplierId/logo" `
        -Method Post `
        -ContentType "application/json" `
        -Body $requestBody
    
    Write-Host "Upload Response: $($uploadResponse.message)" -ForegroundColor Green
    
    # Verify the upload by fetching supplier details again
    Write-Host "`nVerifying logo upload..." -ForegroundColor Cyan
    $verifyResponse = Invoke-RestMethod -Uri "$baseUrl/api/suppliers/$supplierId" -Method Get
    
    if ($verifyResponse.details -and $verifyResponse.details.logo) {
        Write-Host "Logo successfully uploaded!" -ForegroundColor Green
        Write-Host "Logo data length: $($verifyResponse.details.logo.Length) chars" -ForegroundColor Yellow
        
        # Check if it matches what we uploaded
        if ($verifyResponse.details.logo -eq $testImageBase64) {
            Write-Host "Logo data matches uploaded image" -ForegroundColor Green
        } else {
            Write-Host "Logo data does not match exactly (might be processed)" -ForegroundColor Yellow
        }
    } else {
        Write-Host "Logo not found after upload" -ForegroundColor Red
    }
    
    Write-Host "`nLogo upload test completed successfully!" -ForegroundColor Green
    
} catch {
    Write-Host "`nError during logo upload test:" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
    
    if ($_.Exception.Response) {
        $reader = [System.IO.StreamReader]::new($_.Exception.Response.GetResponseStream())
        $errorContent = $reader.ReadToEnd()
        Write-Host "Response content: $errorContent" -ForegroundColor Red
    }
}

Write-Host "`nTest completed." -ForegroundColor Cyan