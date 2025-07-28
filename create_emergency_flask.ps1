# Create Emergency Flask Deployment
Write-Host "Creating Emergency Flask Deployment..." -ForegroundColor Yellow

# Clean up
if (Test-Path "emergency_flask.zip") {
    Remove-Item "emergency_flask.zip" -Force
}
if (Test-Path "emergency_flask") {
    Remove-Item "emergency_flask" -Recurse -Force
}

# Create directory
$dir = New-Item -ItemType Directory -Path "emergency_flask" -Force

# Create Flask application
$flaskApp = @'
from flask import Flask, jsonify, render_template_string
from datetime import datetime
import os

app = Flask(__name__)

# HTML template for home page
HOME_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>FoodXchange</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            text-align: center;
            padding: 50px;
            background: #f5f5f5;
        }
        .container {
            background: white;
            padding: 40px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            max-width: 600px;
            margin: 0 auto;
        }
        h1 { color: #ff6b35; }
        .status {
            background: #d4edda;
            color: #155724;
            padding: 15px;
            border-radius: 5px;
            margin: 20px 0;
        }
        a {
            color: #ff6b35;
            text-decoration: none;
            margin: 0 10px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>FoodXchange</h1>
        <p>AI-Powered Food Sourcing Platform</p>
        <div class="status">
            <strong>System Status:</strong> Operational (Emergency Mode)
        </div>
        <p>
            <a href="/health">Health Check</a> |
            <a href="/health/simple">Simple Health</a> |
            <a href="/health/detailed">Detailed Health</a>
        </p>
    </div>
</body>
</html>
'''

@app.route('/')
def home():
    return render_template_string(HOME_TEMPLATE)

@app.route('/health')
@app.route('/health/simple')
def health():
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat()
    })

@app.route('/health/detailed')
def health_detailed():
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': '1.0.0',
        'mode': 'emergency',
        'platform': 'Azure App Service',
        'message': 'Running in emergency Flask mode'
    })

@app.route('/health/advanced')
def health_advanced():
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': '1.0.0',
        'mode': 'emergency',
        'services': {
            'application': 'healthy',
            'database': 'not_connected'
        }
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    app.run(host='0.0.0.0', port=port)
'@
$flaskApp | Out-File -FilePath "$dir\application.py" -Encoding utf8

# Create requirements.txt
$requirements = @'
flask==3.0.0
gunicorn==21.2.0
'@
$requirements | Out-File -FilePath "$dir\requirements.txt" -Encoding utf8

# Create startup script
$startupScript = @'
#!/usr/bin/env python
import os
import sys
from application import app

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    app.run(host="0.0.0.0", port=port)
'@
$startupScript | Out-File -FilePath "$dir\startup.py" -Encoding utf8

# Create web.config for Azure
$webConfig = @'
<?xml version="1.0" encoding="utf-8"?>
<configuration>
  <system.webServer>
    <handlers>
      <add name="PythonHandler" path="*" verb="*" modules="httpPlatformHandler" resourceType="Unspecified"/>
    </handlers>
    <httpPlatform processPath="python" 
                  arguments="application.py"
                  stdoutLogEnabled="true" 
                  stdoutLogFile="\\?\%home%\LogFiles\python.log"
                  startupTimeLimit="60"
                  processesPerApplication="1">
      <environmentVariables>
        <environmentVariable name="PORT" value="%HTTP_PLATFORM_PORT%" />
      </environmentVariables>
    </httpPlatform>
  </system.webServer>
</configuration>
'@
$webConfig | Out-File -FilePath "$dir\web.config" -Encoding utf8

# Create the zip
Compress-Archive -Path "$dir\*" -DestinationPath "emergency_flask.zip" -Force

# Clean up
Remove-Item -Path $dir -Recurse -Force

Write-Host "Created emergency_flask.zip successfully!" -ForegroundColor Green
Write-Host "Deploy with: az webapp deploy --resource-group foodxchange-rg --name foodxchange-app --src-path emergency_flask.zip --type zip" -ForegroundColor Cyan