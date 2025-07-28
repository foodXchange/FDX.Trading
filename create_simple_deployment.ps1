# Create a minimal deployment package for Azure
Write-Host "Creating minimal deployment package..." -ForegroundColor Yellow

# Clean up
if (Test-Path "foodxchange_minimal.zip") {
    Remove-Item "foodxchange_minimal.zip" -Force
}
if (Test-Path "minimal_deploy") {
    Remove-Item "minimal_deploy" -Recurse -Force
}

# Create deployment directory
$deployDir = New-Item -ItemType Directory -Path "minimal_deploy" -Force

# Copy essential files only
Copy-Item -Path "app" -Destination $deployDir -Recurse -Force
Copy-Item -Path "requirements.txt" -Destination $deployDir -Force
Copy-Item -Path "startup_robust.py" -Destination $deployDir -Force
Copy-Item -Path "web.config" -Destination $deployDir -Force

# Create a simple startup.py that uses startup_robust.py
$startupContent = @'
import subprocess
import sys
import os

# Run the robust startup script
subprocess.run([sys.executable, "startup_robust.py"])
'@
$startupContent | Out-File -FilePath "$deployDir\startup.py" -Encoding utf8

# Create deployment configuration
$deploymentConfig = @"
[config]
SCM_DO_BUILD_DURING_DEPLOYMENT = false
ENABLE_ORYX_BUILD = false
"@
$deploymentConfig | Out-File -FilePath "$deployDir\.deployment" -Encoding utf8

# Create the zip
Compress-Archive -Path "$deployDir\*" -DestinationPath "foodxchange_minimal.zip" -Force

# Clean up
Remove-Item -Path $deployDir -Recurse -Force

Write-Host "Created foodxchange_minimal.zip" -ForegroundColor Green