#!/bin/bash

#!/bin/bash
# APEX Sales Intelligence - Full Repository Sync & Overwrite
# Purpose: Pull latest GitHub state and overwrite local repo completely
# Date: 2025-12-14

set -e  # Exit on error

PROJECT_DIR="/Users/chrisrabenold/projects/apex/apex-sales-intelligence"
GITHUB_REMOTE="origin"
GITHUB_BRANCH="main"  # Change to your default branch if different

echo "=========================================="
echo "APEX Sales Intelligence - Full Git Sync"
echo "=========================================="
echo "Project: $PROJECT_DIR"
echo "Remote: $GITHUB_REMOTE"
echo "Branch: $GITHUB_BRANCH"
echo ""

# Step 1: Validate repo exists
if [ ! -d "$PROJECT_DIR/.git" ]; then
	echo "❌ ERROR: Not a git repository at $PROJECT_DIR"
	exit 1
fi

cd "$PROJECT_DIR"
echo "✓ Navigated to project directory"
echo ""

# Step 2: Backup current state (optional but recommended)
BACKUP_DIR="$PROJECT_DIR/.backup-$(date +%Y%m%d-%H%M%S)"
echo "Creating backup of current state..."
mkdir -p "$BACKUP_DIR"
cp -r "$PROJECT_DIR"/* "$BACKUP_DIR/" 2>/dev/null || true
echo "✓ Backup created at: $BACKUP_DIR"
echo ""

# Step 3: Fetch latest from GitHub
echo "Fetching latest from GitHub..."
git fetch "$GITHUB_REMOTE" "$GITHUB_BRANCH" --prune
echo "✓ Fetch complete"
echo ""

# Step 4: Hard reset to remote state (OVERWRITES local changes)
echo "⚠️  Hard resetting to remote state (this will overwrite local changes)..."
git reset --hard "$GITHUB_REMOTE/$GITHUB_BRANCH"
echo "✓ Hard reset complete"
echo ""

# Step 5: Clean untracked files (optional - uncomment if you want to remove local-only files)
# echo "Cleaning untracked files..."
# git clean -fd
# echo "✓ Cleanup complete"
# echo ""

# Step 6: Update submodules if present
echo "Checking for submodules..."
if grep -q "\[submodule" .gitmodules 2>/dev/null; then
	echo "Updating submodules..."
	git submodule update --init --recursive
	echo "✓ Submodules updated"
else
	echo "✓ No submodules detected"
fi
echo ""

# Step 7: Verify final state
CURRENT_COMMIT=$(git rev-parse HEAD)
CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD)
UPSTREAM_COMMIT=$(git rev-parse "$GITHUB_REMOTE/$GITHUB_BRANCH")

echo "=========================================="
echo "Sync Complete ✓"
echo "=========================================="
echo "Current branch: $CURRENT_BRANCH"
echo "Local HEAD: $CURRENT_COMMIT"
echo "Remote HEAD: $UPSTREAM_COMMIT"
echo ""

if [ "$CURRENT_COMMIT" = "$UPSTREAM_COMMIT" ]; then
	echo "✓ Local repository is in sync with GitHub"
else
	echo "⚠️  Commits differ (may indicate detached state or branch mismatch)"
fi

echo ""
echo "Backup location: $BACKUP_DIR"
echo "To restore backup: cp -r $BACKUP_DIR/* $PROJECT_DIR/"
echo ""
echo "Next steps:"
echo "1. Review changes: git log --oneline -10"
echo "2. Install dependencies: pip install -r requirements.txt (if Python)"
echo "3. Test build/deployment as needed"
echo ""
echo "=========================================="
