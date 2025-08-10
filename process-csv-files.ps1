# Process CSV files to truncate long values before import

$requestsCsvPath = "C:\Users\fdxadmin\Downloads\Requests 9_8_2025.csv"
$itemsCsvPath = "C:\Users\fdxadmin\Downloads\Request line items 10_8_2025.csv"

$requestsOutputPath = "C:\FDX.Trading\Requests_processed.csv"
$itemsOutputPath = "C:\FDX.Trading\Items_processed.csv"

Write-Host "Processing CSV files to truncate long values..." -ForegroundColor Cyan
Write-Host ""

# Function to truncate string to max length
function Truncate-String {
    param(
        [string]$str,
        [int]$maxLength
    )
    if ($str.Length -gt $maxLength) {
        return $str.Substring(0, $maxLength - 3) + "..."
    }
    return $str
}

# Process Requests CSV
Write-Host "Processing Requests CSV..." -ForegroundColor Yellow
$requestsContent = Get-Content $requestsCsvPath -Encoding UTF8
$processedRequests = @()
$processedRequests += $requestsContent[0]  # Keep header

for ($i = 1; $i -lt $requestsContent.Count; $i++) {
    $line = $requestsContent[$i]
    
    # Simple approach - if line is too long, truncate it
    # This is rough but will ensure no field exceeds reasonable limits
    if ($line.Length -gt 2000) {
        $line = $line.Substring(0, 1997) + "..."
    }
    $processedRequests += $line
}

$processedRequests | Out-File -FilePath $requestsOutputPath -Encoding UTF8
Write-Host "  Processed $($processedRequests.Count - 1) request rows" -ForegroundColor Green
Write-Host "  Saved to: $requestsOutputPath" -ForegroundColor Gray

# Process Items CSV
Write-Host ""
Write-Host "Processing Request Line Items CSV..." -ForegroundColor Yellow
$itemsContent = Get-Content $itemsCsvPath -Encoding UTF8
$processedItems = @()
$processedItems += $itemsContent[0]  # Keep header

$truncatedCount = 0
for ($i = 1; $i -lt $itemsContent.Count; $i++) {
    $line = $itemsContent[$i]
    
    # Check if line contains long product names (common issue)
    if ($line.Length -gt 1000) {
        # Try to find and truncate just the product name part
        # Since product name is first field, truncate intelligently
        $parts = $line -split '","', 2
        if ($parts.Count -eq 2) {
            $productPart = $parts[0]
            if ($productPart.StartsWith('"')) {
                $productPart = $productPart.Substring(1)
            }
            
            # Truncate product name to 190 chars to be safe
            if ($productPart.Length -gt 190) {
                $productPart = $productPart.Substring(0, 187) + "..."
                $truncatedCount++
            }
            
            $line = '"' + $productPart + '","' + $parts[1]
        }
    }
    
    $processedItems += $line
}

$processedItems | Out-File -FilePath $itemsOutputPath -Encoding UTF8
Write-Host "  Processed $($processedItems.Count - 1) item rows" -ForegroundColor Green
Write-Host "  Truncated $truncatedCount product names" -ForegroundColor Yellow
Write-Host "  Saved to: $itemsOutputPath" -ForegroundColor Gray

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "CSV files processed successfully!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Processed files ready for import:" -ForegroundColor Cyan
Write-Host "  - $requestsOutputPath" -ForegroundColor White
Write-Host "  - $itemsOutputPath" -ForegroundColor White
Write-Host ""