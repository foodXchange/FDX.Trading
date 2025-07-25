#!/usr/bin/env python
"""Diagnostic script to identify Azure deployment issues"""
import os
import sys
import json
import subprocess

print("=== FoodXchange Azure Diagnostic Tool ===\n")

# Collect diagnostic information
diagnostics = {
    "python_version": sys.version,
    "python_executable": sys.executable,
    "working_directory": os.getcwd(),
    "environment_variables": {},
    "installed_packages": [],
    "files_in_directory": [],
    "import_tests": {}
}

# Key environment variables
key_vars = ['PORT', 'WEBSITE_INSTANCE_ID', 'WEBSITE_SITE_NAME', 'WEBSITE_HOSTNAME', 
            'PYTHON_VERSION', 'APPSETTING_SCM_DO_BUILD_DURING_DEPLOYMENT']
for var in key_vars:
    diagnostics["environment_variables"][var] = os.environ.get(var, "NOT SET")

# List files
try:
    diagnostics["files_in_directory"] = sorted([f for f in os.listdir('.') if not f.startswith('.')])[:20]
except:
    diagnostics["files_in_directory"] = ["ERROR READING DIRECTORY"]

# Test imports
test_imports = ['fastapi', 'uvicorn', 'gunicorn', 'flask', 'django']
for module in test_imports:
    try:
        __import__(module)
        diagnostics["import_tests"][module] = "SUCCESS"
    except ImportError as e:
        diagnostics["import_tests"][module] = f"FAILED: {str(e)}"

# Check pip list
try:
    result = subprocess.run([sys.executable, '-m', 'pip', 'list'], 
                          capture_output=True, text=True, timeout=5)
    if result.returncode == 0:
        diagnostics["installed_packages"] = result.stdout.split('\n')[:10]
except:
    diagnostics["installed_packages"] = ["ERROR RUNNING PIP"]

# Create web response
def application(environ, start_response):
    path = environ.get('PATH_INFO', '/')
    
    if path == '/diagnose':
        status = '200 OK'
        response_headers = [('Content-Type', 'application/json')]
        start_response(status, response_headers)
        return [json.dumps(diagnostics, indent=2).encode('utf-8')]
    
    else:
        status = '200 OK'
        response_headers = [('Content-Type', 'text/html; charset=utf-8')]
        start_response(status, response_headers)
        
        html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>FoodXchange Diagnostics</title>
            <style>
                body { font-family: monospace; margin: 20px; background: #f5f5f5; }
                .container { background: white; padding: 20px; border-radius: 5px; }
                h1 { color: #e53e3e; }
                .section { margin: 20px 0; padding: 15px; background: #f7fafc; border-radius: 5px; }
                .success { color: #38a169; }
                .error { color: #e53e3e; }
                pre { background: #2d3748; color: #fff; padding: 10px; overflow-x: auto; }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>🔧 FoodXchange Diagnostic Report</h1>
                
                <div class="section">
                    <h2>Python Information</h2>
                    <pre>""" + f"""
Version: {diagnostics['python_version']}
Executable: {diagnostics['python_executable']}
Working Dir: {diagnostics['working_directory']}
                    """.strip() + """</pre>
                </div>
                
                <div class="section">
                    <h2>Environment Variables</h2>
                    <ul>"""
        
        for key, value in diagnostics['environment_variables'].items():
            status = 'success' if value != 'NOT SET' else 'error'
            html += f'\n<li class="{status}">{key}: {value}</li>'
        
        html += """
                    </ul>
                </div>
                
                <div class="section">
                    <h2>Import Tests</h2>
                    <ul>"""
        
        for module, result in diagnostics['import_tests'].items():
            status = 'success' if result == 'SUCCESS' else 'error'
            html += f'\n<li class="{status}">{module}: {result}</li>'
        
        html += """
                    </ul>
                </div>
                
                <div class="section">
                    <h2>Files Found</h2>
                    <ul>"""
        
        for file in diagnostics['files_in_directory'][:10]:
            html += f'\n<li>{file}</li>'
        
        html += """
                    </ul>
                </div>
                
                <div class="section">
                    <h2>Actions to Take:</h2>
                    <ol>
                        <li>Check if PORT environment variable is set in Azure</li>
                        <li>Verify Python version in Azure Configuration</li>
                        <li>Check Deployment Center logs for build errors</li>
                        <li>Ensure startup command is set correctly</li>
                    </ol>
                    
                    <p><a href="/diagnose">View JSON diagnostic data</a></p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return [html.encode('utf-8')]

# Multiple entry points
app = application
wsgi_app = application

if __name__ == "__main__":
    print("\nRunning diagnostic server...")
    from wsgiref.simple_server import make_server
    port = int(os.environ.get('PORT', 8000))
    server = make_server('', port, application)
    print(f"Diagnostic server running on http://localhost:{port}")
    print(f"Visit http://localhost:{port}/ for HTML report")
    print(f"Visit http://localhost:{port}/diagnose for JSON data")
    server.serve_forever()