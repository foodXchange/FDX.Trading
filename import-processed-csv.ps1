# Import processed CSV files

$requestsCsv = "C:\FDX.Trading\Requests_processed.csv"
$itemsCsv = "C:\FDX.Trading\Items_processed.csv"

Write-Host "FDX Trading - Import Processed CSV Files" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host ""

# Check files
if (!(Test-Path $requestsCsv)) {
    Write-Host "ERROR: Processed requests file not found" -ForegroundColor Red
    exit 1
}
if (!(Test-Path $itemsCsv)) {
    Write-Host "ERROR: Processed items file not found" -ForegroundColor Red
    exit 1
}

Write-Host "Files found:" -ForegroundColor Green
Write-Host "  Requests: $requestsCsv" -ForegroundColor Gray
Write-Host "  Items: $itemsCsv" -ForegroundColor Gray
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

Write-Host "Sending import request to API..." -ForegroundColor Yellow
Write-Host ""

$stopwatch = [System.Diagnostics.Stopwatch]::StartNew()

try {
    $response = Invoke-RestMethod -Uri "$baseUrl/api/requests/import-csv" `
        -Method Post `
        -ContentType "multipart/form-data; boundary=$boundary" `
        -Body $body `
        -TimeoutSec 300
    
    $stopwatch.Stop()
    $elapsed = $stopwatch.Elapsed.TotalSeconds
    
    Write-Host "========================================" -ForegroundColor Green
    Write-Host "       IMPORT SUCCESSFUL!" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "Time taken: $([Math]::Round($elapsed, 1)) seconds" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Results:" -ForegroundColor Yellow
    Write-Host "  Requests imported: $($response.importedCount)" -ForegroundColor Green
    Write-Host "  Total items: $($response.totalItems)" -ForegroundColor Green
    
    if ($response.importedCount -gt 0) {
        $avgItems = [Math]::Round($response.totalItems / $response.importedCount, 1)
        Write-Host "  Average items per request: $avgItems" -ForegroundColor Gray
    }
    
    Write-Host ""
    Write-Host "Message: $($response.message)" -ForegroundColor Cyan
    
    if ($response.errors -and $response.errors.Count -gt 0) {
        Write-Host ""
        Write-Host "Warnings encountered:" -ForegroundColor Yellow
        foreach ($error in $response.errors) {
            Write-Host "  - $error" -ForegroundColor Yellow
        }
    }
    
    Write-Host ""
    Write-Host "View imported requests at:" -ForegroundColor Cyan
    Write-Host "  http://localhost:53813/requests.html" -ForegroundColor White
    Write-Host ""
    
} catch {
    $stopwatch.Stop()
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Red
    Write-Host "         IMPORT FAILED!" -ForegroundColor Red
    Write-Host "========================================" -ForegroundColor Red
    Write-Host ""
    Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Red
    
    if ($_.Exception.Response) {
        try {
            $reader = [System.IO.StreamReader]::new($_.Exception.Response.GetResponseStream())
            $errorContent = $reader.ReadToEnd()
            Write-Host ""
            Write-Host "Server Response:" -ForegroundColor Yellow
            Write-Host $errorContent -ForegroundColor Red
        } catch {}
    }
}