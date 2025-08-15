# Script to check the updated request titles

Add-Type @"
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

try {
    $response = Invoke-RestMethod -Uri 'https://localhost:53812/api/requests' -Method Get -ErrorAction Stop
    
    Write-Host 'Sample of Updated Request Titles:' -ForegroundColor Cyan
    Write-Host '=================================' -ForegroundColor Cyan
    Write-Host ''
    
    $sample = $response | Select-Object -First 20
    foreach ($req in $sample) {
        Write-Host "Request: $($req.requestNumber)" -ForegroundColor Yellow
        Write-Host "  Title: $($req.title)" -ForegroundColor Green
        Write-Host "  Items: $($req.itemCount)" -ForegroundColor Gray
        Write-Host ""
    }
    
    Write-Host 'Summary Statistics:' -ForegroundColor Cyan
    Write-Host '==================' -ForegroundColor Cyan
    Write-Host "Total Requests: $($response.Count)" -ForegroundColor Green
    
    # Count titles by pattern
    $sourcingTitles = ($response | Where-Object { $_.title -like '*sourcing*' }).Count
    $productTitles = ($response | Where-Object { $_.title -like '*product*' }).Count
    $shortTitles = ($response | Where-Object { ($_.title -split ' ').Count -le 5 }).Count
    
    Write-Host "Titles with 'sourcing': $sourcingTitles" -ForegroundColor Green
    Write-Host "Titles with 'product': $productTitles" -ForegroundColor Green
    Write-Host "Titles with 5 words or less: $shortTitles" -ForegroundColor Green
    
    # Show some examples of different title patterns
    Write-Host ""
    Write-Host "Title Patterns:" -ForegroundColor Cyan
    Write-Host "===============" -ForegroundColor Cyan
    
    $singleProduct = $response | Where-Object { $_.itemCount -eq 1 } | Select-Object -First 3
    Write-Host "Single Product Requests:" -ForegroundColor Yellow
    foreach ($req in $singleProduct) {
        Write-Host "  - $($req.title)" -ForegroundColor Gray
    }
    
    $multiProduct = $response | Where-Object { $_.itemCount -gt 1 } | Select-Object -First 3
    Write-Host "Multi-Product Requests:" -ForegroundColor Yellow
    foreach ($req in $multiProduct) {
        Write-Host "  - $($req.title) (Items: $($req.itemCount))" -ForegroundColor Gray
    }
    
} catch {
    Write-Host "Error: $_" -ForegroundColor Red
}