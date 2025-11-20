#!/usr/bin/env zsh
set -e
cd "${0:A:h}"

# Create venv and install deps (visualization optional)
if [ ! -d .venv ]; then
  echo "Creating Python virtual environment (.venv)..."
  python3 -m venv .venv
fi

source .venv/bin/activate
python -m pip install --upgrade pip wheel
if [ -f requirements.txt ]; then
  echo "Installing requirements..."
  pip install -r requirements.txt
fi

echo "\nSetup complete. Useful commands:"
echo "  source .venv/bin/activate" 
echo "  python user_input_cli.py        # open the input wizard"
echo "  python validate_input.py        # validate input_data.json"
echo "  python main.py                  # run scheduler"
echo "  python visualize_input_data.py  # optional visuals"
echo "  python visualize_schedule.py    # optional visuals"
