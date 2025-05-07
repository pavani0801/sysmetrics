@echo off
setlocal

:: Check pip availability
where pip >nul 2>nul
if errorlevel 1 (
    echo pip not found. Please install Python and ensure pip is in your PATH.
    pause
    exit /b 1
)

:: Check for requirements.txt
if not exist requirements.txt (
    echo requirements.txt not found.
    pause
    exit /b 1
)

:: Check if dependencies are already installed
pip install -r requirements.txt --dry-run >nul 2>&1
if %errorlevel% neq 0 (
    echo Installing missing dependencies...
    pip install -r requirements.txt
) else (
    echo All dependencies already satisfied.
)

echo Running run.py...
python run.py

pause
