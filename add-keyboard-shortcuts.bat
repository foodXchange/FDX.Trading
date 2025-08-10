@echo off
echo Adding keyboard shortcuts to all HTML files...

REM List of files to update
set files=supplier-catalog.html price-management.html users.html request-detail.html user-profile.html index.html supplier-profile.html product-detail.html product-catalog.html

REM Add the script tag before </body> in each file
for %%f in (%files%) do (
    echo Processing %%f...
    powershell -Command "(Get-Content 'C:\FDX.Trading\wwwroot\%%f') -replace '</body>', '    `n    <!-- Global Keyboard Shortcuts -->`n    <script src=\"/js/keyboard-shortcuts.js\"></script>`n</body>' | Set-Content 'C:\FDX.Trading\wwwroot\%%f'"
)

echo Done! Keyboard shortcuts have been added to all HTML files.