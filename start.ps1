# Params
param (
    [string]$mode = "--debug"
)

# venv
$python = Join-Path $PSScriptRoot ".venv\Scripts\python.exe"

if (-not (Test-Path $python)) {
    throw "Virtual environment Python not found: $python`n"
}

# Activate JIT to boost performance
$env:PYTHON_JIT=1

# Command
$command = @"
Write-Host ' * Starting server...'
Write-Host ' * Running in mode: $mode`n'
& '$python' -m social_site.__init__ $mode --host=0.0.0.0 --cert=localhost+2.pem --key=localhost+2-key.pem
"@

Write-Output $command

# Start dev server
Start-Process powershell.exe -ArgumentList @(
    "-NoExit",
    "-Command",
    $command
)