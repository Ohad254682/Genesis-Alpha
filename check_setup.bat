@echo off
echo ========================================
echo   Checking Setup...
echo ========================================
echo.

cd /d "%~dp0"
echo Current directory: %CD%
echo.

echo [1/4] Checking Python...
set PYTHON_CMD=
python --version >nul 2>&1
if %errorlevel% == 0 (
    set PYTHON_CMD=python
    python --version
    echo   Status: OK
) else (
    py --version >nul 2>&1
    if %errorlevel% == 0 (
        set PYTHON_CMD=py
        py --version
        echo   Status: OK
    ) else (
        python3 --version >nul 2>&1
        if %errorlevel% == 0 (
            set PYTHON_CMD=python3
            python3 --version
            echo   Status: OK
        ) else (
            echo   Status: FAILED - Python not found!
            echo   Please install Python from https://www.python.org/
            echo   Or add Python to your system PATH
            goto :end
        )
    )
)
echo.

echo [2/4] Checking Streamlit...
%PYTHON_CMD% -m streamlit --version >nul 2>&1
if %errorlevel% == 0 (
    %PYTHON_CMD% -m streamlit --version
    echo   Status: OK
) else (
    echo   Status: NOT INSTALLED
    echo   Will install when running START_APP.bat
)
echo.

echo [3/4] Checking required packages...
%PYTHON_CMD% -c "import pandas, numpy, yfinance, streamlit" >nul 2>&1
if %errorlevel% == 0 (
    echo   Status: OK - Core packages installed
) else (
    echo   Status: MISSING - Some packages need to be installed
    echo   Run: %PYTHON_CMD% -m pip install -r requirements.txt
)
echo.

echo [4/4] Checking app files...
if exist "app\main.py" (
    echo   Status: OK - app\main.py found
) else (
    echo   Status: FAILED - app\main.py not found!
    goto :end
)
echo.

echo ========================================
echo   Setup Check Complete
echo ========================================
echo.
echo To start the app, run: START_APP.bat
echo.

:end
pause








