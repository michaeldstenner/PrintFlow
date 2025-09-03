# PrintFlow project tasks

PYFILES := `find . -name "*.py" -o -name "*.FCMacro" | xargs`
MDFILES := `find . -name "*.md" | xargs`

# Run the test suite
test TESTS:
    ./scripts/runmacro.sh {{TESTS}}

# Run grip on any markdown file and open in browser
grip FILE:
    #!/usr/bin/env bash
    echo "Starting grip server for {{FILE}}..."
    grip "{{FILE}}" &
    GRIP_PID=$!
    sleep 2
    open http://localhost:6419
    echo "Grip running (PID: $GRIP_PID). Press Ctrl+C to stop."
    wait $GRIP_PID

# Run grip on the manual and open in browser
manual:
    just grip docs/PrintFlowManual.md

# Run pylint on the macro
lint:
    pylint --rcfile .pylintrc PrintFlow.FCMacro > lint.log || true
    @echo "Pylint report written to lint.log"
    
# Clean up generated files
clean:
    rm -f *.3mf *.log *.FCStd1

# Strip trailing whitespace from all files
strip-whitespace FILES:
    sed -i '' 's/[[:space:]]*$//' {{FILES}}

# Version bumping
bump-major:
    bump-my-version bump major

bump-minor:
    bump-my-version bump minor

bump-patch:
    bump-my-version bump patch

# Pre-release checks
pre-release:
    @echo "Running pre-release checks..."
    just test
    just strip-whitespace {{PYFILES}} {{MDFILES}}
    @echo "Ready for version bump!"

# Create GitHub release (run after bumping version)
release:
    #!/usr/bin/env bash
    VERSION=$(grep "current_version" .bumpversion.toml | cut -d'"' -f2)
    echo "Creating GitHub release for version $VERSION..."
    gh release create "v$VERSION" --generate-notes

# AI-assisted development targets
ai-changelog:
    @echo "🤖 Claude will analyze commit history and generate changelog..."
    @echo "Run: claude code 'analyze commits since last release and generate professional changelog'"

ai-suggest-version:
    @echo "🤖 Claude will analyze changes and suggest version bump type..."
    @echo "Run: claude code 'analyze git commits and suggest patch/minor/major version bump'"

ai-prepare-release:
    @echo "🤖 Claude will run comprehensive release preparation..."
    @echo "Run: claude code 'run pre-release checks, analyze changes, suggest version bump, and generate changelog'"

ai-review:
    @echo "🤖 Claude will review recent changes for quality and compatibility..."
    @echo "Run: claude code 'review recent commits for code quality, breaking changes, and compatibility issues'"

# Show available commands
help:
    @just --list
