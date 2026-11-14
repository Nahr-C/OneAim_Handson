$repoRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
$pythonPath = "C:\Users\User\anaconda3\envs\mrseg\python.exe"
$serverPath = Join-Path $repoRoot "app\server.py"

$existing = Get-Process python -ErrorAction SilentlyContinue |
    Where-Object {
        $_.Path -eq $pythonPath
    }

if ($existing) {
    $existing | ForEach-Object {
        Stop-Process -Id $_.Id -Force
    }
    Start-Sleep -Milliseconds 500
}

& $pythonPath $serverPath
