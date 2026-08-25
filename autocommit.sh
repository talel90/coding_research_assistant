#!/bin/bash
cd "$(dirname "$0")" || exit 1

echo "Auto-commit loop started. Checking every 20 minutes..."

while true; do
  git add -A

  if ! git diff --staged --quiet; then
    git commit -m "Auto-commit: $(date +'%Y-%m-%d %H:%M')"
    git push origin main
    echo "[$(date +'%H:%M:%S')] Committed & pushed."
  else
    echo "[$(date +'%H:%M:%S')] No changes."
  fi

  sleep 1200   # 20 minutes
done