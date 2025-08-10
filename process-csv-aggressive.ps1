# Process CSV files with aggressive truncation for database import

Write-Host "Processing CSV files with aggressive truncation..." -ForegroundColor Cyan
Write-Host ""

# Process Items CSV with aggressive truncation
$itemsCsvPath = "C:\Users\fdxadmin\Downloads\Request line items 10_8_2025.csv"
$itemsOutputPath = "C:\FDX.Trading\Items_truncated.csv"

Write-Host "Processing Request Line Items CSV..." -ForegroundColor Yellow

$content = Get-Content $itemsCsvPath -Raw -Encoding UTF8
$lines = $content -split "`r?`n"

$output = @()
$output += $lines[0]  # Header

$truncatedCount = 0
for ($i = 1; $i -lt $lines.Count; $i++) {
    if ([string]::IsNullOrWhiteSpace($lines[$i])) { continue }
    
    $line = $lines[$i]
    
    # Parse CSV line to get the product name field
    $inQuotes = $false
    $fieldStart = 0
    $fieldCount = 0
    $newLine = ""
    
    for ($j = 0; $j -lt $line.Length; $j++) {
        $char = $line[$j]
        
        if ($char -eq '"' -and ($j -eq 0 -or $line[$j-1] -eq ',')) {
            $inQuotes = $true
        }
        elseif ($char -eq '"' -and $inQuotes -and (($j+1) -eq $line.Length -or $line[$j+1] -eq ',')) {
            $inQuotes = $false
        }
        
        if ($char -eq ',' -and -not $inQuotes) {
            # End of field
            $field = $line.Substring($fieldStart, $j - $fieldStart)
            
            # If this is the first field (product name), truncate it
            if ($fieldCount -eq 0) {
                $cleanField = $field.Trim('"')
                if ($cleanField.Length -gt 190) {
                    $cleanField = $cleanField.Substring(0, 187) + "..."
                    $truncatedCount++
                }
                $field = '"' + $cleanField + '"'
            }
            
            $newLine += $field + ","
            $fieldStart = $j + 1
            $fieldCount++
        }
    }
    
    # Handle last field
    if ($fieldStart -lt $line.Length) {
        $field = $line.Substring($fieldStart)
        $newLine += $field
    }
    
    $output += $newLine
}

$output | Out-File -FilePath $itemsOutputPath -Encoding UTF8
Write-Host "  Processed $($output.Count - 1) item rows" -ForegroundColor Green
Write-Host "  Truncated $truncatedCount product names" -ForegroundColor Yellow
Write-Host "  Saved to: $itemsOutputPath" -ForegroundColor Gray

# Process Requests CSV
$requestsCsvPath = "C:\Users\fdxadmin\Downloads\Requests 9_8_2025.csv"
$requestsOutputPath = "C:\FDX.Trading\Requests_truncated.csv"

Write-Host ""
Write-Host "Processing Requests CSV..." -ForegroundColor Yellow

# For requests, just ensure no single line is too long
$requestsContent = Get-Content $requestsCsvPath -Encoding UTF8
$processedRequests = @()

foreach ($line in $requestsContent) {
    if ($line.Length -gt 4000) {
        $line = $line.Substring(0, 3997) + "..."
    }
    $processedRequests += $line
}

$processedRequests | Out-File -FilePath $requestsOutputPath -Encoding UTF8
Write-Host "  Processed $($processedRequests.Count - 1) request rows" -ForegroundColor Green
Write-Host "  Saved to: $requestsOutputPath" -ForegroundColor Gray

Write-Host ""
Write-Host "Files ready for import!" -ForegroundColor Green
Write-Host "  - $requestsOutputPath" -ForegroundColor White
Write-Host "  - $itemsOutputPath" -ForegroundColor White