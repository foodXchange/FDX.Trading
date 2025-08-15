# Test script to add a profile image to Ardo supplier

$baseUrl = "http://localhost:53813"
$supplierId = 260

# Test with a sample logo URL (Ardo company logo)
$body = @{
    companyName = "Ardo"
    email = "ardo@supplier.fdx"
    phoneNumber = "+32 55 23 26 11"
    website = "http://www.ardo.com"
    address = "Wezestraat 61, 8850 Ardooie, Belgium"
    country = "Belgium"
    businessType = "Frozen Food Manufacturer"
    category = "Food & Beverages"
    profileImage = "https://www.ardo.com/_assets/images/logo.svg"
} | ConvertTo-Json

$headers = @{
    "Content-Type" = "application/json"
}

try {
    $response = Invoke-RestMethod -Uri "$baseUrl/api/users/$supplierId/supplier-details" -Method PUT -Body $body -Headers $headers
    Write-Host "Successfully updated supplier profile with image!" -ForegroundColor Green
    Write-Host "Response:" -ForegroundColor Cyan
    $response | ConvertTo-Json -Depth 10
}
catch {
    Write-Host "Error updating supplier:" -ForegroundColor Red
    Write-Host $_.Exception.Message
}