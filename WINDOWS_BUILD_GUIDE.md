# Building for Windows Users

## Option 1: Build on Windows Machine (Recommended)

### You'll need access to a Windows computer:

1. **Copy your project to Windows**:
   - Transfer the entire `planner_osteo` folder to a Windows computer
   - Via USB drive, cloud storage, or network share

2. **Install Python on Windows** (if not already installed):
   - Download from https://www.python.org/downloads/
   - During installation, CHECK "Add Python to PATH"

3. **Build the Windows executable**:
   ```cmd
   cd path\to\planner_osteo
   build_windows_app.bat
   ```

4. **Find your executable**:
   - Located at: `dist\PlannerGUI.exe`
   - This is a standalone .exe that works on any Windows 10/11 machine

5. **Package for distribution**:
   ```
   WindowsPlanner\
   ├── PlannerGUI.exe       # The standalone app
   ├── input_data.json      # Starting data
   ├── image.jpeg           # Summary image
   └── README.txt           # Instructions
   ```

---

## Option 2: Use GitHub Actions (Build from Mac)

If you don't have access to Windows, I can set up automatic builds using GitHub Actions:

1. Push your code to GitHub
2. GitHub Actions will build both Mac and Windows versions
3. Download the Windows .exe from the Actions artifacts

Would you like me to create the GitHub Actions workflow?

---

## Option 3: Cloud Windows VM

Use a cloud service to access Windows temporarily:
- **AWS EC2** (Windows Server, free tier available)
- **Azure Virtual Machines** (Windows, free trial)
- **Paperspace** (Windows VMs, pay-as-you-go)

Steps:
1. Launch Windows VM
2. Copy project files
3. Run build script
4. Download the .exe

---

## Distribution to Windows Client

### Package structure:
```
OsteopathyPlanner-Windows/
├── PlannerGUI.exe
├── input_data.json
├── image.jpeg
└── README.txt
```

### README.txt for Windows:
```
OSTEOPATHY EDUCATION PLANNER - Windows Version
==============================================

QUICK START:
1. Double-click PlannerGUI.exe to launch
2. If Windows shows a security warning:
   - Click "More info"
   - Click "Run anyway"
3. Edit your data in the GUI tabs
4. Click "Run Scheduler" to generate schedules
5. Results appear in images\schedule folder

FILES:
- PlannerGUI.exe: The application
- input_data.json: Your schedule data (auto-saved)
- image.jpeg: Summary image

TIPS:
- All changes save automatically
- Schedule images: images/schedule/
- The app creates an images folder on first run

Questions? Contact: [your email]
```

---

## Recommended Approach

**Easiest**: Build on a Windows machine using `build_windows_app.bat`

**Best for ongoing distribution**: Set up GitHub Actions (I can help!)

Would you like me to:
1. Create a GitHub Actions workflow for automatic Windows builds?
2. Create a more detailed distribution package script?
3. Add an installer (using Inno Setup) for Windows?
