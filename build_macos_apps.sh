#!/usr/bin/env bash
set -eo pipefail
cd "$(dirname "$0")"

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
  --hidden-import=validate_input \
  --hidden-import=data_loader \
  --hidden-import=models \
  user_input_cli.py

echo "\nBuilding PlannerAllInOne.app/.binary"
pyinstaller \
  --clean --noconfirm \
  --onefile \
  --name PlannerAllInOne \
  --add-data "user_input_cli.py:." \
  --add-data "validate_input.py:." \
  --add-data "main.py:." \
  --add-data "visualize_input_data.py:." \
  --add-data "visualize_schedule.py:." \
  --add-data "data_loader.py:." \
  --add-data "models.py:." \
  --add-data "scheduler.py:." \
  --hidden-import=user_input_cli \
  --hidden-import=validate_input \
  --hidden-import=main \
  --hidden-import=visualize_input_data \
  --hidden-import=visualize_schedule \
  --hidden-import=data_loader \
  --hidden-import=models \
  --hidden-import=scheduler \
  --hidden-import=json \
  --hidden-import=shutil \
  --hidden-import=random \
  --hidden-import=dataclasses \
  --hidden-import=enum \
  --hidden-import=collections \
  --hidden-import=matplotlib \
  --hidden-import=matplotlib.pyplot \
  --hidden-import=matplotlib.backends.backend_agg \
  --hidden-import=matplotlib.patches \
  --hidden-import=numpy \
  --collect-all=matplotlib \
  --collect-all=numpy \
  app_cli.py

echo "\nBuild complete. Artifacts in ./dist"
echo "Distribute binaries:"
echo "  dist/PlannerInputWizard     # input wizard only"
echo "  dist/PlannerAllInOne        # wizard + validate + scheduler + visuals"
