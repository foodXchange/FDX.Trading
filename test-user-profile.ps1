# Test User Profile Update API

# Ignore SSL certificate errors for testing
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

Write-Host "Testing User Profile Update..." -ForegroundColor Green

# Test with admin user (ID: 1)
$userId = 1

try {
    # Get current user details
    Write-Host "`nFetching user details for ID: $userId" -ForegroundColor Cyan
    $user = Invoke-RestMethod -Uri "$baseUrl/api/users/$userId" -Method Get
    
    Write-Host "Current user info:" -ForegroundColor Yellow
    Write-Host "  Name: $($user.firstName) $($user.lastName)" -ForegroundColor Gray
    Write-Host "  Email: $($user.email)" -ForegroundColor Gray
    Write-Host "  Company: $($user.companyName)" -ForegroundColor Gray
    
    # Update user with proper name
    $updateData = @{
        firstName = "Udi"
        lastName = "Admin"
        email = $user.email
        phoneNumber = $user.phoneNumber
        companyName = $user.companyName
        country = $user.country
        address = $user.address
        website = $user.website
    } | ConvertTo-Json
    
    Write-Host "`nUpdating user profile..." -ForegroundColor Cyan
    $response = Invoke-RestMethod -Uri "$baseUrl/api/users/$userId" `
        -Method Put `
        -ContentType "application/json" `
        -Body $updateData
    
    Write-Host "User profile updated successfully!" -ForegroundColor Green
    Write-Host "  Updated Name: $($response.firstName) $($response.lastName)" -ForegroundColor Gray
    
} catch {
    Write-Host "Error during test:" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
}

Write-Host "`nYou can now view the user profile at:" -ForegroundColor Cyan
Write-Host "http://localhost:53813/user-profile.html" -ForegroundColor Yellow
Write-Host "(The 'undefined undefined' issue should now be fixed)" -ForegroundColor Gray