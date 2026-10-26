<#
.SYNOPSIS
  Render one Manim scene for an episode and copy the MP4 into 03_slides/public.

.DESCRIPTION
  Uses the episode's project-local .venv via `uv run`; never installs global
  Python packages. The render goes to 04_manim_src/media, then the final MP4
  is copied to 03_slides/public/<Name>.mp4 for Slidev.

.EXAMPLE
  powershell -NoProfile -ExecutionPolicy Bypass -File D:\CourseStudio\tools\render-manim.ps1 -Episode course-attention -Name example_name -SceneClass ExampleName

.EXAMPLE
  # Final quality
  powershell -NoProfile -ExecutionPolicy Bypass -File D:\CourseStudio\tools\render-manim.ps1 -Episode course-attention -Name example_name -Quality h
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$Episode,

    [Parameter(Mandatory = $true)]
    [ValidatePattern('^[a-zA-Z0-9][a-zA-Z0-9_-]*$')]
    [string]$Name,

    [string]$SceneClass,

    [string]$Script,

    [ValidateSet('l', 'm', 'h', 'p', 'k')]
    [string]$Quality = 'l',

    [int]$TimeoutSeconds = 180
)

$ErrorActionPreference = 'Stop'

# Keep uv's cache inside the workspace rather than the host profile.
if (-not $env:UV_CACHE_DIR) {
    $env:UV_CACHE_DIR = Join-Path (Split-Path $PSScriptRoot -Parent) '.uv-cache'
}

$root = Split-Path $PSScriptRoot -Parent
$episodeDir = Join-Path $root "courses\$Episode"
if (-not (Test-Path $episodeDir)) {
    throw "Episode not found: $episodeDir"
}

if (-not $Script) {
    $Script = "04_manim_src\scenes\$Name.py"
}
$scriptPath = Join-Path $episodeDir $Script
if (-not (Test-Path $scriptPath)) {
    throw "Scene script not found: $scriptPath"
}

if (-not $SceneClass) {
    $SceneClass = (($Name -split '[_-]') | ForEach-Object {
        if ($_.Length -gt 0) { $_.Substring(0, 1).ToUpper() + $_.Substring(1) }
    }) -join ''
}
if (-not $SceneClass) {
    throw "Could not derive SceneClass from Name; pass -SceneClass explicitly."
}

$mediaDir = Join-Path $episodeDir '04_manim_src\media'
$outDir = Join-Path $episodeDir '03_slides\public'
New-Item -ItemType Directory -Force -Path $mediaDir, $outDir | Out-Null

$uv = (Get-Command uv -ErrorAction Stop).Source
$token = [guid]::NewGuid().ToString('N')
$cmdFile = Join-Path $env:TEMP "coursestudio-manim-$token.cmd"
$logFile = Join-Path $env:TEMP "coursestudio-manim-$token.log"
$exitFile = Join-Path $env:TEMP "coursestudio-manim-$token.exit"

$argParts = @(
    "run", "manim", "-q$Quality", $Script, $SceneClass,
    "--media_dir", $mediaDir, "--output_file", $Name, "--format", "mp4"
) | ForEach-Object { '"' + ($_ -replace '"', '""') + '"' }
$argLine = $argParts -join ' '

$cmdLines = @(
    '@echo off',
    "cd /d `"$episodeDir`"",
    "call `"$uv`" $argLine > `"$logFile`" 2>&1",
    "echo %ERRORLEVEL% > `"$exitFile`""
)
Set-Content -LiteralPath $cmdFile -Value $cmdLines -Encoding ASCII

$success = $false
Push-Location $episodeDir
try {
    $proc = Start-Process -FilePath "cmd.exe" -ArgumentList @("/c", "`"$cmdFile`"") -NoNewWindow -PassThru
    if (-not $proc.WaitForExit($TimeoutSeconds * 1000)) {
        & taskkill.exe /T /F /PID $proc.Id | Out-Null
        throw "Manim render exceeded ${TimeoutSeconds}s; process tree killed. See $logFile"
    }

    if (-not (Test-Path $exitFile)) {
        throw "Manim render did not write an exit code. See $logFile"
    }
    $exitCode = [int]((Get-Content -LiteralPath $exitFile -Raw).Trim())
    if ($exitCode -ne 0) {
        $logText = if (Test-Path $logFile) { (Get-Content -LiteralPath $logFile -Tail 60 | Out-String) } else { "" }
        throw "Manim render failed (exit $exitCode).`n$logText"
    }

    $mp4 = Get-ChildItem -Path $mediaDir -Recurse -Filter "$Name.mp4" -File |
        Sort-Object LastWriteTime -Descending |
        Select-Object -First 1
    if (-not $mp4) {
        throw "Render finished but $Name.mp4 was not found under $mediaDir"
    }

    $dest = Join-Path $outDir "$Name.mp4"
    Copy-Item -LiteralPath $mp4.FullName -Destination $dest -Force
    $bytes = (Get-Item -LiteralPath $dest).Length
    if ($bytes -le 0) {
        throw "Copied MP4 is empty: $dest"
    }

    Write-Host "OUTPUT=$dest"
    Write-Host "BYTES=$bytes"
    Write-Host "STATUS=PASS_VERIFIED"
    $success = $true
}
finally {
    Pop-Location
    if ($success) {
        Remove-Item -LiteralPath $cmdFile, $logFile, $exitFile -Force -ErrorAction SilentlyContinue
    }
    else {
        Remove-Item -LiteralPath $cmdFile, $exitFile -Force -ErrorAction SilentlyContinue
        if (Test-Path $logFile) {
            Write-Host "LOG=$logFile"
            Write-Host "Render failed; log preserved for troubleshooting."
        }
    }
}
