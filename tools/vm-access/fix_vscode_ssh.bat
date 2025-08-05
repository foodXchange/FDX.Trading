@echo off
echo Fixing VS Code SSH Connection...
echo.

REM Test basic SSH first
echo Testing SSH connection...
ssh -o ConnectTimeout=10 fdx-vm "echo SSH works!"
if %ERRORLEVEL% NEQ 0 (
    echo SSH connection failed! Check your internet connection.
    pause
    exit /b 1
)

echo SSH connection successful!
echo.

REM Clear VS Code Remote Server cache
echo Clearing VS Code remote server cache...
rmdir /s /q "%APPDATA%\Code\User\globalStorage\ms-vscode-remote.remote-ssh" 2>nul
rmdir /s /q "%USERPROFILE%\.vscode-server" 2>nul

echo.
echo Starting VS Code with fresh connection...
"C:\Users\foodz\AppData\Local\Programs\Microsoft VS Code\bin\code" --new-window --folder-uri vscode-remote://ssh-remote+fdx-vm/home/fdxfounder/fdx/app

echo.
echo If VS Code still doesn't connect:
echo 1. In VS Code, press Ctrl+Shift+P
echo 2. Type: "Remote-SSH: Kill VS Code Server on Host"
echo 3. Select fdx-vm
echo 4. Try connecting again
echo.
echo Alternative: Use the web IDE at http://4.206.1.15:8080
echo Password: a8853291ae5fa6f122a04412
echo.
pause