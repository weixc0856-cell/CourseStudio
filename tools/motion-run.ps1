<#
.SYNOPSIS
  Start a Motion Canvas recording page for one segment.

.DESCRIPTION
  Each core concept is a single-scene Motion Canvas project. This runner
  scaffolds courses/<slug>/04_motion_src from tools/motion-runtime when the
  directory is missing, installs the pinned dependencies inside that course
  directory when needed, selects the segment through MC_SEGMENT, and starts
  Vite.

  It prints the record.html URL, not ?present. Phase 0 proved that ?present
  keeps the SLIDES panel and playback controls visible in fullscreen and is
  therefore preview-only.

.EXAMPLE
  powershell -NoProfile -ExecutionPolicy Bypass -File D:\CourseStudio\tools\motion-run.ps1 `
    -Episode course-attention -Segment attention_scores

.EXAMPLE
  # Use a temporary root for template tests
  powershell -NoProfile -ExecutionPolicy Bypass -File D:\CourseStudio\tools\motion-run.ps1 `
    -Episode zz-motion-test -Segment example -Root C:\temp\motion-run-test
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [ValidatePattern('^[a-z0-9][a-z0-9._-]*$')]
    [string]$Episode,

    [Parameter(Mandatory = $true)]
    [ValidatePattern('^[a-z0-9][a-z0-9_-]*$')]
    [string]$Segment,

    [ValidateRange(1, 65535)]
    [int]$Port = 9100,

    [string]$Root
)

$ErrorActionPreference = 'Stop'

function Assert-LastExit([string]$Step) {
    if ($LASTEXITCODE -ne 0) { throw "$Step failed (exit $LASTEXITCODE)" }
}

if ($Root) {
    $root = (Resolve-Path -LiteralPath $Root).Path
} else {
    $root = Split-Path $PSScriptRoot -Parent
}

$episodeDir = Join-Path $root "courses\$Episode"
if (-not (Test-Path -LiteralPath $episodeDir)) {
    throw "Episode not found: $episodeDir"
}

$motionDir = Join-Path $episodeDir '04_motion_src'
$template = Join-Path $PSScriptRoot 'motion-runtime'

if (-not (Test-Path -LiteralPath $motionDir)) {
    if (-not (Test-Path -LiteralPath $template)) {
        throw "Motion runtime template not found: $template"
    }
    New-Item -ItemType Directory -Force -Path $motionDir | Out-Null
    Copy-Item -Path (Join-Path $template '*') -Destination $motionDir -Recurse -Force
    Write-Host "Scaffolded: $motionDir (from tools/motion-runtime)"
}

foreach ($required in @('package.json', 'pnpm-lock.yaml', 'vite.config.ts', 'record.html', 'segments.json')) {
    $path = Join-Path $motionDir $required
    if (-not (Test-Path -LiteralPath $path)) {
        throw "Missing $required in $motionDir. Copy tools/motion-runtime into 04_motion_src, or add the file manually."
    }
}

$projectFile = Join-Path $motionDir "src\projects\$Segment.ts"
$sceneFile = Join-Path $motionDir "src\scenes\$Segment.tsx"
if (-not (Test-Path -LiteralPath $projectFile)) {
    $projects = Get-ChildItem -LiteralPath (Join-Path $motionDir 'src\projects') -Filter '*.ts' -ErrorAction SilentlyContinue |
        Select-Object -ExpandProperty BaseName
    throw "Project not found: $projectFile. Available: $($projects -join ', ')"
}
if (-not (Test-Path -LiteralPath $sceneFile)) {
    throw "Scene not found: $sceneFile"
}

$pnpm = Get-Command pnpm -ErrorAction SilentlyContinue
if (-not $pnpm) {
    throw "pnpm not found on PATH. Motion Canvas dependencies are installed inside the course directory only."
}

if (-not (Test-Path -LiteralPath (Join-Path $motionDir 'node_modules'))) {
    Write-Host "Installing Motion Canvas dependencies in $motionDir ..."
    & pnpm --dir $motionDir install --frozen-lockfile
    Assert-LastExit 'pnpm install --frozen-lockfile'
}

$env:MC_SEGMENT = $Segment
$env:MC_PORT = "$Port"

$url = "http://localhost:$Port/record.html?segment=$Segment"
Write-Host ""
Write-Host "Recording URL: $url"
Write-Host "Segment:       $Segment"
Write-Host "Port:          $Port"
Write-Host ""
Write-Host "Before recording:"
Write-Host "  1. Open the URL in Chrome and enter fullscreen."
Write-Host "  2. Wait 2 seconds for Chrome's fullscreen bubble to disappear."
Write-Host "  3. Start OBS, then reload the page to start the segment from frame 0."
Write-Host ""
Write-Host "OBS capture:"
Write-Host "  - Use Display Capture or Window Capture (Windows Graphics Capture)."
Write-Host "  - Do NOT use BitBlt / GDI window capture; Chrome renders black."
Write-Host "  - Keep the OBS canvas at 1920x1080 and scale the source."
Write-Host "  - At 4K + 150% scaling, 1920x1080 CSS is 2880x1620 physical pixels."
Write-Host "  - OBS is manual. This script does not launch or automate OBS."
Write-Host ""

Push-Location $motionDir
try {
    & pnpm exec vite
} finally {
    Pop-Location
}

exit $LASTEXITCODE
