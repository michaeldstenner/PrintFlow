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

# Automated release targets
patch:
    @just _release patch

minor:
    @just _release minor

major:
    @just _release major

# Internal release automation (use patch/minor/major instead)
_release LEVEL:
    #!/usr/bin/env bash
    set -euo pipefail
    
    echo "🚀 Starting {{LEVEL}} release automation..."
    echo
    
    # Safety checks
    if [ "$(git branch --show-current)" != "dev" ]; then
        echo "❌ ERROR: Must be on dev branch"
        echo "Run: git checkout dev"
        exit 1
    fi
    
    if ! git diff --quiet; then
        echo "❌ ERROR: Working directory not clean"
        echo "Commit your changes first"
        git status
        exit 1
    fi
    
    echo "🔍 Pre-flight checks..."
    git pull origin dev
    
    echo
    echo "🤖 STEP 1: AI Release Preparation"
    echo "============================================"
    just ai-prepare-release
    echo
    echo "👆 Please run the Claude command above to:"
    echo "   • Analyze your changes"
    echo "   • Update CHANGELOG.md" 
    echo "   • Get release recommendations"
    echo
    read -p "✅ Have you run the AI analysis and updated CHANGELOG.md? Continue? (y/N): " continue_after_ai
    if [[ ! "$continue_after_ai" =~ ^[Yy]$ ]]; then
        echo "❌ Release cancelled - run AI analysis first"
        exit 1
    fi
    
    echo "🧪 Running test suite..."
    ./scripts/runmacro.sh
    
    echo "🧹 Cleaning up whitespace..."
    sed -i '' 's/[[:space:]]*$//' PrintFlow.FCMacro docs/PrintFlowManual.md justfile local/release.md CHANGELOG.md
    
    # Show what's about to happen
    CURRENT_VERSION=$(grep "current_version" .bumpversion.toml | cut -d'"' -f2)
    echo
    echo "📋 RELEASE SUMMARY:"
    echo "   Current version: $CURRENT_VERSION"
    echo "   Release type: {{LEVEL}}"
    echo "   Branch: dev → main"
    echo "   Will create: GitHub release with auto-generated notes"
    echo
    
    read -p "🤔 Continue with {{LEVEL}} release? (y/N): " confirm
    if [[ ! "$confirm" =~ ^[Yy]$ ]]; then
        echo "❌ Release cancelled"
        exit 1
    fi
    
    echo "⚡ Executing release..."
    
    # Version bump
    bump-my-version bump {{LEVEL}}
    
    # Push changes
    git push origin dev --tags
    
    # Create and merge PR
    NEW_VERSION=$(grep "current_version" .bumpversion.toml | cut -d'"' -f2)
    echo "📝 Creating PR for v$NEW_VERSION..."
    
    gh pr create --title "Release v$NEW_VERSION" \
                 --body "Automated {{LEVEL}} release from v$CURRENT_VERSION to v$NEW_VERSION" \
                 --base main --head dev
    
    echo "🔀 Merging PR..."
    gh pr merge --merge
    
    # Switch to main and create release
    git checkout main
    git pull origin main
    
    echo "🏷️ Creating GitHub release..."
    gh release create "v$NEW_VERSION" --generate-notes
    
    # Switch back to dev
    git checkout dev
    
    echo
    echo "🎉 SUCCESS! Release v$NEW_VERSION completed"
    echo "📦 View release: https://github.com/$(gh repo view --json nameWithOwner -q .nameWithOwner)/releases/tag/v$NEW_VERSION"

# AI-assisted development targets (for manual workflow)
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
