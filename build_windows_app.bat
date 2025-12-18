@echo off
REM Windows build script for Osteopathy Planner
REM Run this on a Windows machine to create the .exe

echo Creating Python virtual environment for building...
if not exist .venv-app-win (
    python -m venv .venv-app-win
)

call .venv-app-win\Scripts\activate.bat

echo Installing build dependencies...
python -m pip install --upgrade pip wheel
pip install pyinstaller

echo Installing project requirements...
if exist requirements.txt (
    pip install -r requirements.txt
)

echo Building PlannerGUI.exe...
pyinstaller ^
  --clean --noconfirm ^
  --onefile ^
  --windowed ^
  --name PlannerGUI ^
  --add-data "image.jpeg;." ^
  --hidden-import=validate_input ^
  --hidden-import=data_loader ^
  --hidden-import=models ^
  --hidden-import=scheduler ^
  --hidden-import=visualize_schedule ^
  --hidden-import=swiss_holidays ^
  --hidden-import=PIL ^
  --hidden-import=PIL.Image ^
  --hidden-import=PIL.ImageTk ^
  --collect-all=matplotlib ^
  --collect-all=numpy ^
  --collect-all=PIL ^
  gui_input_tk.py

echo.
echo Build complete!
echo Executable location: dist\PlannerGUI.exe
echo.
echo To distribute to Windows users:
echo 1. Copy dist\PlannerGUI.exe
echo 2. Copy input_data.json
echo 3. Copy image.jpeg
echo 4. Create a folder with all three files and zip it
echo.
pause
