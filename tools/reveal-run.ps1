<#
.SYNOPSIS
  Sync Reveal.js assets and serve a course deck with Python's static server.

.DESCRIPTION
  Copies tools/reveal-runtime/node_modules/reveal.js/dist into
  courses/<slug>/03_slides/.vendor/reveal/ (gitignored), then serves
  03_slides with python -m http.server. No extra Node server dependency is
  installed.

  The deck is for slides only. Animation segments are recorded separately
  through 04_motion_src/record.html?segment=<name>; do not embed MP4s here.

.EXAMPLE
  powershell -NoProfile -ExecutionPolicy Bypass -File D:\CourseStudio\tools\reveal-run.ps1 -Episode course-attention
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [ValidatePattern('^[a-z0-9][a-z0-9._-]*$')]
    [string]$Episode,

    [ValidateRange(1, 65535)]
    [int]$Port = 3040,

    [string]$Root
)

$ErrorActionPreference = 'Stop'

if ($Root) {
    $root = (Resolve-Path -LiteralPath $Root).Path
} else {
    $root = Split-Path $PSScriptRoot -Parent
}

$slidesDir = Join-Path $root "courses\$Episode\03_slides"
$index = Join-Path $slidesDir 'index.html'
if (-not (Test-Path -LiteralPath $index)) {
    throw "Reveal deck not found: $index. Use mode course, or run slidev-run.ps1 for a Slidev deck."
}

$runtime = Join-Path $PSScriptRoot 'reveal-runtime'
$dist = Join-Path $runtime 'node_modules\reveal.js\dist'
if (-not (Test-Path -LiteralPath (Join-Path $dist 'reveal.js'))) {
    throw "Reveal runtime not installed: $runtime. Run: pnpm --dir `"$runtime`" install"
}

$python = Get-Command python -ErrorAction SilentlyContinue
if (-not $python) {
    throw "python not found on PATH; python -m http.server is required."
}

$vendor = Join-Path $slidesDir '.vendor\reveal'
if (Test-Path -LiteralPath $vendor) {
    Remove-Item -LiteralPath $vendor -Recurse -Force
}
New-Item -ItemType Directory -Force -Path $vendor | Out-Null
Copy-Item -Path (Join-Path $dist '*') -Destination $vendor -Recurse -Force

$url = "http://127.0.0.1:$Port/index.html"
Write-Host ""
Write-Host "Reveal assets synced: $vendor"
Write-Host "Deck URL:   $url"
Write-Host "Fullscreen: open the URL in Chrome, press F11, and wait 2 seconds for the fullscreen bubble."
Write-Host "Slides only: animation segments are recorded separately via record.html?segment=<name>."
Write-Host "Do not embed MP4s in this deck."
Write-Host ""

& python -m http.server $Port --bind 127.0.0.1 --directory $slidesDir
exit $LASTEXITCODE
