# SPDX-License-Identifier: Apache-2.0
#
# GABBE bootstrap installer (Windows PowerShell).
#
#   irm https://raw.githubusercontent.com/andreibesleaga/GABBE/main/install.ps1 | iex
#
# Picks the best available installer:
#   1. Node present  -> `npx --yes gabbe-kit init` (Python-independent path).
#   2. Else python   -> `python scripts/init.py` (the interactive wizard).
#
# No destructive operations: it only runs an installer that copies the kit into
# the current directory. Extra args pass through to the installer.

[CmdletBinding()]
param(
    [switch]$Help,
    [Parameter(ValueFromRemainingArguments = $true)]
    [string[]]$Args
)

$ErrorActionPreference = 'Stop'

function Show-Usage {
    @'
GABBE bootstrap installer (PowerShell)

Usage:
  .\install.ps1 [installer-args...]

Behavior:
  - If Node is installed, runs:   npx --yes gabbe-kit init [args...]
  - Else if Python is installed:  python scripts/init.py
  - Otherwise, prints how to install Node or Python and exits non-zero.

Examples:
  .\install.ps1 init --agents claude,cursor --yes
  irm https://raw.githubusercontent.com/andreibesleaga/GABBE/main/install.ps1 | iex
'@ | Write-Output
}

if ($Help -or ($Args -contains '--help') -or ($Args -contains '-h')) {
    Show-Usage
    exit 0
}

function Test-Cmd([string]$name) {
    return [bool](Get-Command $name -ErrorAction SilentlyContinue)
}

Write-Output 'GABBE installer: detecting runtime...'

$passthru = @()
if ($Args) { $passthru = $Args }

if ((Test-Cmd 'node') -and (Test-Cmd 'npx')) {
    $ver = (& node --version)
    Write-Output "-> Node detected ($ver). Using: npx --yes gabbe-kit init"
    & npx --yes gabbe-kit init @passthru
    exit $LASTEXITCODE
}

if (Test-Cmd 'npx') {
    Write-Output '-> npx detected. Using: npx --yes gabbe-kit init'
    & npx --yes gabbe-kit init @passthru
    exit $LASTEXITCODE
}

$scriptDir = if ($PSScriptRoot) { $PSScriptRoot } else { (Get-Location).Path }
$initPy = Join-Path $scriptDir 'scripts/init.py'

foreach ($py in @('python', 'python3')) {
    if (Test-Cmd $py) {
        if (Test-Path $initPy) {
            Write-Output "-> Node not found; $py detected. Using: $py $initPy"
            & $py $initPy
            exit $LASTEXITCODE
        }
        else {
            Write-Output "-> $py detected but $initPy was not found."
            Write-Output '   Run this from a GABBE checkout, or install Node and re-run.'
            exit 1
        }
    }
}

Write-Error 'Neither Node nor Python was found on PATH.'
Write-Output 'Install one of the following, then re-run install.ps1:'
Write-Output '  - Node.js >= 16   (https://nodejs.org)  then: npx gabbe-kit init'
Write-Output '  - Python >= 3.9   (https://python.org)   then: python scripts/init.py'
exit 1
