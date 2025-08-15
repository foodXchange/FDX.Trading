# Test Profile Update

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
$userId = 1

Write-Host "Testing Profile Update..." -ForegroundColor Green

try {
    # Get current user
    Write-Host "`nGetting current user data..." -ForegroundColor Cyan
    $user = Invoke-RestMethod -Uri "$baseUrl/api/users/$userId" -Method Get
    
    Write-Host "Current user:" -ForegroundColor Yellow
    Write-Host "  Email: $($user.email)" -ForegroundColor Gray
    Write-Host "  Username: $($user.username)" -ForegroundColor Gray
    Write-Host "  FirstName: $($user.firstName)" -ForegroundColor Gray
    Write-Host "  LastName: $($user.lastName)" -ForegroundColor Gray
    Write-Host "  ProfileImage: $($user.profileImage)" -ForegroundColor Gray
    
    # Try to update
    $updateData = @{
        firstName = "John"
        lastName = "Doe"
        email = $user.username  # Use username as email
        phoneNumber = "+1234567890"
        companyName = "FDX Trading"
        country = "Israel"
        address = "Test Address"
        website = "https://example.com"
        profileImage = "cool"  # Just use text for now
    } | ConvertTo-Json
    
    Write-Host "`nSending update request..." -ForegroundColor Cyan
    Write-Host "Update data: $updateData" -ForegroundColor Gray
    
    $response = Invoke-RestMethod -Uri "$baseUrl/api/users/$userId" `
        -Method Put `
        -ContentType "application/json" `
        -Body $updateData
    
    Write-Host "`nUpdate response:" -ForegroundColor Green
    Write-Host "  FirstName: $($response.firstName)" -ForegroundColor Gray
    Write-Host "  LastName: $($response.lastName)" -ForegroundColor Gray
    Write-Host "  ProfileImage: $($response.profileImage)" -ForegroundColor Gray
    
    if ($response.firstName -eq "John" -and $response.lastName -eq "Doe") {
        Write-Host "`nUpdate successful!" -ForegroundColor Green
    } else {
        Write-Host "`nUpdate failed - values not changed" -ForegroundColor Red
    }
    
} catch {
    Write-Host "`nError:" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
    
    if ($_.Exception.Response) {
        $reader = [System.IO.StreamReader]::new($_.Exception.Response.GetResponseStream())
        $errorContent = $reader.ReadToEnd()
        Write-Host "Response: $errorContent" -ForegroundColor Red
    }
}

Write-Host "`nCheck the profile at: http://localhost:53813/user-profile.html" -ForegroundColor Yellow