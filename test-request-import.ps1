# Test Request CSV Import

# Ignore SSL certificate errors
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
$requestsFile = "C:\Users\fdxadmin\Downloads\Requests 9_8_2025.csv"
$itemsFile = "C:\Users\fdxadmin\Downloads\Request line items 10_8_2025.csv"

Write-Host "Testing Request CSV Import..." -ForegroundColor Green

# Check if files exist
if (!(Test-Path $requestsFile)) {
    Write-Host "Requests file not found: $requestsFile" -ForegroundColor Red
    exit
}

if (!(Test-Path $itemsFile)) {
    Write-Host "Items file not found: $itemsFile" -ForegroundColor Yellow
    Write-Host "Continuing with requests file only..." -ForegroundColor Yellow
}

try {
    # Create multipart form data
    $boundary = [System.Guid]::NewGuid().ToString()
    $LF = "`r`n"
    
    # Build the form data
    $bodyLines = @()
    
    # Add requests file
    $bodyLines += "--$boundary"
    $bodyLines += "Content-Disposition: form-data; name=`"requestsFile`"; filename=`"Requests.csv`""
    $bodyLines += "Content-Type: text/csv"
    $bodyLines += ""
    $bodyLines += [System.IO.File]::ReadAllText($requestsFile)
    
    # Add items file if it exists
    if (Test-Path $itemsFile) {
        $bodyLines += "--$boundary"
        $bodyLines += "Content-Disposition: form-data; name=`"itemsFile`"; filename=`"Items.csv`""
        $bodyLines += "Content-Type: text/csv"
        $bodyLines += ""
        $bodyLines += [System.IO.File]::ReadAllText($itemsFile)
    }
    
    $bodyLines += "--$boundary--"
    $body = $bodyLines -join $LF
    
    Write-Host "Sending import request..." -ForegroundColor Cyan
    
    $response = Invoke-RestMethod -Uri "$baseUrl/api/requests/import-csv" `
        -Method Post `
        -ContentType "multipart/form-data; boundary=$boundary" `
        -Body $body
    
    Write-Host "`nImport successful!" -ForegroundColor Green
    Write-Host "Results:" -ForegroundColor Yellow
    Write-Host "  - Imported Requests: $($response.importedCount)" -ForegroundColor Gray
    Write-Host "  - Total Items: $($response.totalItems)" -ForegroundColor Gray
    Write-Host "  - Message: $($response.message)" -ForegroundColor Gray
    
    if ($response.importedRequests) {
        Write-Host "`nImported Requests:" -ForegroundColor Cyan
        foreach ($req in $response.importedRequests) {
            Write-Host "  - $($req.requestNumber): $($req.title) ($($req.itemCount) items) - Status: $($req.status)" -ForegroundColor Gray
        }
    }
    
    if ($response.errors -and $response.errors.Count -gt 0) {
        Write-Host "`nWarnings/Errors:" -ForegroundColor Yellow
        foreach ($error in $response.errors) {
            Write-Host "  - $error" -ForegroundColor Yellow
        }
    }
    
} catch {
    Write-Host "`nError:" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
    
    if ($_.Exception.Response) {
        $reader = [System.IO.StreamReader]::new($_.Exception.Response.GetResponseStream())
        $errorContent = $reader.ReadToEnd()
        Write-Host "Response: $errorContent" -ForegroundColor Red
    }
}

Write-Host "`nCheck imported requests at: http://localhost:53813/requests.html" -ForegroundColor Yellow