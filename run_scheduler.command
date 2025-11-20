#!/usr/bin/env zsh
cd "${0:A:h}"
if [ ! -d .venv ]; then
  echo "Setting up environment..."
  ./setup.sh || exit 1
fi
source .venv/bin/activate
python main.py
