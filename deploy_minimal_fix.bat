@echo off
echo Deploying minimal fix to Azure...

REM Create a minimal deployment
echo Creating minimal deployment...
mkdir minimal_deploy 2>nul

REM Create minimal startup.py
echo import os > minimal_deploy\startup.py
echo from fastapi import FastAPI >> minimal_deploy\startup.py
echo from fastapi.responses import JSONResponse >> minimal_deploy\startup.py
echo import uvicorn >> minimal_deploy\startup.py
echo. >> minimal_deploy\startup.py
echo app = FastAPI() >> minimal_deploy\startup.py
echo. >> minimal_deploy\startup.py
echo @app.get("/") >> minimal_deploy\startup.py
echo async def root(): >> minimal_deploy\startup.py
echo     return {"message": "FoodXchange is running", "status": "online"} >> minimal_deploy\startup.py
echo. >> minimal_deploy\startup.py
echo @app.get("/health") >> minimal_deploy\startup.py
echo async def health(): >> minimal_deploy\startup.py
echo     return {"status": "healthy"} >> minimal_deploy\startup.py
echo. >> minimal_deploy\startup.py
echo @app.get("/health/detailed") >> minimal_deploy\startup.py
echo async def health_detailed(): >> minimal_deploy\startup.py
echo     return JSONResponse({"status": "healthy", "service": "foodxchange"}) >> minimal_deploy\startup.py
echo. >> minimal_deploy\startup.py
echo if __name__ == "__main__": >> minimal_deploy\startup.py
echo     port = int(os.environ.get("PORT", 8000)) >> minimal_deploy\startup.py
echo     uvicorn.run(app, host="0.0.0.0", port=port) >> minimal_deploy\startup.py

REM Create requirements.txt
echo fastapi==0.104.1 > minimal_deploy\requirements.txt
echo uvicorn==0.24.0 >> minimal_deploy\requirements.txt

REM Create deployment package
cd minimal_deploy
tar -czf ../minimal_fix.zip *
cd ..

REM Deploy
echo Deploying to Azure...
az webapp deploy --resource-group foodxchange-rg --name foodxchange-app --src-path minimal_fix.zip --type zip

REM Set startup command
echo Setting startup command...
az webapp config set --resource-group foodxchange-rg --name foodxchange-app --startup-file "python startup.py"

REM Restart
echo Restarting app...
az webapp restart --name foodxchange-app --resource-group foodxchange-rg

echo Done! Wait 2 minutes then check https://www.fdx.trading/health