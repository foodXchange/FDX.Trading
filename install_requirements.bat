@echo off
echo Installing FoodXchange requirements...
call foodxchange-env\Scripts\activate.bat
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
echo.
echo Installation complete!
pause