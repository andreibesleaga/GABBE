#!/bin/bash
# setup-context.sh: Dumps project context for AI Agents

echo "# Project Context Report"
echo "Generated: $(date)"
echo ""

echo "## Directory Structure"
echo '```'
# Use git ls-files if available, otherwise find, excluding node_modules/vendor/etc
if [ -d .git ]; then
    git ls-files --exclude-standard -co | grep -vE "^(\.git|\.idea|\.vscode|node_modules|vendor|dist|build|coverage)" | tree --fromfile -L 3
else
    find . -maxdepth 3 -not -path '*/.*' -not -path './node_modules*' -not -path './vendor*' -not -path './dist*' -print | sort | sed 's/[^/]*\//  /g'
fi
echo '```'
echo ""

echo "## Key Configuration Files"
FILES=("package.json" "composer.json" "pyproject.toml" "go.mod" "Cargo.toml" "Makefile" "Dockerfile" "docker-compose.yml" ".env.example" "agents.md" "AGENTS.md" "SETUP_MISSION.md" "BOOTSTRAP_MISSION.md")

for f in "${FILES[@]}"; do
    if [ -f "$f" ]; then
        echo "### $f"
        echo '```'${f##*.}
        cat "$f"
        echo '```'
        echo ""
    fi
done

echo "## Active Task List"
if [ -f "task.md" ]; then
    echo '```markdown'
    cat "task.md"
    echo '```'
fi
