#!/bin/bash

# Stop if a command fails
set -e

# Move to the directory where this script is located
cd "$(dirname "$0")" || exit 1

echo "=========================================="
echo " Git Auto-Commit Started"
echo " Checking every 30 minutes"
echo "=========================================="

while true; do

    echo ""
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] Checking for changes..."

    # Stage all changes
    git add -A

    # Check if there are staged changes
    if ! git diff --cached --quiet; then

        echo "Changes detected."

        # Create commit
        git commit -m "Auto-commit: $(date +'%Y-%m-%d %H:%M')"

        # Push to GitHub
        git push origin main

        echo "[$(date +'%H:%M:%S')] Changes committed and pushed successfully."

    else

        echo "[$(date +'%H:%M:%S')] No changes. Nothing to commit."

    fi

    echo "Next check in 60 minutes..."

    # Wait 60 minutes
    sleep 1800

done