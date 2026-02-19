<#
.SYNOPSIS
    GABBE Agentic Kit - Context Setup Script (PowerShell)
.DESCRIPTION
    Wires up the .agents/ directory to various AI coding tools on Windows.
    Creates necessary symlinks (or copies if non-admin) and initializes memory.
.NOTES
    Usage: .\setup-context.ps1
#>

$ErrorActionPreference = "Stop"

# --- Configuration ---
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$AgentsDir = Resolve-Path "$ScriptDir\.."
$ProjectRoot = Resolve-Path "$AgentsDir\.."

# Colors for Output
function Write-Green($text) { Write-Host $text -ForegroundColor Green }
function Write-Yellow($text) { Write-Host $text -ForegroundColor Yellow }
function Write-Blue($text) { Write-Host $text -ForegroundColor Cyan }
function Write-Red($text) { Write-Host $text -ForegroundColor Red }

# Helper: Create Symlink with Fallback
function New-SymlinkOrCopy {
    param (
        [string]$SourcePath,
        [string]$TargetPath,
        [bool]$IsDirectory = $false
    )

    $Source = $SourcePath
    $Target = $TargetPath

    # Remove existing target if it exists
    if (Test-Path $Target) {
        if ((Get-Item $Target).Target -ne $null) {
            # It's a symlink/junction, safe to remove
            Remove-Item $Target -Force -Recurse -ErrorAction SilentlyContinue
        } else {
            # It's a real file/dir, backup first
            Write-Yellow "! Backing up existing $Target to $Target.bak"
            Move-Item $Target "$Target.bak" -Force
        }
    }

    # Ensure parent dir exists
    $ParentDir = Split-Path $Target -Parent
    if (-not (Test-Path $ParentDir)) {
        New-Item -ItemType Directory -Path $ParentDir -Force | Out-Null
    }

    try {
        # Try Creating Symlink (Requires Admin usually, or Dev Mode)
        New-Item -ItemType SymbolicLink -Path $Target -Target $Source -Force | Out-Null
        Write-Green "✓ Linked $(Split-Path $Target -Leaf) -> $Source"
    }
    catch {
        Write-Yellow "! Symlink failed (requires Admin or Dev Mode). Falling back to Copy..."
        try {
            if ($IsDirectory) {
                Copy-Item -Path $Source -Destination $Target -Recurse -Force
            } else {
                Copy-Item -Path $Source -Destination $Target -Force
            }
            Write-Green "✓ Copied $(Split-Path $Target -Leaf) (Fallback)"
        }
        catch {
            Write-Red "x Failed to copy: $_"
        }
    }
}

Write-Host ""
Write-Blue "======================================"
Write-Blue "  Agentic Engineering Kit — Setup     "
Write-Blue "======================================"
Write-Host ""

# -----------------------------------------------------------------------------
# Step 1: Unifying Context (AGENTS.md -> Tools)
# -----------------------------------------------------------------------------
Write-Yellow "Step 1: Unifying agent context (AGENTS.md -> all tools)"

# Paths
$AgentsMd = "$AgentsDir\AGENTS.md"

# Claude
New-SymlinkOrCopy -SourcePath $AgentsMd -TargetPath "$ProjectRoot\.claude\CLAUDE.md"

# Cursor
New-SymlinkOrCopy -SourcePath $AgentsMd -TargetPath "$ProjectRoot\.cursorrules"

# Gemini / Antigravity
if (-not (Test-Path "$ProjectRoot\.gemini")) { New-Item -ItemType Directory -Path "$ProjectRoot\.gemini" | Out-Null }
if (-not (Test-Path "$ProjectRoot\.gemini\settings.json")) {
    $SettingsJson = @{
        agent_instructions_file = "..\.agents\AGENTS.md"
        skills_directory = "..\.agents\skills\"
        notes = "Managed by .agents\setup-context.ps1"
    } | ConvertTo-Json -Depth 2
    Set-Content -Path "$ProjectRoot\.gemini\settings.json" -Value $SettingsJson
    Write-Green "✓ .gemini\settings.json created"
} else {
    Write-Yellow "! .gemini\settings.json already exists (skipped)"
}

# GitHub Copilot
New-SymlinkOrCopy -SourcePath $AgentsMd -TargetPath "$ProjectRoot\.github\copilot-instructions.md"

Write-Host ""

# -----------------------------------------------------------------------------
# Step 2: Wiring Skills
# -----------------------------------------------------------------------------
Write-Yellow "Step 2: Wiring skills directories"

$SkillsDir = "$AgentsDir\skills"

# Claude Skills
New-SymlinkOrCopy -SourcePath $SkillsDir -TargetPath "$ProjectRoot\.claude\skills" -IsDirectory $true

