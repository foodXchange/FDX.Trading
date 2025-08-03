@echo off
echo ========================================
echo Start FoodXchange Production Server
echo ========================================
echo.

echo 🔧 Starting production server...
echo.

echo 📋 Server Configuration:
echo - Host: 0.0.0.0 (accessible from network)
echo - Port: 8000
echo - Environment: Production
echo.

echo 🚀 Starting server...
python -c "import uvicorn; uvicorn.run('app:app', host='0.0.0.0', port=8000, reload=False)"

echo.
echo ✅ Server started successfully!
echo 🌐 Access your app at: http://localhost:8000
echo 🌐 Network access: http://[your-ip]:8000
echo.

pause 