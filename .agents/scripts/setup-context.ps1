# setup-context.ps1: Dumps project context for AI Agents (Windows PowerShell)

Write-Host "# Project Context Report"
Write-Host "Generated: $(Get-Date)"
Write-Host ""

Write-Host "## Directory Structure"
Write-Host '```'

# Use Get-ChildItem (ls/dir equivalent)
# Exclude common ignore folders
$exclude = @('.git', '.idea', '.vscode', 'node_modules', 'vendor', 'dist', 'build', 'coverage', '__pycache__', '.pytest_cache')

try {
    # If git is available, use it (better for .gitignore respect)
    if (Get-Command git -ErrorAction SilentlyContinue) {
        git ls-files --exclude-standard -co | Select-String -Pattern "^(\.git|\.idea|\.vscode|node_modules|vendor|dist|build|coverage)" -NotMatch | Sort-Object
        # Note: tree-like output is harder in pure PS without external tools, simple list is safer for context context
    }
    else {
        # Fallback to Get-ChildItem
        Get-ChildItem -Recurse -Depth 3 | Where-Object { 
            $path = $_.FullName
            $skip = $false
            foreach ($ex in $exclude) {
                if ($path -match [regex]::Escape($ex)) { $skip = $true; break }
            }
            return -not $skip
        } | Select-Object -ExpandProperty FullName | ForEach-Object { $_.Replace((Get-Location).Path + "\", "") } | Sort-Object
    }
}
catch {
    Write-Host "Error listing files: $_"
}

Write-Host '```'
Write-Host ""

Write-Host "## Key Configuration Files"
$files = @("package.json", "composer.json", "pyproject.toml", "go.mod", "Cargo.toml", "Makefile", "Dockerfile", "docker-compose.yml", ".env.example", "agents.md", "AGENTS.md", "SETUP_MISSION.md", "BOOTSTRAP_MISSION.md")

foreach ($f in $files) {
    if (Test-Path $f) {
        Write-Host "### $f"
        $ext = [System.IO.Path]::GetExtension($f).TrimStart('.')
        if ($ext -eq "") { $ext = "txt" }
        Write-Host ('```' + $ext)
        Get-Content $f -Raw
        Write-Host '```'
        Write-Host ""
    }
}

Write-Host "## Active Task List"
if (Test-Path "task.md") {
    Write-Host '```markdown'
    Get-Content "task.md" -Raw
    Write-Host '```'
}
