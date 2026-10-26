<#
.SYNOPSIS
  Create an isolated course project: its own uv project, .venv, and locked ManimCE.

.DESCRIPTION
  Every course gets an independent virtual environment. Manim is installed only
  into that course's .venv; there is no shared or global manim install.

.EXAMPLE
  powershell -NoProfile -ExecutionPolicy Bypass -File D:\CourseStudio\tools\new-course.ps1 -Name ai-intro
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory = $true, Position = 0)]
    [ValidatePattern('^[a-z0-9][a-z0-9._-]*$')]
    [string]$Name,

    [string]$CoursesRoot = 'D:\CourseStudio\courses',

    [string]$PythonVersion = '3.12'
)

$ErrorActionPreference = 'Stop'

function Assert-LastExit([string]$Step) {
    if ($LASTEXITCODE -ne 0) { throw "$Step failed (exit $LASTEXITCODE)" }
}

$target = Join-Path $CoursesRoot $Name
if (Test-Path (Join-Path $target 'pyproject.toml')) {
    throw "Course project already initialized: $target"
}

New-Item -ItemType Directory -Force -Path $target | Out-Null
Push-Location $target
try {
    if (-not (Test-Path 'pyproject.toml')) {
        uv init --python $PythonVersion
        Assert-LastExit 'uv init'
    }
    if (Test-Path 'main.py') { Remove-Item 'main.py' -Force }

    # Install the shared ignore rules (kept beside this script).
    $ignoreTemplate = Join-Path $PSScriptRoot 'course.gitignore'
    if (Test-Path $ignoreTemplate) {
        Copy-Item -LiteralPath $ignoreTemplate -Destination (Join-Path $target '.gitignore') -Force
    }

    uv add manim
    Assert-LastExit 'uv add manim'

    New-Item -ItemType Directory -Force -Path 'animations\manim', 'animations\rendered' | Out-Null

    # Keep renders out of the course root and inside the documented layout.
    $manimCfg = Join-Path $target 'manim.cfg'
    if (-not (Test-Path $manimCfg)) {
        @'
[CLI]
media_dir = animations/rendered
'@ | Out-File -FilePath $manimCfg -Encoding ascii
    }
}
finally {
    Pop-Location
}

Write-Host "Course project created: $target"
Write-Host "Virtual environment:  $target\.venv"
Write-Host "Manim output:         $target\animations\rendered"
Write-Host "Verify with:          cd `"$target`"; uv run manim checkhealth"
