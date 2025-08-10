# Script to update all request titles to use product sourcing names (max 5 words)

Write-Host "Updating Request Titles to Product Sourcing Names" -ForegroundColor Cyan
Write-Host "==================================================" -ForegroundColor Cyan
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

Write-Host "Fetching all requests..." -ForegroundColor Yellow

try {
    # Get all requests
    $requests = Invoke-RestMethod -Uri "$baseUrl/api/requests" -Method Get
    
    Write-Host "Found $($requests.Count) requests to update" -ForegroundColor Green
    Write-Host ""
    
    $updatedCount = 0
    $failedCount = 0
    
    foreach ($request in $requests) {
        # Get full request details with items
        $fullRequest = Invoke-RestMethod -Uri "$baseUrl/api/requests/$($request.id)" -Method Get
        
        # Generate new title based on items
        $newTitle = ""
        
        if ($fullRequest.items -and $fullRequest.items.Count -gt 0) {
            # Get product names from items
            $productNames = @()
            foreach ($item in $fullRequest.items) {
                if ($item.productName) {
                    # Extract key words from product name
                    $words = $item.productName -split '\s+|,|-|/'
                    $cleanWords = $words | Where-Object { $_.Length -gt 2 -and $_ -notmatch '^\d+$' }
                    if ($cleanWords.Count -gt 0) {
                        $productNames += $cleanWords[0]
                    }
                }
            }
            
            # Create title from product names
            if ($productNames.Count -eq 1) {
                # Single product - use first few words
                $words = $fullRequest.items[0].productName -split '\s+'
                $titleWords = $words[0..4] # Take first 5 words
                $newTitle = ($titleWords -join ' ').Trim()
            }
            elseif ($productNames.Count -gt 1) {
                # Multiple products - combine names
                $uniqueProducts = $productNames | Select-Object -Unique -First 3
                $newTitle = ($uniqueProducts -join ', ') + " sourcing"
            }
            
            # Ensure title is not too long (max 5 words for main part)
            $titleWords = $newTitle -split '\s+'
            if ($titleWords.Count -gt 5) {
                $newTitle = ($titleWords[0..4] -join ' ')
            }
            
            # Clean up title
            $newTitle = $newTitle -replace '\s+', ' '
            $newTitle = $newTitle.Trim(',', ' ', '-')
            
        }
        
        # If no items or couldn't generate title, create a generic one
        if ([string]::IsNullOrWhiteSpace($newTitle)) {
            $newTitle = "Product sourcing request"
        }
        
        # Ensure title is not empty and not too long
        if ($newTitle.Length -gt 200) {
            $newTitle = $newTitle.Substring(0, 197) + "..."
        }
        
        # Only update if title is different
        if ($request.title -ne $newTitle) {
            Write-Host "  Updating: $($request.requestNumber)" -ForegroundColor Gray
            Write-Host "    Old: $($request.title)" -ForegroundColor DarkGray
            Write-Host "    New: $newTitle" -ForegroundColor Green
            
            # Update the request
            $updateData = @{
                title = $newTitle
                description = $fullRequest.description
                buyerCompany = $fullRequest.buyerCompany
                items = $fullRequest.items | ForEach-Object {
                    @{
                        productName = $_.productName
                        quantity = $_.quantity
                        unit = $_.unit
                        description = $_.description
                        targetPrice = $_.targetPrice
                    }
                }
            }
            
            $json = $updateData | ConvertTo-Json -Depth 10
            
            try {
                $response = Invoke-RestMethod -Uri "$baseUrl/api/requests/$($request.id)" `
                    -Method Put `
                    -ContentType "application/json" `
                    -Body $json
                
                $updatedCount++
            }
            catch {
                Write-Host "    Failed to update: $_" -ForegroundColor Red
                $failedCount++
            }
        }
        else {
            Write-Host "  Skipping: $($request.requestNumber) - title already good" -ForegroundColor DarkGray
        }
    }
    
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Green
    Write-Host "Update Complete!" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "Results:" -ForegroundColor Yellow
    Write-Host "  Updated: $updatedCount requests" -ForegroundColor Green
    Write-Host "  Failed: $failedCount requests" -ForegroundColor Red
    Write-Host "  Unchanged: $($requests.Count - $updatedCount - $failedCount) requests" -ForegroundColor Gray
    
} catch {
    Write-Host ""
    Write-Host "Error: $_" -ForegroundColor Red
}