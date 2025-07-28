# PowerShell script for syncing files to Azure Kudu
# This allows live editing without full deployment

param(
    [string]$file = "",
    [switch]$watch
)

$username = "`$foodxchange-app"
$password = "0yowobGiG2NG4bWhtpQbwTYNTKHeGtT4vXnSY8Lr3bPXP4gaFRbtJzYry47w"
$kuduUrl = "https://foodxchange-app.scm.azurewebsites.net/api/vfs/site/wwwroot/"

function Upload-File {
    param($localPath, $remotePath)
    
    $base64Auth = [Convert]::ToBase64String([Text.Encoding]::ASCII.GetBytes("$username:$password"))
    $headers = @{ Authorization = "Basic $base64Auth" }
    
    Invoke-RestMethod -Uri "$kuduUrl$remotePath" `
        -Method PUT `
        -Headers $headers `
        -InFile $localPath `
        -ContentType "application/octet-stream"
    
    Write-Host "✅ Uploaded: $localPath -> $remotePath" -ForegroundColor Green
}

if ($file) {
    # Upload single file
    Upload-File $file $file
} elseif ($watch) {
    # Watch for changes and auto-upload
    Write-Host "👀 Watching for file changes..." -ForegroundColor Cyan
    $watcher = New-Object System.IO.FileSystemWatcher
    $watcher.Path = "."
    $watcher.Filter = "*.py"
    $watcher.IncludeSubdirectories = $true
    $watcher.EnableRaisingEvents = $true
    
    Register-ObjectEvent $watcher "Changed" -Action {
        $path = $Event.SourceEventArgs.FullPath
        $relativePath = Resolve-Path -Relative $path
        Upload-File $path $relativePath
    }
    
    Write-Host "Press Ctrl+C to stop watching" -ForegroundColor Yellow
    while ($true) { Start-Sleep -Seconds 1 }
}