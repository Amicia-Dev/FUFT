@echo off
REM Check which Python command is available: py, python, python3

set "PYTHON_CMD="

REM Check for 'python3'
python3 --version >nul 2>&1
if %ERRORLEVEL%==0 (
    set "PYTHON_CMD=python3"
    goto :found
)

REM Check for 'py' first
py --version >nul 2>&1
if %ERRORLEVEL%==0 (
    set "PYTHON_CMD=py"
    goto :found
)

REM Check for 'python'
python --version >nul 2>&1
if %ERRORLEVEL%==0 (
    set "PYTHON_CMD=python"
    goto :found
)



:found
if defined PYTHON_CMD (
    set "PYTHON=%PYTHON_CMD%"
    echo Creating virtual environment...
    PYTHON -m venv .venv
    echo Generating launch script Launch.bat...

    echo @echo off > Launch.bat
    echo if exist setup_windows.bat ^(del setup_windows.bat^) else ^(echo.^) >> Launch.bat
    echo .venv\Scripts\python.exe main.py >> Launch.bat
    



    echo Installing dependencies...
    .venv\Scripts\pip3 install urllib3 tqdm

    del setup_linux.sh
    echo.
    echo Setup complete. Use Launch.bat to run the program. You can close this window.
    echo.
    pause

) else (
    echo No Python interpreter found! Install Python or add it to your environment variables.
    pause
)

