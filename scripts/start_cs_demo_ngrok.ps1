# Start English CS demo + ngrok tunnel (Phase 0 · 殷主管 Review)

$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
Set-Location $Root

$Port = 8765
$Images = "_scratch/run-006/images"

Write-Host "Starting qa_server on port $Port ..."
$server = Start-Process -PassThru -NoNewWindow python -ArgumentList @(
    "qa_server.py",
    "--unified-cs",
    "--demo-presentation", "cs-email",
    "--allowed-libraries", "a3s,ad5s",
    "--images-dir", $Images,
    "--port", "$Port"
)

Start-Sleep -Seconds 3

if (-not (Get-Command ngrok -ErrorAction SilentlyContinue)) {
    Write-Host "ngrok not found. Install: https://ngrok.com/download"
    Write-Host "Local URL: http://127.0.0.1:$Port"
    exit 0
}

Write-Host "Starting ngrok http $Port ..."
Write-Host "Share the https://*.ngrok URL with reviewer."
ngrok http $Port

# Cleanup on exit
Stop-Process -Id $server.Id -Force -ErrorAction SilentlyContinue
