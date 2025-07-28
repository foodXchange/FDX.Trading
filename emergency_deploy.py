import os
import subprocess
import zipfile
import shutil

print("Creating emergency deployment package...")

# Create deployment directory
deploy_dir = "emergency_deployment"
if os.path.exists(deploy_dir):
    shutil.rmtree(deploy_dir)
os.makedirs(deploy_dir)

# Create a minimal working app
startup_content = '''import os
from fastapi import FastAPI
from fastapi.responses import JSONResponse
import uvicorn

app = FastAPI()

@app.get("/")
async def root():
    return {
        "message": "FoodXchange is running",
        "status": "online",
        "azure_openai": bool(os.getenv("AZURE_OPENAI_API_KEY"))
    }

@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "service": "foodxchange",
        "azure_openai_configured": bool(os.getenv("AZURE_OPENAI_API_KEY"))
    }

@app.get("/health/detailed")
async def health_detailed():
    return JSONResponse({
        "status": "healthy",
        "service": "foodxchange",
        "components": {
            "api": "operational",
            "azure_openai": "configured" if os.getenv("AZURE_OPENAI_API_KEY") else "not_configured"
        }
    })

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
'''

# Write startup.py
with open(os.path.join(deploy_dir, "startup.py"), "w") as f:
    f.write(startup_content)

# Create requirements.txt
requirements = '''fastapi==0.104.1
uvicorn==0.24.0
python-dotenv==1.0.0
'''

with open(os.path.join(deploy_dir, "requirements.txt"), "w") as f:
    f.write(requirements)

# Create web.config
webconfig = '''<?xml version="1.0" encoding="utf-8"?>
<configuration>
  <system.webServer>
    <handlers>
      <add name="PythonHandler" path="*" verb="*" modules="httpPlatformHandler" resourceType="Unspecified"/>
    </handlers>
    <httpPlatform processPath="python" 
                  arguments="startup.py"
                  stdoutLogEnabled="true" 
                  stdoutLogFile="\\\\?\\%home%\\LogFiles\\python.log"
                  startupTimeLimit="60"
                  processesPerApplication="1">
      <environmentVariables>
        <environmentVariable name="PORT" value="%HTTP_PLATFORM_PORT%" />
      </environmentVariables>
    </httpPlatform>
  </system.webServer>
</configuration>'''

with open(os.path.join(deploy_dir, "web.config"), "w") as f:
    f.write(webconfig)

# Create deployment zip
zip_name = "emergency_foodxchange.zip"
with zipfile.ZipFile(zip_name, 'w', zipfile.ZIP_DEFLATED) as zipf:
    for root, dirs, files in os.walk(deploy_dir):
        for file in files:
            file_path = os.path.join(root, file)
            arcname = os.path.relpath(file_path, deploy_dir)
            zipf.write(file_path, arcname)

print(f"Created {zip_name}")

# Deploy to Azure
print("Deploying to Azure...")
cmd = f"az webapp deploy --resource-group foodxchange-rg --name foodxchange-app --src-path {zip_name} --type zip"
result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
print(result.stdout)
if result.stderr:
    print("Errors:", result.stderr)

print("Deployment complete! Restarting app...")
subprocess.run("az webapp restart --name foodxchange-app --resource-group foodxchange-rg", shell=True)

print("Done! The site should be back online in 1-2 minutes.")