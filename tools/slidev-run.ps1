<#
.SYNOPSIS
  Run Slidev from the shared project-local runtime against an episode.
.DESCRIPTION
  Uses D:\CourseStudio\tools\slidev-runtime\node_modules. Does not install
  anything globally and does not create per-episode node_modules.

.EXAMPLE
  powershell -NoProfile -ExecutionPolicy Bypass -File D:\CourseStudio\tools\slidev-run.ps1 -Episode course-attention -Mode dev

.EXAMPLE
  powershell -NoProfile -ExecutionPolicy Bypass -File D:\CourseStudio\tools\slidev-run.ps1 -Episode course-attention -Mode build
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$Episode,

    [ValidateSet('dev', 'build')]
    [string]$Mode = 'dev',

    [int]$Port = 3030,

    [switch]$Open,

    [string]$Out
)

$ErrorActionPreference = 'Stop'

$root = Split-Path $PSScriptRoot -Parent
$episodeDir = Join-Path $root "courses\$Episode"
$slides = Join-Path $episodeDir '03_slides\slides.md'
$runtime = Join-Path $PSScriptRoot 'slidev-runtime'

if (-not (Test-Path $slides)) {
    throw "slides.md not found: $slides"
}
if (-not (Test-Path (Join-Path $runtime 'node_modules'))) {
    throw "Slidev runtime not installed: $runtime. Run: pnpm --dir `"$runtime`" install"
}

if ($Mode -eq 'dev') {
    $pnpmArgs = @('--dir', $runtime, 'exec', 'slidev', $slides, '--port', "$Port")
    if ($Open) { $pnpmArgs += '--open' }
    & pnpm @pnpmArgs
    exit $LASTEXITCODE
}

if (-not $Out) {
    $Out = Join-Path $episodeDir '03_slides\dist'
}
& pnpm --dir $runtime exec slidev build $slides --out $Out
if ($LASTEXITCODE -ne 0) {
    throw "Slidev build failed (exit $LASTEXITCODE)"
}

$index = Join-Path $Out 'index.html'
if (-not (Test-Path $index)) {
    throw "Slidev build finished but index.html was not found: $index"
}
Write-Host "Slidev build OK: $Out"
