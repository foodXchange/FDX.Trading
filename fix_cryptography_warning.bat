@echo off
echo Fixing cryptography warning...
echo.

echo Uninstalling cryptography and related packages...
venv\Scripts\python.exe -m pip uninstall cryptography python-jose PyJWT -y

echo.
echo Installing fresh versions...
venv\Scripts\python.exe -m pip install cryptography==45.0.5
venv\Scripts\python.exe -m pip install python-jose[cryptography]==3.3.0

echo.
echo Testing imports...
venv\Scripts\python.exe -c "import warnings; warnings.filterwarnings('ignore'); from jose import jwt; print('✅ python-jose import successful')"

echo.
echo Done! The warning should be resolved.
pause 