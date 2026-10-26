@echo off
set "PYTHON_EXE=%LocalAppData%\Programs\Python\Python314\python.exe"
if not exist "%PYTHON_EXE%" (
  for /d %%D in ("%LocalAppData%\Programs\Python\Python3*") do (
    if exist "%%~fD\python.exe" set "PYTHON_EXE=%%~fD\python.exe"
  )
)
if not exist "%PYTHON_EXE%" (
  echo Python was not found. Install Python 3.10 or newer first.
  pause
  exit /b 1
)
"%PYTHON_EXE%" -m pip install -r requirements.txt
start http://127.0.0.1:5000
"%PYTHON_EXE%" web_app.py
