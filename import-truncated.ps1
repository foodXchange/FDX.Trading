# Import truncated CSV files

$requestsCsv = "C:\FDX.Trading\Requests_truncated.csv"
$itemsCsv = "C:\FDX.Trading\Items_truncated.csv"

Write-Host "Importing Truncated CSV Files" -ForegroundColor Cyan
Write-Host "==============================" -ForegroundColor Cyan
Write-Host ""

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
    Write-Host "IMPORT SUCCESSFUL!" -ForegroundColor Green
    Write-Host "==================" -ForegroundColor Green
    Write-Host ""
    Write-Host "Requests imported: $($response.importedCount)" -ForegroundColor Green
    Write-Host "Total items: $($response.totalItems)" -ForegroundColor Green
    Write-Host ""
    Write-Host "View at: http://localhost:53813/requests.html" -ForegroundColor Cyan
    
} catch {
    Write-Host ""
    Write-Host "Import failed!" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
}