# SPDX-License-Identifier: Apache-2.0
#
# GABBE uninstaller (PowerShell). Run it in the project that has the kit.
#
#   .\uninstall.ps1 [-DryRun] [-Agents claude,cursor] [-Purge] [-Dir PATH] [-Help]
#
# Reverses a GABBE install from its .gabbe\manifest.json: removes exactly what was
# installed, restores the files that were backed up, and never touches unrelated files.
# -DryRun, -Agents and -Purge become --dry-run, --agents and --purge; -Dir is the project
# folder (default: the current folder). The exit status is that of the tool that ran.
#
# npx runs from a new, empty temporary folder, never from the project, and gets the project as
# `--dir <absolute path>`: the project's own .npmrc (registry, node-options) and node_modules
# then do not decide what runs. Your own user .npmrc still applies.
#
# The tool, in this order:
#   1. Node present   -> gabbe-kit uninstall (bin\install.js next to this script, else
#                        npx --yes gabbe-kit@<this release> uninstall)
#   2. Python present -> the `gabbe.exe` of `pip install gabbe`, else that package run by
#                        python without the current folder on its path (a `gabbe\` folder
#                        in the project is never imported)
#   3. neither        -> prints the manual steps

[CmdletBinding()]
param(
    [switch]$DryRun,
    [switch]$Purge,
    [string]$Agents,
    [string]$Dir,
    [switch]$Help
)

$ErrorActionPreference = 'Stop'

# The kit version this script belongs to (the release gate checks this line against
# package.json). $env:GABBE_KIT_VERSION overrides it; `latest` means the newest release.
$GabbeKitDefaultVersion = '1.1.4'

if ($Help) {
    @'
GABBE uninstaller (PowerShell). Run it in the project that has the kit.

Usage:
  .\uninstall.ps1 [-DryRun] [-Agents claude,cursor] [-Purge] [-Dir PATH] [-Help]

Removes exactly what .gabbe\manifest.json records and restores backed-up files.
Uses Node (npx gabbe-kit@<this release> uninstall --dir <project>, run from a temporary
folder) when present, else the Python CLI (gabbe), else prints the manual steps. -Dir names
the project (default: the current folder); a relative path is made absolute first.

Environment:
  GABBE_KIT_VERSION   Run that gabbe-kit version (for example 1.2.0) instead of the
                      release this script belongs to. `latest` means the newest
                      release on npm, unpinned.
'@ | Write-Output
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

$localInstaller = if ($PSScriptRoot) { Join-Path $PSScriptRoot 'bin/install.js' } else { '' }

# The project, as an absolute path: npx runs from another folder, and the Python CLI acts on the
# current folder (it is entered just before that tool runs).
$projectAbs = (Get-Location).ProviderPath
if ($Dir) {
    if (-not (Test-Path -LiteralPath $Dir -PathType Container)) {
        Write-Host "uninstall.ps1: -Dir: there is no such folder: $Dir"
        exit 2
    }
    $projectAbs = (Resolve-Path -LiteralPath $Dir).ProviderPath
}

$toolArgs = @()
if ($DryRun) { $toolArgs += '--dry-run' }
if ($Purge) { $toolArgs += '--purge' }
if ($Agents) { $toolArgs += '--agents'; $toolArgs += $Agents }

function Test-Cmd([string]$name) {
    return [bool](Get-Command $name -ErrorAction SilentlyContinue)
}

# python without the project on its import path. A gabbe\ folder in the current project
# must never be imported (it would run that project's code). Python 3.11+ has -P (no
# current folder on the path; the user site stays) and -E (no PYTHON* variables). Older
# Pythons have only -I, which also drops the user site; there the gabbe command, used
# first, covers `pip install --user`.
function Get-IsolatedPythonFlags {
    try {
        & python -E -P -c 'pass' 2>$null
        if ($LASTEXITCODE -eq 0) { return @('-E', '-P') }
    }
    catch { }
    return @('-I')
}

# The gabbe command of the Python package is gabbe.exe; the npm package's is gabbe.cmd.
function Get-GabbeCommand {
    $cmd = Get-Command 'gabbe' -CommandType Application -ErrorAction SilentlyContinue | Select-Object -First 1
    if ($cmd -and $cmd.Source -like '*.exe') { return $cmd.Source }
    return $null
}

function Test-GabbePython {
    if (Get-GabbeCommand) { return $true }
    if (-not (Test-Cmd 'python')) { return $false }
    $flags = Get-IsolatedPythonFlags
    try {
        & python @flags -c 'import gabbe' 2>$null
        return ($LASTEXITCODE -eq 0)
    }
    catch {
        return $false
    }
}

if ((Test-Cmd 'node') -and (Test-Cmd 'npx')) {
    if ($localInstaller -and (Test-Path $localInstaller)) {
        & node $localInstaller uninstall @toolArgs --dir $projectAbs
        exit $LASTEXITCODE
    }
    # npx reads the .npmrc of the folder it runs in and prefers a gabbe-kit of the same name and
    # version in that folder's node_modules. So it runs from a new empty folder, never from the
    # project, and the project is named with --dir. The version is fixed as well.
    $workDir = Join-Path ([System.IO.Path]::GetTempPath()) ('gabbe-' + [System.Guid]::NewGuid().ToString('N'))
    New-Item -ItemType Directory -Path $workDir | Out-Null
    Push-Location -LiteralPath $workDir
    try {
        & npx --yes $kitSpec uninstall @toolArgs --dir $projectAbs
        $npxExit = $LASTEXITCODE
    }
    finally {
        Pop-Location
        Remove-Item -LiteralPath $workDir -Recurse -Force -ErrorAction SilentlyContinue
    }
    exit $npxExit
}

if (Test-GabbePython) {
    Set-Location -LiteralPath $projectAbs
    $gabbeCmd = Get-GabbeCommand
    if ($gabbeCmd) {
        & $gabbeCmd uninstall @toolArgs
    }
    else {
        $flags = Get-IsolatedPythonFlags
        & python @flags -m gabbe.main uninstall @toolArgs
    }
    exit $LASTEXITCODE
}

Write-Host 'uninstall.ps1: found neither Node (npx) nor the Python CLI (pip install gabbe).'
Write-Host 'Install one, then run this again. Or remove the kit by hand:'
Write-Host '  - read .gabbe\manifest.json: it lists every path the installer wrote;'
Write-Host '  - delete those paths (agents\, .agents\skills\, the per-agent folders and links);'
Write-Host '  - take the block between GABBE-KIT:BEGIN and GABBE-KIT:END out of your own'
Write-Host '    instruction files, or restore them from <name>.gabbe-bak (or <name>.bak);'
Write-Host '  - finally delete .gabbe\ and any empty folders left.'
Write-Host 'See docs/INSTALL.md, "Uninstalling".'
exit 2
