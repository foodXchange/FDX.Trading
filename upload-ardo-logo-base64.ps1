# Upload Ardo Logo as Base64

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

Write-Host "Downloading and converting Ardo logo to base64..." -ForegroundColor Green

try {
    # Download the Ardo logo
    $webClient = New-Object System.Net.WebClient
    $imageBytes = $webClient.DownloadData("https://www.ardo.com/sites/default/files/2021-04/ardo-logo.png")
    
    # Convert to base64
    $base64String = [Convert]::ToBase64String($imageBytes)
    $dataUri = "data:image/png;base64,$base64String"
    
    Write-Host "Logo downloaded and converted (size: $($base64String.Length) chars)" -ForegroundColor Cyan
    
    # Create request body with base64 logo
    $requestBody = @{
        logo = $dataUri
    } | ConvertTo-Json
    
    # Upload the logo
    Write-Host "`nUploading base64 logo to API..." -ForegroundColor Cyan
    $response = Invoke-RestMethod -Uri "$baseUrl/api/suppliers/$supplierId/logo" `
        -Method Post `
        -ContentType "application/json" `
        -Body $requestBody
    
    Write-Host "Response: $($response.message)" -ForegroundColor Green
    
    # Verify the upload
    Write-Host "`nVerifying logo upload..." -ForegroundColor Cyan
    $verifyResponse = Invoke-RestMethod -Uri "$baseUrl/api/suppliers/$supplierId" -Method Get
    
    if ($verifyResponse.details -and $verifyResponse.details.logo) {
        $logoLength = $verifyResponse.details.logo.Length
        Write-Host "Ardo logo successfully uploaded as base64!" -ForegroundColor Green
        Write-Host "Logo data size: $logoLength characters" -ForegroundColor Yellow
        
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