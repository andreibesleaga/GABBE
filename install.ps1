# SPDX-License-Identifier: Apache-2.0
#
# GABBE bootstrap installer (Windows PowerShell).
#
#   irm https://raw.githubusercontent.com/andreibesleaga/GABBE/main/install.ps1 | iex
#   .\install.ps1 [-Agents claude,cursor] [-Yes] [-Force] [-Help]
#
# Picks the best available installer:
#   1. Node present  -> `npx --yes gabbe-kit@<this release> init` (Python-independent path).
#   2. Else python   -> `python scripts/init.py` (the interactive wizard), only from a
#                       GABBE checkout: run the script from a file, not piped.
#
# No destructive operations: it only runs an installer that copies the kit into the
# current directory. -Agents, -Yes and -Force become --agents, --yes and --force; any other
# argument is passed on as it is (for example: .\install.ps1 init --agents claude --yes).

[CmdletBinding()]
param(
    [switch]$Help,
    [switch]$Force,
    [switch]$Yes,
    [string]$Agents,
    [Parameter(ValueFromRemainingArguments = $true)]
    [string[]]$InstallerArgs
)

$ErrorActionPreference = 'Stop'

# The kit version this script belongs to (the release gate checks this line against
# package.json). $env:GABBE_KIT_VERSION overrides it; `latest` means the newest release.
$GabbeKitDefaultVersion = '1.1.4'

function Show-Usage {
    @'
GABBE bootstrap installer (PowerShell)

Usage:
  .\install.ps1 [-Agents claude,cursor] [-Yes] [-Force] [-Help] [installer-args...]

Behavior:
  - If Node is installed, runs:   npx --yes gabbe-kit@<this release> init [args...]
  - Else if Python is installed and this script is run from a GABBE checkout:
                                  python scripts/init.py [--force] [--hooks]
    (the wizard has only --force and --hooks; other arguments are ignored and listed)
  - Otherwise, prints how to install Node or Python and exits non-zero.

Environment:
  GABBE_KIT_VERSION   Install that exact gabbe-kit version (for example 1.2.0) instead of
                      the release this script belongs to. `latest` means the newest
                      release on npm, unpinned.

Examples:
  .\install.ps1 -Agents claude,cursor -Yes
  irm https://raw.githubusercontent.com/andreibesleaga/GABBE/main/install.ps1 | iex
'@ | Write-Output
}

function Test-Cmd([string]$name) {
    return [bool](Get-Command $name -ErrorAction SilentlyContinue)
}

# Arguments for the installer: a leading `init` is dropped (it is the default command).
$rest = @($InstallerArgs | Where-Object { $_ })
if ($rest.Count -gt 0 -and $rest[0] -eq 'init') {
    if ($rest.Count -gt 1) { $rest = @($rest[1..($rest.Count - 1)]) } else { $rest = @() }
}

if ($Help -or ($rest -contains '--help') -or ($rest -contains '-h')) {
    Show-Usage
    exit 0
}

# The npm package spec: the release this script belongs to, unless GABBE_KIT_VERSION says
# otherwise. Only a plain version (1.2.0, 1.2.0-rc.1) or `latest` is accepted, so the value
# cannot add anything to the command.
$kitVersion = if ($env:GABBE_KIT_VERSION) { $env:GABBE_KIT_VERSION } else { $GabbeKitDefaultVersion }
$kitSpec = 'gabbe-kit'
if ($kitVersion -ne 'latest') {
    if ($kitVersion -notmatch '^[0-9]+\.[0-9]+\.[0-9]+(-[0-9A-Za-z]+(\.[0-9A-Za-z]+)*)?$') {
        Write-Host 'Error: GABBE_KIT_VERSION must be a version such as 1.2.0, or latest.'
        exit 1
    }
    $kitSpec = "gabbe-kit@$kitVersion"
}

$toolArgs = @()
if ($Force) { $toolArgs += '--force' }
if ($Yes) { $toolArgs += '--yes' }
if ($Agents) { $toolArgs += '--agents'; $toolArgs += $Agents }
$toolArgs += $rest

Write-Output 'GABBE installer: detecting runtime...'

if (Test-Cmd 'npx') {
    Write-Output "-> Node (npx) detected. Using: npx --yes $kitSpec init"
    # npx prefers a gabbe-kit of the same name and version found in the project's own
    # node_modules; that is why the version is fixed.
    & npx --yes $kitSpec init @toolArgs
    exit $LASTEXITCODE
}

foreach ($py in @('python', 'python3')) {
    if (-not (Test-Cmd $py)) { continue }
    $initPy = if ($PSScriptRoot) { Join-Path $PSScriptRoot 'scripts/init.py' } else { '' }
    if (-not $initPy -or -not (Test-Path $initPy)) {
        Write-Host 'Python was found but Node was not, and there is no GABBE checkout here'
        Write-Host '(this script was piped, or scripts/init.py is not next to it).'
        Write-Host 'Install Node.js >= 16 and re-run, or clone the repository and run:'
        Write-Host '  git clone https://github.com/andreibesleaga/GABBE; python GABBE/scripts/init.py'
        exit 1
    }
    if ([Console]::IsInputRedirected) {
        Write-Host 'The Python wizard asks questions and needs a terminal; input is redirected.'
        Write-Host 'Install Node.js >= 16 for an install without questions: npx gabbe-kit init --yes'
        exit 1
    }
    $ignored = @($toolArgs | Where-Object { $_ -ne '--force' -and $_ -ne '--hooks' })
    if ($ignored.Count -gt 0) {
        Write-Host ("! The wizard does not take these arguments; ignored: " + ($ignored -join ' '))
    }
    $wizardArgs = @()
    if ($Force -or ($toolArgs -contains '--force')) { $wizardArgs += '--force' }
    if ($toolArgs -contains '--hooks') { $wizardArgs += '--hooks' }
    Write-Output "-> Node not found; $py detected. Using: $py $initPy"
    & $py $initPy @wizardArgs
    exit $LASTEXITCODE
}

Write-Host 'Neither Node nor Python was found on PATH.'
Write-Host 'Install one of the following, then re-run install.ps1:'
Write-Host '  - Node.js >= 16   (https://nodejs.org)  then: npx gabbe-kit init'
Write-Host '  - Python >= 3.9   (https://python.org)   then: python scripts/init.py'
exit 1
