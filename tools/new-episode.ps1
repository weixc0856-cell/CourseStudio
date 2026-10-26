<#
.SYNOPSIS
  Create a CourseStudio episode with the Episode + Slidev + Manim layout.

.DESCRIPTION
  Creates courses/<Name>/ with 00_raw_materials, 01_research, 02_scripts,
  03_slides, 04_manim_src and qa. Installs Manim into the episode's own
  .venv via uv; no global Python packages are installed.

  Does NOT run git init, commit, render, or build Slidev.

.EXAMPLE
  powershell -NoProfile -ExecutionPolicy Bypass -File D:\CourseStudio\tools\new-episode.ps1 -Name course-attention

.EXAMPLE
  # Podcast: skip Python/Manim, keep research + script
  powershell -NoProfile -ExecutionPolicy Bypass -File D:\CourseStudio\tools\new-episode.ps1 -Name podcast-example -Mode podcast

.EXAMPLE
  # Scaffold only, skip the Manim install (useful for template tests)
  powershell -NoProfile -ExecutionPolicy Bypass -File D:\CourseStudio\tools\new-episode.ps1 -Name zz-template-test -SkipManim
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory = $true, Position = 0)]
    [ValidatePattern('^[a-z0-9][a-z0-9._-]*$')]
    [string]$Name,

    [string]$CoursesRoot = 'D:\CourseStudio\courses',

    [string]$PythonVersion = '3.12',

    [ValidateSet('course', 'technical', 'news', 'podcast')]
    [string]$Mode = 'course',

    [switch]$SkipManim
)

$ErrorActionPreference = 'Stop'
$skipManim = $SkipManim -or $Mode -in @('news', 'podcast')

# Keep uv's cache inside the workspace rather than the host profile.
if (-not $env:UV_CACHE_DIR) {
    $env:UV_CACHE_DIR = Join-Path (Split-Path $PSScriptRoot -Parent) '.uv-cache'
}

function Assert-LastExit([string]$Step) {
    if ($LASTEXITCODE -ne 0) { throw "$Step failed (exit $LASTEXITCODE)" }
}

$template = Join-Path $PSScriptRoot 'episode-template'
if (-not (Test-Path $template)) {
    throw "Episode template not found: $template"
}

$target = Join-Path $CoursesRoot $Name
if (Test-Path $target) {
    throw "Episode already exists: $target"
}

$created = $false
try {
    New-Item -ItemType Directory -Force -Path $target | Out-Null
    $created = $true
    Copy-Item -Path (Join-Path $template '*') -Destination $target -Recurse -Force

    # Replace the {{EPISODE}} / {{MODE}} placeholders in text templates.
    $utf8NoBom = New-Object System.Text.UTF8Encoding($false)
    Get-ChildItem $target -Recurse -File |
        Where-Object { $_.Extension -in '.md', '.csv', '.txt' } |
        ForEach-Object {
            $text = [System.IO.File]::ReadAllText($_.FullName, [System.Text.Encoding]::UTF8)
            if ($text.Contains('{{EPISODE}}') -or $text.Contains('{{MODE}}')) {
                $text = $text.Replace('{{EPISODE}}', $Name).Replace('{{MODE}}', $Mode)
                [System.IO.File]::WriteAllText($_.FullName, $text, $utf8NoBom)
            }
        }

    Copy-Item -LiteralPath (Join-Path $PSScriptRoot 'course.gitignore') -Destination (Join-Path $target '.gitignore') -Force

    Push-Location $target
    try {
        if ($Mode -ne 'podcast') {
            uv init --bare --python $PythonVersion
            Assert-LastExit 'uv init'

            uv python pin $PythonVersion
            Assert-LastExit 'uv python pin'

            if (-not $skipManim) {
                uv add 'manim==0.22.0'
                Assert-LastExit 'uv add manim==0.22.0'
            }
        }
    }
    finally {
        Pop-Location
    }
}
catch {
    $originalError = $_
    if ($created -and (Test-Path $target)) {
        try {
            Remove-Item -LiteralPath $target -Recurse -Force -ErrorAction Stop
            Write-Warning "Rolled back incomplete episode: $target"
        }
        catch {
            Write-Warning "Rollback failed for $target : $($_.Exception.Message)"
        }
    }
    throw $originalError
}

Write-Host ""
Write-Host "Episode created: $target"
Write-Host "Mode:            $Mode"
if ($skipManim) {
    if ($Mode -in @('news', 'podcast')) {
        Write-Host "Manim:           skipped ($Mode mode)"
    } else {
        Write-Host "Manim:           skipped (-SkipManim)"
    }
} else {
    Write-Host "Manim:           $target\.venv (project-local)"
}
Write-Host "Slides:          $target\03_slides\slides.md"
Write-Host "Script:          $target\02_scripts\lecture_script.md"
Write-Host "Handoff:         $target\handoff.md"
Write-Host ""
Write-Host "Next:"
if ($Mode -ne 'podcast') {
    Write-Host "  powershell -NoProfile -ExecutionPolicy Bypass -File $PSScriptRoot\slidev-run.ps1 -Episode $Name -Mode dev"
}
Write-Host "  python $PSScriptRoot\check-episode.py $Name --mode $Mode --strict"
