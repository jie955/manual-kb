#Requires -Version 5.1
<#
.SYNOPSIS
  打包客户 Lite 交付 zip（run-007 Web demo · 不含 venv、modelscope、密钥）

.USAGE
  cd D:\pythonProject\manual-kb
  .\pack-lite.ps1
  .\pack-lite.ps1 -OutputZip "D:\deliver\custom.zip"
#>
param(
    [string]$OutputZip = ""
)

$ErrorActionPreference = "Stop"
$RepoRoot = $PSScriptRoot
$Date = Get-Date -Format "yyyyMMdd"
$DistDir = Join-Path $RepoRoot "dist"
$StageName = "manual-kb-lite"
$StageRoot = Join-Path $env:TEMP "$StageName-$Date"

if (-not $OutputZip) {
    $OutputZip = Join-Path $DistDir "manual-kb-lite-$Date.zip"
}

function Remove-IfExists([string]$Path) {
    if (Test-Path $Path) { Remove-Item $Path -Recurse -Force }
}

function Copy-Files([string]$Src, [string]$Dst, [string[]]$Include) {
    $null = New-Item -ItemType Directory -Force -Path $Dst
    foreach ($pattern in $Include) {
        Get-ChildItem -Path $Src -Filter $pattern -File -ErrorAction SilentlyContinue |
            Copy-Item -Destination $Dst -Force
    }
}

function Require-Path([string]$Path, [string]$Label) {
    if (-not (Test-Path $Path)) {
        throw "missing required artifact for Lite pack ($Label): $Path"
    }
}

Write-Host ">>> staging: $StageRoot"
Remove-IfExists $StageRoot
$null = New-Item -ItemType Directory -Force -Path $StageRoot

Copy-Item (Join-Path $RepoRoot "DELIVERY_README.md") (Join-Path $StageRoot "DELIVERY_README.md")

Copy-Files $RepoRoot $StageRoot @(
    "*.py", "requirements.txt", "requirements-local.txt",
    "eval_queries.json", ".env.example", ".gitignore"
)
Get-ChildItem -Path $RepoRoot -Filter "*.md" -File |
    Where-Object { $_.Name -ne "PACKAGING.md" } |
    Copy-Item -Destination $StageRoot -Force

Require-Path (Join-Path $RepoRoot "demo") "demo/"
Copy-Item (Join-Path $RepoRoot "demo") (Join-Path $StageRoot "demo") -Recurse -Force

$ScratchSrc = Join-Path $RepoRoot "_scratch"
$ScratchDst = Join-Path $StageRoot "_scratch"

$null = New-Item -ItemType Directory -Force -Path (Join-Path $ScratchDst "input")
if (Test-Path (Join-Path $ScratchSrc "input")) {
    Copy-Item (Join-Path $ScratchSrc "input\*") (Join-Path $ScratchDst "input") -Recurse -Force
}

$Run007ChromaSrc = Join-Path $ScratchSrc "run-007\chroma_captioned"
Require-Path $Run007ChromaSrc "run-007/chroma_captioned"
$Run007Dst = Join-Path $ScratchDst "run-007"
$null = New-Item -ItemType Directory -Force -Path $Run007Dst
Copy-Item $Run007ChromaSrc (Join-Path $Run007Dst "chroma_captioned") -Recurse -Force

$Run006Src = Join-Path $ScratchSrc "run-006"
$Run006Dst = Join-Path $ScratchDst "run-006"
Require-Path (Join-Path $Run006Src "images") "run-006/images"
$null = New-Item -ItemType Directory -Force -Path $Run006Dst
Copy-Item (Join-Path $Run006Src "images") (Join-Path $Run006Dst "images") -Recurse -Force

$EvalReport = Join-Path $Run006Src "eval\experiment_report.json"
Require-Path $EvalReport "run-006/eval/experiment_report.json"
$EvalDst = Join-Path $Run006Dst "eval"
$null = New-Item -ItemType Directory -Force -Path $EvalDst
Copy-Item $EvalReport $EvalDst -Force

foreach ($f in @("qa_groups.json", "chunks.json")) {
    $p = Join-Path $Run006Src $f
    if (Test-Path $p) { Copy-Item $p $Run006Dst -Force }
}

$leaks = @(
    (Join-Path $StageRoot ".env"),
    (Join-Path $StageRoot ".translate_cache.json"),
    (Join-Path $StageRoot ".caption_cache.json")
)
foreach ($leak in $leaks) {
    if (Test-Path $leak) {
        throw "refusing to pack: sensitive file present: $leak"
    }
}

$null = New-Item -ItemType Directory -Force -Path $DistDir
if (Test-Path $OutputZip) { Remove-Item $OutputZip -Force }
Compress-Archive -Path (Join-Path $StageRoot "*") -DestinationPath $OutputZip -CompressionLevel Optimal

$sizeMb = [math]::Round((Get-Item $OutputZip).Length / 1MB, 1)
Write-Host ""
Write-Host ">>> done: $OutputZip ($sizeMb MB)"
Write-Host ">>> demo: python qa_server.py --chroma-dir _scratch/run-007/chroma_captioned --images-dir _scratch/run-006/images"

Remove-IfExists $StageRoot
