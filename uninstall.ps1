# SPDX-License-Identifier: Apache-2.0
#
# GABBE uninstaller (PowerShell).
#
#   .\uninstall.ps1 [-DryRun] [-Agents claude,cursor] [-Purge] [-Dir PATH]
#
# Reverses a GABBE install from its .gabbe\manifest.json: removes exactly what was
# installed, restores any .bak backups, and never touches unrelated files.
#
# Resolution order:
#   1. `gabbe` console script on PATH  -> gabbe uninstall @args
#   2. python3 + repo checkout         -> python -m gabbe.main uninstall @args
param([Parameter(ValueFromRemainingArguments = $true)] $Args)

$ErrorActionPreference = 'Stop'

if (Get-Command gabbe -ErrorAction SilentlyContinue) {
    & gabbe uninstall @Args
} elseif (Get-Command python -ErrorAction SilentlyContinue) {
    & python -m gabbe.main uninstall @Args
} else {
    Write-Error "uninstall.ps1: need either the 'gabbe' CLI or python on PATH. Manual fallback: delete the paths listed in .gabbe\manifest.json."
    exit 2
}
