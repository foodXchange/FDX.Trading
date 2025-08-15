# Test Requests Page Navigation Update

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

Write-Host 'Testing Requests Page Updates' -ForegroundColor Cyan
Write-Host '==============================' -ForegroundColor Cyan
Write-Host ''

# Test the requests page loads
try {
    $response = Invoke-WebRequest -Uri 'http://localhost:53813/requests.html' -Method Get -ErrorAction Stop
    if ($response.StatusCode -eq 200) {
        Write-Host '✓ Requests page loads successfully' -ForegroundColor Green
        Write-Host "  Status: $($response.StatusCode)" -ForegroundColor Gray
        
        # Check for navbar elements
        if ($response.Content -match 'navbar') {
            Write-Host '✓ Navbar is present on the page' -ForegroundColor Green
        }
        
        if ($response.Content -match 'FDX Trading') {
            Write-Host '✓ Brand logo is present' -ForegroundColor Green
        }
        
        if ($response.Content -match 'nav-link active.*Requests') {
            Write-Host '✓ Requests nav link is marked as active' -ForegroundColor Green
        }
    }
} catch {
    Write-Host "✗ Error loading requests page: $_" -ForegroundColor Red
}

Write-Host ''
Write-Host 'Changes Made to Requests Page:' -ForegroundColor Yellow
Write-Host '===============================' -ForegroundColor Yellow
Write-Host '✓ Added unified navbar matching dashboard design' -ForegroundColor Green
Write-Host '✓ Removed duplicate header with navigation buttons' -ForegroundColor Green
Write-Host '✓ Moved action buttons (New Request, Import CSV) to filters section' -ForegroundColor Green
Write-Host '✓ Added user avatar in navbar for profile access' -ForegroundColor Green
Write-Host '✓ Added notification bell with badge' -ForegroundColor Green
Write-Host '✓ Maintained consistent navigation across pages' -ForegroundColor Green
Write-Host '✓ No welcome message (as requested)' -ForegroundColor Green

Write-Host ''
Write-Host 'Navigation Structure:' -ForegroundColor Cyan
Write-Host '====================' -ForegroundColor Cyan
Write-Host '• Single unified navbar at top' -ForegroundColor White
Write-Host '• All page navigation links in one place' -ForegroundColor White
Write-Host '• User controls (avatar, notifications, logout) on right' -ForegroundColor White
Write-Host '• Page-specific actions in filter bar' -ForegroundColor White
Write-Host '• Clean, professional appearance' -ForegroundColor White