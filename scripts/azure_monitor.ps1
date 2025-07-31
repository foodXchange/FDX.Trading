# Azure Resource Monitoring Script for FoodXchange
# Run this script regularly to monitor your Azure resources

Write-Host "=== Azure FoodXchange Resource Monitor ===" -ForegroundColor Cyan
Write-Host ""

# 1. Check Resource Health
Write-Host "1. Checking Resource Health..." -ForegroundColor Yellow
az resource list --resource-group foodxchange-rg --query "[].{Name:name, Type:type, Status:provisioningState}" --output table

Write-Host "`n2. OpenAI Service Status..." -ForegroundColor Yellow
az cognitiveservices account show --name "foodxchangeopenai" --resource-group "foodxchange-rg" --query "{Name:name, Status:provisioningState, Endpoint:properties.endpoint, SKU:sku.name}" --output table

# 2. Check Current Usage (OpenAI)
Write-Host "`n3. OpenAI Usage Metrics (Last 24h)..." -ForegroundColor Yellow
$endTime = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")
$startTime = (Get-Date).AddDays(-1).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")

az monitor metrics list `
    --resource /subscriptions/88931ed0-52df-42fb-a09c-e024c9586f8a/resourceGroups/foodxchange-rg/providers/Microsoft.CognitiveServices/accounts/foodxchangeopenai `
    --metric-names "ProcessedPromptTokens" "GeneratedCompletionTokens" `
    --start-time $startTime `
    --end-time $endTime `
    --interval PT1H `
    --query "value[].{Metric:name.value, Total:timeseries[0].data[].total}" `
    --output json 2>$null || Write-Host "Metrics may not be available yet" -ForegroundColor Gray

# 3. Cost Analysis
Write-Host "`n4. Estimated Costs (Current Month)..." -ForegroundColor Yellow
$month = (Get-Date).ToString("yyyy-MM")
az costmanagement query `
    --type Usage `
    --scope "/subscriptions/88931ed0-52df-42fb-a09c-e024c9586f8a" `
    --dataset-filter "{`"and`":[{`"dimensions`":{`"name`":`"ResourceGroup`",`"operator`":`"In`",`"values`":[`"foodxchange-rg`",`"foodxchange-ai-rg`"]}}]}" `
    --timeframe MonthToDate `
    --query "rows[*].[0,1,2]" `
    --output table 2>$null || Write-Host "Cost data typically appears after 24-48 hours" -ForegroundColor Gray

# 4. Check Quotas
Write-Host "`n5. Service Quotas..." -ForegroundColor Yellow
Write-Host "OpenAI GPT-35-Turbo: 240K tokens/min (Free tier)" -ForegroundColor Green
Write-Host "Document Intelligence: 500 pages/month (Free tier)" -ForegroundColor Green
Write-Host "Computer Vision: 5,000 transactions/month (Free tier)" -ForegroundColor Green
Write-Host "Translator: 2M characters/month (Free tier)" -ForegroundColor Green

# 5. Alerts Status
Write-Host "`n6. Active Alerts..." -ForegroundColor Yellow
az monitor alert list --resource-group foodxchange-rg --output table 2>$null || Write-Host "No alerts configured" -ForegroundColor Gray

Write-Host "`n=== Monitoring Complete ===" -ForegroundColor Cyan
Write-Host "For detailed monitoring, visit: https://portal.azure.com" -ForegroundColor Blue
Write-Host ""