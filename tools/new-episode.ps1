<#
.SYNOPSIS
  Create a CourseStudio episode with the Episode + Motion Canvas + Reveal/Slidev layout.

.DESCRIPTION
  Creates courses/<Name>/ with 00_raw_materials, 01_research, 02_scripts,
  03_slides, 04_motion_src, 05_recording and qa. Motion Canvas is the default
  animation path and is copied from tools/motion-runtime.

  course mode keeps the Reveal.js deck (03_slides/index.html); technical,
  news and podcast keep the Slidev deck (03_slides/slides.md). The unused deck
  is removed from the new episode. Reveal assets are synced by reveal-run.ps1.

  Manim is optional: pass -WithManim to install Manim into the episode's own
  .venv via uv and create 04_manim_src. No global Python packages are installed.

  Does NOT run git init, commit, render, install Motion Canvas dependencies, or
  build Slidev.

.EXAMPLE
  powershell -NoProfile -ExecutionPolicy Bypass -File D:\CourseStudio\tools\new-episode.ps1 -Name course-attention

.EXAMPLE
  # Optional Manim fallback for strong formula/symbol scenes
  powershell -NoProfile -ExecutionPolicy Bypass -File D:\CourseStudio\tools\new-episode.ps1 -Name course-attention -WithManim

.EXAMPLE
  # Podcast: skip Python/Manim/Motion Canvas, keep research + recording package
  powershell -NoProfile -ExecutionPolicy Bypass -File D:\CourseStudio\tools\new-episode.ps1 -Name podcast-example -Mode podcast

.EXAMPLE
  # Compatibility switch: skip the Manim install (now the default)
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

    [switch]$WithManim,

    [switch]$SkipManim
)

$ErrorActionPreference = 'Stop'
$installManim = $WithManim -and -not $SkipManim -and $Mode -notin @('news', 'podcast')
$createMotion = $Mode -ne 'podcast'
$useReveal = $Mode -eq 'course'

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

    if ($createMotion) {
        $motionTemplate = Join-Path $PSScriptRoot 'motion-runtime'
        if (-not (Test-Path -LiteralPath $motionTemplate)) {
            throw "Motion runtime template not found: $motionTemplate"
        }
        $motionTarget = Join-Path $target '04_motion_src'
        New-Item -ItemType Directory -Force -Path $motionTarget | Out-Null
        Copy-Item -Path (Join-Path $motionTemplate '*') -Destination $motionTarget -Recurse -Force
    }

    # course defaults to Reveal; technical/news/podcast keep the Slidev deck.
    $revealIndex = Join-Path $target '03_slides\index.html'
    $revealAssets = Join-Path $target '03_slides\assets'
    $slidevDeck = Join-Path $target '03_slides\slides.md'
    if ($useReveal) {
        if (Test-Path -LiteralPath $slidevDeck) {
            Remove-Item -LiteralPath $slidevDeck -Force
        }
    } else {
        if (Test-Path -LiteralPath $revealIndex) {
            Remove-Item -LiteralPath $revealIndex -Force
        }
        if (Test-Path -LiteralPath $revealAssets) {
            Remove-Item -LiteralPath $revealAssets -Recurse -Force
        }
    }

    # Replace the {{EPISODE}} / {{MODE}} placeholders in text templates.
    $utf8NoBom = New-Object System.Text.UTF8Encoding($false)
    Get-ChildItem $target -Recurse -File |
        Where-Object { $_.Extension -in '.md', '.csv', '.txt', '.json', '.html' } |
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

            if ($installManim) {
                $manimScenes = Join-Path $target '04_manim_src\scenes'
                New-Item -ItemType Directory -Force -Path $manimScenes | Out-Null
                New-Item -ItemType File -Force -Path (Join-Path $manimScenes '.gitkeep') | Out-Null
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
if ($createMotion) {
    Write-Host "Motion:          $target\04_motion_src (template; replace segments.json and example scene)"
} else {
    Write-Host "Motion:          skipped (podcast mode)"
}
if ($installManim) {
    Write-Host "Manim:           $target\.venv (project-local, -WithManim)"
} elseif ($SkipManim) {
    Write-Host "Manim:           skipped (-SkipManim)"
} elseif ($Mode -in @('news', 'podcast')) {
    Write-Host "Manim:           skipped ($Mode mode)"
} else {
    Write-Host "Manim:           skipped (default; use -WithManim for Manim fallback)"
}
Write-Host "Recording:       $target\05_recording"
if ($useReveal) {
    Write-Host "Slides:          $target\03_slides\index.html (Reveal)"
} else {
    Write-Host "Slides:          $target\03_slides\slides.md (Slidev)"
}
Write-Host "Script:          $target\02_scripts\lecture_script.md"
Write-Host "Handoff:         $target\handoff.md"
Write-Host ""
Write-Host "Next:"
if ($createMotion) {
    Write-Host "  powershell -NoProfile -ExecutionPolicy Bypass -File $PSScriptRoot\motion-run.ps1 -Episode $Name -Segment example"
    Write-Host "  python $PSScriptRoot\check-episode.py $Name --mode $Mode --stage motion"
    Write-Host "  python $PSScriptRoot\check-episode.py $Name --mode $Mode --stage recording"
}
if ($useReveal) {
    Write-Host "  powershell -NoProfile -ExecutionPolicy Bypass -File $PSScriptRoot\reveal-run.ps1 -Episode $Name -Port 3040"
} elseif ($Mode -ne 'podcast') {
    Write-Host "  powershell -NoProfile -ExecutionPolicy Bypass -File $PSScriptRoot\slidev-run.ps1 -Episode $Name -Mode dev"
}
Write-Host "  python $PSScriptRoot\check-episode.py $Name --mode $Mode --stage qa --strict"
