# 🪟 Windows Installation Guide

## Problem: Compiler Errors on Windows

You're getting this error because:
- Python 3.14 is very new
- pandas 2.1.4 needs to be compiled from source
- Windows doesn't have C++ compilers by default

## ✅ Solution: Use Pre-Built Wheels

### Option 1: Use Updated Requirements (RECOMMENDED)
```bash
pip install -r requirements_windows.txt
```

This installs newer versions that have pre-built wheels for Python 3.14.

### Option 2: Downgrade to Python 3.11 or 3.12
Python 3.14 is bleeding edge. For better compatibility:
1. Download Python 3.11 or 3.12 from python.org
2. Install it
3. Use the original requirements.txt

### Option 3: Install Packages One-by-One
If you still have issues, try:
```bash
pip install streamlit
pip install pandas
pip install requests
pip install pillow
```

This lets pip find the best available version for your system.

## 🎯 Quick Start (Windows)

1. **Open PowerShell or Command Prompt**
2. **Navigate to your project folder**
   ```bash
   cd path\to\your\project
   ```

3. **Install packages**
   ```bash
   pip install -r requirements_windows.txt
   ```

4. **Run the app**
   ```bash
   streamlit run er_monitor_app.py
   ```

## 🔧 If You Still Get Errors

### Install Visual C++ Build Tools
Some packages need C++ compilers. Install them:

1. Download: https://visualstudio.microsoft.com/visual-cpp-build-tools/
2. Run installer
3. Select "Desktop development with C++"
4. Install
5. Restart terminal
6. Try `pip install -r requirements.txt` again

## ✅ Verify Installation

After installing, check if it worked:
```bash
python -c "import streamlit; import pandas; import requests; from PIL import Image; print('All packages installed successfully!')"
```

If you see "All packages installed successfully!" - you're ready to go! 🎉

## 🆘 Still Having Issues?

Try creating a virtual environment:
```bash
# Create virtual environment
python -m venv venv

# Activate it (Windows)
venv\Scripts\activate

# Install packages
pip install -r requirements_windows.txt

# Run app
streamlit run er_monitor_app.py
```

---

## Next Steps After Installation

Once packages are installed:
1. ✅ Generate patient CSV files (I can help with this!)
2. ✅ Test the app
3. ✅ Create architecture diagram
4. ✅ Record demo video
5. ✅ Submit assignment
