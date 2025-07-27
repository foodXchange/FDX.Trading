# Food Xchange v0 Component Integration Script (Simplified)
param(
    [Parameter(Mandatory=$true)]
    [string]$ComponentName
)

Write-Host "🚀 Food Xchange v0 Component Integration" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Green

# Check if component name is provided
if (-not $ComponentName) {
    Write-Host "❌ Error: Component name is required" -ForegroundColor Red
    Write-Host "Usage: .\integrate-v0-simple.ps1 -ComponentName 'rfq-form'" -ForegroundColor Yellow
    exit 1
}

Write-Host "📋 Component: $ComponentName" -ForegroundColor Cyan

# Create directories if they don't exist
$directories = @(
    "app/templates/v0-components",
    "app/static/v0-styles", 
    "app/static/js/v0-components",
    "app/routes"
)

foreach ($dir in $directories) {
    if (-not (Test-Path $dir)) {
        New-Item -Path $dir -ItemType Directory -Force
        Write-Host "✅ Created directory: $dir" -ForegroundColor Green
    }
}

# Create simple HTML template
$htmlContent = @"
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{title | default('$ComponentName')}} - Food Xchange</title>
    
    <!-- Food Xchange Custom Fonts -->
    <link rel="stylesheet" href="/static/brand/fx-fonts.css">
    <link rel="stylesheet" href="/static/brand/fx-complete.css">
    
    <!-- Tailwind CSS -->
    <script src="https://cdn.tailwindcss.com"></script>
    
    <!-- v0 Generated Styles -->
    <link rel="stylesheet" href="/static/v0-styles/$ComponentName.css">
</head>
<body class="font-roboto-serif bg-white text-gray-800">
    <!-- Navigation -->
    <nav class="bg-white shadow-sm border-b border-gray-200">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div class="flex justify-between h-16">
                <div class="flex items-center">
                    <div class="flex-shrink-0">
                        <img src="/static/brand/logos/Favicon.png" alt="Food Xchange" class="h-8 w-auto">
                        <h1 class="text-xl font-david-libre font-semibold text-fx-primary ml-2">Food Xchange</h1>
                    </div>
                </div>
                <div class="flex items-center space-x-4">
                    <a href="/" class="text-gray-600 hover:text-fx-primary px-3 py-2 rounded-md text-sm font-medium">Home</a>
                    <a href="/rfq-form" class="text-gray-600 hover:text-fx-primary px-3 py-2 rounded-md text-sm font-medium">RFQ</a>
                    <a href="/suppliers" class="text-gray-600 hover:text-fx-primary px-3 py-2 rounded-md text-sm font-medium">Suppliers</a>
                </div>
            </div>
        </div>
    </nav>
    
    <!-- Main Content -->
    <main class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div class="v0-component">
            <!-- Your v0 generated content goes here -->
            <!-- Copy the HTML from your v0 generated component -->
        </div>
    </main>
    
    <!-- Footer -->
    <footer class="bg-gray-50 border-t border-gray-200 mt-16">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
            <div class="text-center text-gray-500">
                <p>Copyright 2024 Food Xchange. All rights reserved.</p>
            </div>
        </div>
    </footer>
    
    <!-- v0 Generated JavaScript -->
    <script src="/static/js/v0-components/$ComponentName.js"></script>
</body>
</html>
"@

# Create simple CSS file
$cssContent = @"
/* $ComponentName - v0 Generated Styles */
/* Copy the CSS from your v0 generated component here */

/* Food Xchange Brand Integration */
.v0-component {
    font-family: 'Roboto Serif', serif;
}

.v0-component h1, .v0-component h2, .v0-component h3 {
    font-family: 'David Libre', serif;
    font-weight: 600;
}

.v0-component button, .v0-component input, .v0-component select {
    font-family: 'Causten', sans-serif;
}

/* Add your v0 generated CSS here */
"@

# Create simple JavaScript file
$jsContent = @"
// $ComponentName - v0 Generated JavaScript
// Copy the JavaScript from your v0 generated component here

// Food Xchange Integration
document.addEventListener('DOMContentLoaded', function() {
    console.log('$ComponentName component loaded');
    
    // Add your component-specific JavaScript here
    // Copy the JavaScript from your v0 generated component
});
"@

# Create simple FastAPI route
$routeContent = @"
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

@router.get("/$ComponentName", response_class=HTMLResponse)
async def $ComponentName_page(request: Request):
    """Render the $ComponentName page"""
    return templates.TemplateResponse(
        "v0-components/$ComponentName.html",
        {"request": request, "title": "$ComponentName".replace('-', ' ').title()}
    )

@router.post("/api/$ComponentName")
async def $ComponentName_api(data: dict):
    """Handle $ComponentName form submission"""
    return {"success": True, "message": "$ComponentName submitted successfully"}
"@

# Write files
$htmlContent | Out-File -FilePath "app/templates/v0-components/$ComponentName.html" -Encoding UTF8
$cssContent | Out-File -FilePath "app/static/v0-styles/$ComponentName.css" -Encoding UTF8
$jsContent | Out-File -FilePath "app/static/js/v0-components/$ComponentName.js" -Encoding UTF8
$routeContent | Out-File -FilePath "app/routes/v0_$ComponentName`_routes.py" -Encoding UTF8

Write-Host "✅ Created files:" -ForegroundColor Green
Write-Host "   📄 app/templates/v0-components/$ComponentName.html" -ForegroundColor Cyan
Write-Host "   🎨 app/static/v0-styles/$ComponentName.css" -ForegroundColor Cyan
Write-Host "   ⚡ app/static/js/v0-components/$ComponentName.js" -ForegroundColor Cyan
Write-Host "   🛣️  app/routes/v0_$ComponentName`_routes.py" -ForegroundColor Cyan

Write-Host ""
Write-Host "📝 Next Steps:" -ForegroundColor Yellow
Write-Host "1. Copy your v0 generated HTML into the template file" -ForegroundColor White
Write-Host "2. Copy your v0 generated CSS into the CSS file" -ForegroundColor White
Write-Host "3. Copy your v0 generated JavaScript into the JS file" -ForegroundColor White
Write-Host "4. Add the route to your main app.py file" -ForegroundColor White
Write-Host "5. Test your component at: http://localhost:8000/$ComponentName" -ForegroundColor White

Write-Host ""
Write-Host "🎯 Ready to integrate your v0 component!" -ForegroundColor Green 