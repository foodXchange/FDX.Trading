# Test with a placeholder image
$body = @{
    companyName = "Ardo"
    email = "ardo@supplier.fdx"
    phoneNumber = "+32 55 23 26 11"
    website = "http://www.ardo.com"
    address = "Wezestraat 61, 8850 Ardooie, Belgium"
    country = "Belgium"
    businessType = "Frozen Food Manufacturer"
    category = "Food & Beverages"
    profileImage = "https://via.placeholder.com/120x120/667eea/ffffff?text=ARDO"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:53813/api/users/260/supplier-details" -Method PUT -Body $body -ContentType "application/json"