# Agent Skills (Gemini)
New-SymlinkOrCopy -SourcePath $SkillsDir -TargetPath "$ProjectRoot\.agent\skills" -IsDirectory $true

# Cursor & VS Code (Compile)
$CompileScript = "$AgentsDir\scripts\compile_skills.py"
if (Test-Path $CompileScript) {
    Write-Yellow "Compiling skills for Cursor and VS Code..."
    
    # Check for Python
    try {
        python --version | Out-Null
        
        # Cursor
        python "$CompileScript" --platform "Cursor" --skills-dir "$SkillsDir" --target-dir "$ProjectRoot\.cursor\rules" --project-root "$ProjectRoot"
        
        # VS Code
        python "$CompileScript" --platform "VS Code" --skills-dir "$SkillsDir" --target-dir "$ProjectRoot\.github\skills" --project-root "$ProjectRoot"
    }
    catch {
        Write-Red "x Python not found or error running compile_skills.py. Skipping compilation."
    }
} else {
    Write-Red "x compile_skills.py not found at $CompileScript"
}

Write-Host ""

# -----------------------------------------------------------------------------
# Step 3: Initialize Memory
# -----------------------------------------------------------------------------
Write-Yellow "Step 3: Initializing loki\memory structure"

$MemoryDir = "$AgentsDir\loki\memory"
New-Item -ItemType Directory -Path "$MemoryDir\episodic\SESSION_SNAPSHOT" -Force | Out-Null
New-Item -ItemType Directory -Path "$MemoryDir\semantic" -Force | Out-Null
Write-Green "✓ loki\memory structure created"

Write-Host ""

# -----------------------------------------------------------------------------
# Step 4: Initialize Memory Files
# -----------------------------------------------------------------------------
Write-Yellow "Step 4: Initializing memory files"

# We use the existing logic to check if they exist, but creating them in PS is verbose.
# Ideally these should be templates copied from .agents\templates\ if possible,
# or we just write short placeholders like the bash script.

function Create-MemoryFile($FileName, $Content) {
    $Path = "$MemoryDir\$FileName"
    if (-not (Test-Path $Path)) {
        Set-Content -Path $Path -Value $Content -Encoding UTF8
        Write-Green "✓ Created $FileName"
    } else {
        Write-Yellow "! $FileName already exists (skipped)"
    }
}

$ProjectStateContent = @"
# PROJECT_STATE.md — Master Project State
> Updated by: sdlc-checkpoint.skill

## Current SDLC Phase
Phase: S00_INITIALIZED
Status: NOT_STARTED

## Next Actions
1. Fill in AGENTS.md
2. Run spec-writer.skill
"@

Create-MemoryFile "PROJECT_STATE.md" $ProjectStateContent

$AuditLogContent = @"
# AUDIT_LOG.md — Project Audit Trail
> APPEND ONLY. Updated by: audit-trail.skill

| Timestamp | Session | Agent/Human | Action Type | Description | Outcome |
|---|---|---|---|---|---|
| INIT | S00 | setup-context.ps1 | PHASE_TRANSITION | Kit initialized | SUCCESS |
"@

Create-MemoryFile "AUDIT_LOG.md" $AuditLogContent

$ContinuityContent = @"
# CONTINUITY.md — Project Memory: Past Failures & Lessons
> Read at START of reason phase.

## Past Failures & Lessons
_No entries yet._
"@

Create-MemoryFile "CONTINUITY.md" $ContinuityContent

Write-Host ""

# -----------------------------------------------------------------------------
# Step 5: Update .gitignore
# -----------------------------------------------------------------------------
Write-Yellow "Step 5: Updating .gitignore"

$GitIgnore = "$ProjectRoot\.gitignore"
if (-not (Test-Path $GitIgnore)) {    New-Item -ItemType File -Path $GitIgnore | Out-Null }

$CurrentIgnore = Get-Content $GitIgnore -Raw -ErrorAction SilentlyContinue
$AppendContent = ""

if ($CurrentIgnore -notmatch "\.env") { $AppendContent += "`n.env`n" }
if ($CurrentIgnore -notmatch "\.env\.local") { $AppendContent += ".env.local`n" }
if ($CurrentIgnore -notmatch "\.env\.*\.local") { $AppendContent += ".env.*.local`n" }

if ($AppendContent -ne "") {
    Add-Content -Path $GitIgnore -Value $AppendContent
    Write-Green "✓ Updated .gitignore"
} else {
    Write-Yellow "! .gitignore already up to date"
}

Write-Host ""
Write-Green "======================================"
Write-Green "  Context Unification Complete!       "
Write-Green "======================================"
Write-Host "Kit is ready. Next steps:"
Write-Host "  1. Fill in AGENTS.md placeholders"
Write-Host "  2. Tell your AI: 'Read AGENTS.md and start with spec-writer skill'"
