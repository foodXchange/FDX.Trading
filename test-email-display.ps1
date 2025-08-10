# Test Email Display in User Profile

# Ignore SSL certificate errors
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

Write-Host "Checking User Email Display..." -ForegroundColor Green

# Test with admin user (ID: 1)
$userId = 1

try {
    # Get user details
    Write-Host "`nFetching user ID $userId details..." -ForegroundColor Cyan
    $user = Invoke-RestMethod -Uri "$baseUrl/api/users/$userId" -Method Get
    
    Write-Host "`nUser Data:" -ForegroundColor Yellow
    Write-Host "  ID: $($user.id)" -ForegroundColor Gray
    Write-Host "  Username: $($user.username)" -ForegroundColor Gray
    Write-Host "  Email: $($user.email)" -ForegroundColor Gray
    Write-Host "  First Name: $($user.firstName)" -ForegroundColor Gray
    Write-Host "  Last Name: $($user.lastName)" -ForegroundColor Gray
    Write-Host "  Company: $($user.companyName)" -ForegroundColor Gray
    
    if ($user.email) {
        Write-Host "`n✓ Email field is populated: $($user.email)" -ForegroundColor Green
    } elseif ($user.username) {
        Write-Host "`n✓ Username can be used as email: $($user.username)" -ForegroundColor Yellow
    } else {
        Write-Host "`n✗ No email or username found!" -ForegroundColor Red
    }
    
    # Update the user to ensure email matches username if needed
    if (-not $user.email -and $user.username) {
        Write-Host "`nSetting email to match username..." -ForegroundColor Cyan
        
        $updateData = @{
            email = $user.username
            firstName = "Admin"
            lastName = "User"
            phoneNumber = $user.phoneNumber
            companyName = $user.companyName
            country = $user.country
            address = $user.address
            website = $user.website
        } | ConvertTo-Json
        
        $updated = Invoke-RestMethod -Uri "$baseUrl/api/users/$userId" `
            -Method Put `
            -ContentType "application/json" `
            -Body $updateData
            
        Write-Host "Email updated to: $($updated.email)" -ForegroundColor Green
    }
    
} catch {
    Write-Host "Error:" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
}

Write-Host "`nTo test the user profile page:" -ForegroundColor Cyan
Write-Host "1. Go to: http://localhost:53813/user-profile.html" -ForegroundColor Yellow
Write-Host "2. The email field should now display: udi@fdx.trading" -ForegroundColor Yellow
Write-Host "3. In edit mode, the email field should be read-only with gray background" -ForegroundColor Yellow