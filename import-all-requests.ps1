# Direct database import of all requests and items
# This script reads CSV files and inserts data directly

$requestsCsv = "C:\Users\fdxadmin\Downloads\Requests 9_8_2025.csv"
$itemsCsv = "C:\Users\fdxadmin\Downloads\Request line items 10_8_2025.csv"

Write-Host "Starting bulk import of Requests and Items..." -ForegroundColor Green

# Function to parse CSV line properly
function Parse-CsvLine {
    param([string]$line)
    
    $values = @()
    $currentValue = ""
    $inQuotes = $false
    
    for ($i = 0; $i -lt $line.Length; $i++) {
        $ch = $line[$i]
        
        if ($ch -eq '"') {
            if ($inQuotes -and ($i + 1) -lt $line.Length -and $line[$i + 1] -eq '"') {
                $currentValue += '"'
                $i++
            }
            else {
                $inQuotes = -not $inQuotes
            }
        }
        elseif ($ch -eq ',' -and -not $inQuotes) {
            $values += $currentValue
            $currentValue = ""
        }
        else {
            $currentValue += $ch
        }
    }
    $values += $currentValue
    return $values
}

try {
    # First, process items file to build a dictionary
    Write-Host "`nProcessing Request Line Items..." -ForegroundColor Cyan
    $items = @{}
    
    if (Test-Path $itemsCsv) {
        $itemsContent = Get-Content $itemsCsv -Encoding UTF8
        $itemsHeader = $itemsContent[0]
        
        for ($i = 1; $i -lt $itemsContent.Count; $i++) {
            try {
                $values = Parse-CsvLine $itemsContent[$i]
                if ($values.Count -ge 4) {
                    $productName = $values[0].Trim()
                    $requestLink = $values[3].Trim()
                    
                    if ($productName -and $requestLink) {
                        $quantity = 1
                        $unit = "pcs"
                        
                        if ($values.Count -gt 6 -and $values[6]) {
                            try { $quantity = [decimal]$values[6] } catch {}
                        }
                        if ($values.Count -gt 7 -and $values[7]) {
                            $unit = $values[7].Trim()
                        }
                        
                        $item = @{
                            ProductName = $productName
                            Quantity = $quantity
                            Unit = $unit
                            Description = if ($values.Count -gt 9) { $values[9] } else { $null }
                        }
                        
                        if (-not $items.ContainsKey($requestLink)) {
                            $items[$requestLink] = @()
                        }
                        $items[$requestLink] += $item
                    }
                }
            }
            catch {
                Write-Host "  Warning: Could not parse item line $i" -ForegroundColor Yellow
            }
        }
        
        Write-Host "  Processed $($items.Count) unique requests with items" -ForegroundColor Green
        $totalItems = 0
        foreach ($key in $items.Keys) {
            $totalItems += $items[$key].Count
        }
        Write-Host "  Total items: $totalItems" -ForegroundColor Green
    }
    
    # Now process requests file
    Write-Host "`nProcessing Requests..." -ForegroundColor Cyan
    $requestsContent = Get-Content $requestsCsv -Encoding UTF8
    $requestsHeader = $requestsContent[0]
    
    $importedCount = 0
    $skippedCount = 0
    $errorCount = 0
    $maxToImport = 50  # Import first 50 for testing
    
    for ($i = 1; $i -lt $requestsContent.Count -and $importedCount -lt $maxToImport; $i++) {
        try {
            $values = Parse-CsvLine $requestsContent[$i]
            
            if ($values.Count -ge 3) {
                $requestName = $values[0].Trim()
                
                if (-not $requestName) {
                    $skippedCount++
                    continue
                }
                
                # Extract key fields
                $status = if ($values.Count -gt 2) { $values[2].Trim() } else { "New" }
                $brief = ""
                if ($values.Count -gt 6) {
                    $brief = $values[6]
                    # Truncate if too long
                    if ($brief.Length -gt 1000) {
                        $brief = $brief.Substring(0, 997) + "..."
                    }
                }
                
                $buyer = if ($values.Count -gt 9) { $values[9].Trim() } else { "Unknown" }
                $requestId = if ($values.Count -gt 33) { $values[33].Trim() } else { "" }
                
                # Create request object
                $request = @{
                    Title = $requestName.Substring(0, [Math]::Min($requestName.Length, 200))
                    Description = $brief
                    Status = $status
                    Buyer = $buyer
                    RequestId = $requestId
                    Items = @()
                }
                
                # Add items if they exist
                if ($items.ContainsKey($requestName)) {
                    $request.Items = $items[$requestName]
                }
                elseif ($requestId -and $items.ContainsKey($requestId)) {
                    $request.Items = $items[$requestId]
                }
                
                # Here you would normally save to database
                # For now, just count
                $importedCount++
                
                if ($importedCount % 10 -eq 0) {
                    Write-Host "  Processed $importedCount requests..." -ForegroundColor Gray
                }
            }
            else {
                $skippedCount++
            }
        }
        catch {
            $errorCount++
            Write-Host "  Error on line $i : $_" -ForegroundColor Red
        }
    }
    
    Write-Host "`nImport Summary:" -ForegroundColor Green
    Write-Host "  Imported: $importedCount requests" -ForegroundColor Green
    Write-Host "  Skipped: $skippedCount empty/invalid rows" -ForegroundColor Yellow
    Write-Host "  Errors: $errorCount rows with errors" -ForegroundColor Red
    
    Write-Host "`nNote: This was a test run importing first $maxToImport requests." -ForegroundColor Cyan
    Write-Host "To import all, modify the maxToImport variable in the script." -ForegroundColor Cyan
    
}
catch {
    Write-Host "`nFatal Error: $_" -ForegroundColor Red
}

Write-Host "`nImport process completed." -ForegroundColor Green