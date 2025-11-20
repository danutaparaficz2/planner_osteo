#!/usr/bin/env zsh
set -euo pipefail
cd "${0:A:h}"

APPENV=.venv-app
if [ ! -d "$APPENV" ]; then
  echo "Creating builder venv ($APPENV)..."
  python3 -m venv "$APPENV"
fi
source "$APPENV/bin/activate"
python -m pip install --upgrade pip wheel

# Install packager and project deps for analysis
pip install pyinstaller
if [ -f requirements.txt ]; then
  echo "Installing project requirements into builder venv..."
  pip install -r requirements.txt
fi

echo "\nBuilding PlannerInputWizard.app/.binary"
pyinstaller \
  --clean --noconfirm \
  --onefile \
  --name PlannerInputWizard \
  user_input_cli.py

echo "\nBuilding PlannerAllInOne.app/.binary"
pyinstaller \
  --clean --noconfirm \
  --onefile \
  --name PlannerAllInOne \
  app_cli.py

echo "\nBuild complete. Artifacts in ./dist"
echo "Distribute binaries:"
echo "  dist/PlannerInputWizard     # input wizard only"
echo "  dist/PlannerAllInOne        # wizard + validate + scheduler + visuals"
