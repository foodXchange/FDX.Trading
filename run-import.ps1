# Simple import script for Requests and Request Line Items

$requestsCsv = "C:\Users\fdxadmin\Downloads\Requests 9_8_2025.csv"
$itemsCsv = "C:\Users\fdxadmin\Downloads\Request line items 10_8_2025.csv"

Write-Host "FDX Trading - Request Import Script" -ForegroundColor Cyan
Write-Host ""

# Check files
if (!(Test-Path $requestsCsv)) {
    Write-Host "ERROR: Requests file not found" -ForegroundColor Red
    exit 1
}
if (!(Test-Path $itemsCsv)) {
    Write-Host "ERROR: Items file not found" -ForegroundColor Red
    exit 1
}

Write-Host "Files found - starting import..." -ForegroundColor Green

# Setup SSL
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

# Create form data
$boundary = [System.Guid]::NewGuid().ToString()
$LF = "`r`n"

$bodyLines = @()
$bodyLines += "--$boundary"
$bodyLines += "Content-Disposition: form-data; name=`"requestsFile`"; filename=`"Requests.csv`""
$bodyLines += "Content-Type: text/csv"
$bodyLines += ""
$bodyLines += [System.IO.File]::ReadAllText($requestsCsv)

$bodyLines += "--$boundary"
$bodyLines += "Content-Disposition: form-data; name=`"itemsFile`"; filename=`"Items.csv`""
$bodyLines += "Content-Type: text/csv"
$bodyLines += ""
$bodyLines += [System.IO.File]::ReadAllText($itemsCsv)

$bodyLines += "--$boundary--"
$body = $bodyLines -join $LF

Write-Host "Sending import request..." -ForegroundColor Yellow

try {
    $response = Invoke-RestMethod -Uri "$baseUrl/api/requests/import-csv" `
        -Method Post `
        -ContentType "multipart/form-data; boundary=$boundary" `
        -Body $body `
        -TimeoutSec 300
    
    Write-Host ""
    Write-Host "Import Successful!" -ForegroundColor Green
    Write-Host "Requests imported: $($response.importedCount)" -ForegroundColor Green
    Write-Host "Total items: $($response.totalItems)" -ForegroundColor Green
    Write-Host ""
    Write-Host "View at: http://localhost:53813/requests.html" -ForegroundColor Cyan
    
} catch {
    Write-Host ""
    Write-Host "Import failed!" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
}