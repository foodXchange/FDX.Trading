@echo off
echo 🚀 Food Xchange v0 Component Integration Setup
echo ==============================================

echo.
echo ✅ Creating directories...
if not exist "app\templates\v0-components" mkdir "app\templates\v0-components"
if not exist "app\static\v0-styles" mkdir "app\static\v0-styles"
if not exist "app\static\js\v0-components" mkdir "app\static\js\v0-components"
if not exist "app\routes" mkdir "app\routes"

echo.
echo 📁 Directories created:
echo    app\templates\v0-components
echo    app\static\v0-styles
echo    app\static\js\v0-components
echo    app\routes

echo.
echo 🎯 Next Steps:
echo 1. Open v0 Pro in your browser
echo 2. Copy a prompt from v0-pro-optimized-prompts.md
echo 3. Generate your component
echo 4. Download the generated files
echo 5. Copy the HTML, CSS, and JS into the appropriate directories
echo 6. Test your component

echo.
echo 📖 Open v0 Pro now? (y/n)
set /p choice=
if /i "%choice%"=="y" (
    start https://v0.dev
)

echo.
echo 🎉 Setup complete! Ready to integrate v0 components.
pause 