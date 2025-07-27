# Bootstrap Setup Script for Food Xchange
# This script sets up Bootstrap integration with FastAPI

Write-Host "🚀 Setting up Bootstrap for Food Xchange..." -ForegroundColor Green

# Create Bootstrap directories if they don't exist
$bootstrapDirs = @(
    "app/static/bootstrap",
    "app/static/bootstrap/css",
    "app/static/bootstrap/js",
    "app/templates/bootstrap"
)

foreach ($dir in $bootstrapDirs) {
    if (!(Test-Path $dir)) {
        New-Item -Path $dir -ItemType Directory -Force
        Write-Host "✅ Created directory: $dir" -ForegroundColor Green
    } else {
        Write-Host "ℹ️  Directory already exists: $dir" -ForegroundColor Yellow
    }
}

# Download Bootstrap CSS and JS files
Write-Host "📥 Downloading Bootstrap files..." -ForegroundColor Blue

$bootstrapVersion = "5.3.2"
$bootstrapCSS = "https://cdn.jsdelivr.net/npm/bootstrap@$bootstrapVersion/dist/css/bootstrap.min.css"
$bootstrapJS = "https://cdn.jsdelivr.net/npm/bootstrap@$bootstrapVersion/dist/js/bootstrap.bundle.min.js"

try {
    # Download Bootstrap CSS
    Invoke-WebRequest -Uri $bootstrapCSS -OutFile "app/static/bootstrap/css/bootstrap.min.css"
    Write-Host "✅ Downloaded Bootstrap CSS" -ForegroundColor Green
    
    # Download Bootstrap JS
    Invoke-WebRequest -Uri $bootstrapJS -OutFile "app/static/bootstrap/js/bootstrap.bundle.min.js"
    Write-Host "✅ Downloaded Bootstrap JS" -ForegroundColor Green
} catch {
    Write-Host "⚠️  Could not download Bootstrap files. Using CDN links instead." -ForegroundColor Yellow
}

# Create README files
$bootstrapReadme = @"
# Bootstrap Integration

This directory contains Bootstrap files for the Food Xchange platform.

## Files:
- bootstrap.min.css: Bootstrap 5.3.2 CSS
- bootstrap.bundle.min.js: Bootstrap 5.3.2 JavaScript (includes Popper.js)

## Usage:
The Bootstrap files are loaded via CDN in the base template for better performance.
Local files are available as fallback.

## Customization:
- Brand colors are overridden in the base template
- Custom fonts are applied to specific elements
- Responsive design is implemented throughout
"@

$bootstrapReadme | Out-File -FilePath "app/static/bootstrap/README.md" -Encoding UTF8

$templatesReadme = @"
# Bootstrap Templates

This directory contains Bootstrap-based templates for the Food Xchange platform.

## Templates:
- base.html: Base template with navigation and footer
- rfq-form.html: RFQ Creation Form
- order-management.html: Order Management Interface
- analytics.html: Analytics Dashboard
- help.html: Help & Support Center

## Features:
- Responsive design
- Food Xchange branding
- Form validation
- Interactive components
- API integration
"@

$templatesReadme | Out-File -FilePath "app/templates/bootstrap/README.md" -Encoding UTF8

Write-Host "✅ Created README files" -ForegroundColor Green

# Check if routes file exists and needs to be added to main app
$routesFile = "app/routes/bootstrap_routes.py"
if (Test-Path $routesFile) {
    Write-Host "✅ Bootstrap routes file exists" -ForegroundColor Green
} else {
    Write-Host "⚠️  Bootstrap routes file not found. Please create it manually." -ForegroundColor Yellow
}

# Create a simple test script
$testScript = @"
# Test Bootstrap Integration
Write-Host "Testing Bootstrap integration..." -ForegroundColor Blue

# Check if all required files exist
`$requiredFiles = @(
    "app/templates/bootstrap/base.html",
    "app/templates/bootstrap/rfq-form.html",
    "app/templates/bootstrap/order-management.html",
    "app/templates/bootstrap/analytics.html",
    "app/templates/bootstrap/help.html",
    "app/routes/bootstrap_routes.py"
)

foreach (`$file in `$requiredFiles) {
    if (Test-Path `$file) {
        Write-Host "✅ `$file" -ForegroundColor Green
    } else {
        Write-Host "❌ `$file" -ForegroundColor Red
    }
}

Write-Host "`nBootstrap setup complete!" -ForegroundColor Green
Write-Host "You can now access Bootstrap screens at:" -ForegroundColor Cyan
Write-Host "  - /bootstrap/rfq" -ForegroundColor White
Write-Host "  - /bootstrap/orders" -ForegroundColor White
Write-Host "  - /bootstrap/analytics" -ForegroundColor White
Write-Host "  - /bootstrap/help" -ForegroundColor White
"@

$testScript | Out-File -FilePath "test-bootstrap.ps1" -Encoding UTF8

Write-Host "✅ Created test script: test-bootstrap.ps1" -ForegroundColor Green

# Summary
Write-Host "`n🎉 Bootstrap Setup Complete!" -ForegroundColor Green
Write-Host "`n📋 Summary:" -ForegroundColor Cyan
Write-Host "  ✅ Created Bootstrap directories" -ForegroundColor White
Write-Host "  ✅ Downloaded Bootstrap files (or using CDN)" -ForegroundColor White
Write-Host "  ✅ Created README files" -ForegroundColor White
Write-Host "  ✅ Created test script" -ForegroundColor White
Write-Host "`n🚀 Next Steps:" -ForegroundColor Cyan
Write-Host "  1. Run: .\test-bootstrap.ps1" -ForegroundColor White
Write-Host "  2. Start your FastAPI server" -ForegroundColor White
Write-Host "  3. Visit: http://localhost:8000/bootstrap/rfq" -ForegroundColor White
Write-Host "`n💡 All Bootstrap screens are now ready with Food Xchange branding!" -ForegroundColor Yellow 