@echo off
echo ========================================
echo   Starting Stock Analysis App...
echo ========================================
echo.
cd /d "%~dp0"
echo Current directory: %CD%
echo.

REM Try to find Python
set PYTHON_CMD=
echo Checking Python installation...
python --version >nul 2>&1
if %errorlevel% == 0 (
    set PYTHON_CMD=python
    echo Found: python
    python --version
) else (
    py --version >nul 2>&1
    if %errorlevel% == 0 (
        set PYTHON_CMD=py
        echo Found: py
        py --version
    ) else (
        python3 --version >nul 2>&1
        if %errorlevel% == 0 (
            set PYTHON_CMD=python3
            echo Found: python3
            python3 --version
        ) else (
            echo ERROR: Python not found!
            echo.
            echo Python is not installed or not in your system PATH.
            echo.
            echo Please do one of the following:
            echo   1. Install Python from https://www.python.org/downloads/
            echo      (Make sure to check "Add Python to PATH" during installation)
            echo   2. Or run find_python.ps1 to find existing Python installations
            echo   3. Or use Anaconda/Miniconda and activate your environment first
            echo.
            echo After installing Python, restart this script.
            echo.
            pause
            exit /b 1
        )
    )
)
echo.

REM Check if Streamlit is installed
echo Checking Streamlit installation...
%PYTHON_CMD% -m streamlit --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Streamlit is not installed!
    echo Installing required packages...
    %PYTHON_CMD% -m pip install -r requirements.txt
    if %errorlevel% neq 0 (
        echo ERROR: Failed to install dependencies!
        pause
        exit /b 1
    )
)
echo.

echo Starting Streamlit server...
echo.
echo The app will open in your browser at: http://localhost:8501
echo.
echo Press Ctrl+C to stop the server
echo.
%PYTHON_CMD% -m streamlit run app/main.py
if %errorlevel% neq 0 (
    echo.
    echo ERROR: Failed to start Streamlit server!
    echo Check the error messages above.
    echo.
    pause
    exit /b 1
)
pause

