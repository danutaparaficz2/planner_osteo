#!/usr/bin/env zsh
set -euo pipefail

# Always run from this script's folder
cd "$(dirname "$0")"

APP="./dist/PlannerAllInOne"

# Build if binary missing
if [[ ! -x "$APP" ]]; then
  echo "PlannerAllInOne binary not found. Building..."
  chmod +x build_macos_apps.sh || true
  zsh ./build_macos_apps.sh
fi

# Remove quarantine bit if present (local builds sometimes get it)
if command -v xattr >/dev/null 2>&1; then
  if xattr -p com.apple.quarantine "$APP" >/dev/null 2>&1; then
    echo "Removing macOS quarantine from binary..."
    xattr -d com.apple.quarantine "$APP" || true
  fi
fi

# Run the app
if [[ -x "$APP" ]]; then
  echo "Launching PlannerAllInOne..."
  exec "$APP"
else
  echo "Error: PlannerAllInOne binary not found after build." >&2
  exit 1
fi
