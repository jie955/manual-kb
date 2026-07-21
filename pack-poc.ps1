#Requires -Version 5.1
<#
.SYNOPSIS
  三库 POC 交付包 → dist/manual-kb-poc-YYYYMMDD.zip

.USAGE
  cd D:\pythonProject\manual-kb
  .\pack-poc.ps1
#>
param(
    [string]$OutputZip = ""
)

$ErrorActionPreference = "Stop"
$RepoRoot = $PSScriptRoot
$Date = Get-Date -Format "yyyyMMdd"
$DistDir = Join-Path $RepoRoot "dist"
$StageName = "manual-kb-poc"
$StageRoot = Join-Path $env:TEMP "$StageName-$Date"

if (-not $OutputZip) {
    $OutputZip = Join-Path $DistDir "manual-kb-poc-$Date.zip"
}

function Remove-IfExists([string]$Path) {
    if (Test-Path $Path) { Remove-Item $Path -Recurse -Force }
}

function Require-Path([string]$Path, [string]$Label) {
    if (-not (Test-Path $Path)) {
        throw "missing required artifact ($Label): $Path"
    }
}

function Copy-Tree([string]$Src, [string]$Dst) {
    $null = New-Item -ItemType Directory -Force -Path (Split-Path $Dst -Parent)
    Copy-Item $Src $Dst -Recurse -Force
}

function Copy-ChromaDir([string]$Src, [string]$Dst) {
    Require-Path $Src "chroma_captioned"
    $null = New-Item -ItemType Directory -Force -Path $Dst
    Get-ChildItem -Path $Src -Force | Where-Object {
        $_.Name -notmatch '\.bak' -and $_.Name -notmatch '^chroma_captioned\.bak'
    } | ForEach-Object {
        $target = Join-Path $Dst $_.Name
        if ($_.PSIsContainer) {
            Copy-Tree $_.FullName $target
        } else {
            Copy-Item $_.FullName $target -Force
        }
    }
}

function Copy-RunData(
    [string]$RunName,
    [string[]]$Files,
    [switch]$Chroma,
    [switch]$RequireImages
) {
    $SrcBase = Join-Path $RepoRoot "_scratch\$RunName"
    $DstBase = Join-Path $StageRoot "_scratch\$RunName"
    $null = New-Item -ItemType Directory -Force -Path $DstBase

    foreach ($f in $Files) {
        $src = Join-Path $SrcBase $f
        Require-Path $src "$RunName/$f"
        Copy-Item $src (Join-Path $DstBase $f) -Force
    }
    if ($Chroma) {
        Copy-ChromaDir (Join-Path $SrcBase "chroma_captioned") (Join-Path $DstBase "chroma_captioned")
    }
    $imgSrc = Join-Path $SrcBase "images"
    if (Test-Path $imgSrc) {
        Copy-Tree $imgSrc (Join-Path $DstBase "images")
    } elseif ($RequireImages) {
        $imgDst = Join-Path $DstBase "images"
        $null = New-Item -ItemType Directory -Force -Path $imgDst
    }
}

$PipelinePy = @(
    "qa_server.py",
    "retrieval_engine.py",
    "embed_ingest_local.py",
    "chunk_builder.py",
    "qa_doc_extractor.py",
    "generate_answer.py",
    "image_utils.py",
    "link_utils.py",
    "branch_utils.py",
    "ladder_utils.py",
    "display_content_utils.py",
    "env_utils.py",
    "translate.py",
    "negotiation_utils.py",
    "eval_run.py"
)

Write-Host ">>> staging: $StageRoot"
Remove-IfExists $StageRoot
$null = New-Item -ItemType Directory -Force -Path $StageRoot

Copy-Item (Join-Path $RepoRoot "DELIVERY_README.md") (Join-Path $StageRoot "DELIVERY_README.md") -Force

foreach ($py in $PipelinePy) {
    $src = Join-Path $RepoRoot $py
    Require-Path $src $py
    Copy-Item $src (Join-Path $StageRoot $py) -Force
}

foreach ($f in @(
    "requirements.txt", "requirements-local.txt",
    "eval_queries.json", "eval_queries_ad5s.json", "eval_queries_tc148.json",
    ".env.example", ".gitignore"
)) {
    $src = Join-Path $RepoRoot $f
    if (Test-Path $src) { Copy-Item $src (Join-Path $StageRoot $f) -Force }
}

Require-Path (Join-Path $RepoRoot "demo") "demo/"
Copy-Tree (Join-Path $RepoRoot "demo") (Join-Path $StageRoot "demo")

# A3S: merge run-006 + run-007 → run-a3s（与 ad5s/tc148 同构）
$A3sDst = Join-Path $StageRoot "_scratch\run-a3s"
$null = New-Item -ItemType Directory -Force -Path $A3sDst
foreach ($f in @("qa_groups.json", "chunks_captioned.json")) {
    $src = Join-Path $RepoRoot "_scratch\run-006\$f"
    Require-Path $src "run-006/$f"
    Copy-Item $src (Join-Path $A3sDst $f) -Force
}
Copy-Tree (Join-Path $RepoRoot "_scratch\run-006\images") (Join-Path $A3sDst "images")
Copy-ChromaDir (Join-Path $RepoRoot "_scratch\run-007\chroma_captioned") (Join-Path $A3sDst "chroma_captioned")

# AD5S / TC148
Copy-RunData "run-ad5s" @("qa_groups.json", "chunks_captioned.json") -Chroma
Copy-RunData "run-tc148" @("qa_groups.json", "chunks_captioned.json") -Chroma -RequireImages

$leaks = @(
    (Join-Path $StageRoot ".env"),
    (Join-Path $StageRoot ".translate_cache.json"),
    (Join-Path $StageRoot ".caption_cache.json")
)
foreach ($leak in $leaks) {
    if (Test-Path $leak) { throw "refusing to pack: sensitive file: $leak" }
}

# refuse accidental bak in stage
Get-ChildItem -Path $StageRoot -Recurse -Force -ErrorAction SilentlyContinue |
    Where-Object { $_.Name -match '\.bak' -or $_.Name -match 'chroma_captioned\.bak' } |
    ForEach-Object { throw "refusing to pack backup artifact: $($_.FullName)" }

$null = New-Item -ItemType Directory -Force -Path $DistDir
if (Test-Path $OutputZip) { Remove-Item $OutputZip -Force }
Compress-Archive -Path (Join-Path $StageRoot "*") -DestinationPath $OutputZip -CompressionLevel Optimal

$sizeMb = [math]::Round((Get-Item $OutputZip).Length / 1MB, 1)
Write-Host ""
Write-Host ">>> done: $OutputZip ($sizeMb MB)"
Write-Host ">>> verify: see DELIVERY_README.md section 6"

Remove-IfExists $StageRoot
