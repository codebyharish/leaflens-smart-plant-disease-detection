@echo off
where python >nul 2>nul
if errorlevel 1 (
  echo Python was not found. Read START_HERE.md and install Python 3.10 or newer.
  pause
  exit /b 1
)
if not exist .venv\Scripts\python.exe (
  echo Creating the virtual environment and installing packages...
  python -m venv .venv
  call .venv\Scripts\activate.bat
  pip install -r requirements.txt
) else (
  call .venv\Scripts\activate.bat
)
streamlit run app.py
