# Full import script for Requests and Request Line Items
# This script imports all data from the CSV files into the database

$requestsCsv = "C:\Users\fdxadmin\Downloads\Requests 9_8_2025.csv"
$itemsCsv = "C:\Users\fdxadmin\Downloads\Request line items 10_8_2025.csv"

Write-Host "`nFDX Trading - Request Import Script" -ForegroundColor Cyan
Write-Host "====================================" -ForegroundColor Cyan
Write-Host ""

# Check if files exist
if (!(Test-Path $requestsCsv)) {
    Write-Host "ERROR: Requests file not found at: $requestsCsv" -ForegroundColor Red
    exit 1
}

if (!(Test-Path $itemsCsv)) {
    Write-Host "ERROR: Items file not found at: $itemsCsv" -ForegroundColor Red
    exit 1
}

Write-Host "Files found:" -ForegroundColor Green
Write-Host "  ✓ Requests CSV: $requestsCsv" -ForegroundColor Gray
Write-Host "  ✓ Items CSV: $itemsCsv" -ForegroundColor Gray
Write-Host ""

# Setup for API call
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

Write-Host "Starting import process..." -ForegroundColor Yellow
Write-Host ""

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
    $requestsContent = [System.IO.File]::ReadAllText($requestsCsv)
    $bodyLines += $requestsContent
    
    # Add items file
    $bodyLines += "--$boundary"
    $bodyLines += "Content-Disposition: form-data; name=`"itemsFile`"; filename=`"Items.csv`""
    $bodyLines += "Content-Type: text/csv"
    $bodyLines += ""
    $itemsContent = [System.IO.File]::ReadAllText($itemsCsv)
    $bodyLines += $itemsContent
    
    $bodyLines += "--$boundary--"
    $body = $bodyLines -join $LF
    
    # Calculate file sizes for display
    $requestsSize = (Get-Item $requestsCsv).Length / 1MB
    $itemsSize = (Get-Item $itemsCsv).Length / 1MB
    
    Write-Host "File sizes:" -ForegroundColor Cyan
    Write-Host ("  Requests: {0:N2} MB" -f $requestsSize) -ForegroundColor Gray
    Write-Host ("  Items: {0:N2} MB" -f $itemsSize) -ForegroundColor Gray
    Write-Host ""
    
    Write-Host "Sending import request to API..." -ForegroundColor Yellow
    Write-Host "  URL: $baseUrl/api/requests/import-csv" -ForegroundColor Gray
    Write-Host ""
    
    $stopwatch = [System.Diagnostics.Stopwatch]::StartNew()
    
    $response = Invoke-RestMethod -Uri "$baseUrl/api/requests/import-csv" `
        -Method Post `
        -ContentType "multipart/form-data; boundary=$boundary" `
        -Body $body `
        -TimeoutSec 300
    
    $stopwatch.Stop()
    $elapsed = $stopwatch.Elapsed.TotalSeconds
    
    Write-Host ("✅ Import completed in {0:N1} seconds!" -f $elapsed) -ForegroundColor Green
    Write-Host ""
    Write-Host "Import Results:" -ForegroundColor Cyan
    Write-Host "===============" -ForegroundColor Cyan
    Write-Host "  📋 Requests imported: $($response.importedCount)" -ForegroundColor Green
    Write-Host "  📦 Total items imported: $($response.totalItems)" -ForegroundColor Green
    
    if ($response.importedCount -gt 0) {
        $avgItemsPerRequest = [Math]::Round($response.totalItems / $response.importedCount, 1)
        Write-Host "  📊 Average items per request: $avgItemsPerRequest" -ForegroundColor Gray
    }
    
    Write-Host ""
    Write-Host "Message: $($response.message)" -ForegroundColor Yellow
    
    # Show sample of imported requests
    if ($response.importedRequests -and $response.importedRequests.Count -gt 0) {
        Write-Host ""
        Write-Host "Sample of imported requests (first 10):" -ForegroundColor Cyan
        $count = 0
        foreach ($req in $response.importedRequests) {
            if ($count -ge 10) { break }
            $title = $req.title
            if ($title.Length -gt 50) {
                $title = $title.Substring(0, 47) + "..."
            }
            $reqNum = $req.requestNumber
            $itemCnt = $req.itemCount
            Write-Host "  - $reqNum`: $title `($itemCnt items`)" -ForegroundColor Gray
            $count++
        }
        
        if ($response.importedRequests.Count -gt 10) {
            $remaining = $response.importedRequests.Count - 10
            Write-Host "  `... and $remaining more requests" -ForegroundColor DarkGray
        }
    }
    
    # Show any warnings/errors
    if ($response.errors -and $response.errors.Count -gt 0) {
        Write-Host ""
        Write-Host "⚠️ Warnings/Errors encountered:" -ForegroundColor Yellow
        $errorCount = 0
        foreach ($error in $response.errors) {
            if ($errorCount -ge 10) {
                    $remainingErrors = $response.errors.Count - 10
                Write-Host "  `... and $remainingErrors more warnings" -ForegroundColor DarkYellow
                break
            }
            Write-Host "  - $error" -ForegroundColor Yellow
            $errorCount++
        }
    }
    
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Green
    Write-Host "✅ Import process completed successfully!" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "📌 View imported requests at:" -ForegroundColor Cyan
    Write-Host "   http://localhost:53813/requests.html" -ForegroundColor White
    Write-Host ""
    
} catch {
    Write-Host ""
    Write-Host "❌ Import failed!" -ForegroundColor Red
    Write-Host "=================" -ForegroundColor Red
    Write-Host ""
    Write-Host "Error: $_" -ForegroundColor Red
    
    if ($_.Exception.Response) {
        try {
            $reader = [System.IO.StreamReader]::new($_.Exception.Response.GetResponseStream())
            $errorContent = $reader.ReadToEnd()
            Write-Host ""
            Write-Host "Server Response:" -ForegroundColor Yellow
            Write-Host $errorContent -ForegroundColor Red
        } catch {
            Write-Host "Could not read error response" -ForegroundColor Yellow
        }
    }
    
    Write-Host ""
    Write-Host "Troubleshooting tips:" -ForegroundColor Yellow
    Write-Host "  1. Make sure the API is running (check if https://localhost:53812 is accessible)" -ForegroundColor Gray
    Write-Host "  2. Verify the CSV files exist at the specified paths" -ForegroundColor Gray
    Write-Host "  3. Check if there are any data validation issues in the CSV files" -ForegroundColor Gray
    Write-Host "  4. Review the API logs for more detailed error information" -ForegroundColor Gray
    
    exit 1
}

Write-Host "Press any key to exit..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")