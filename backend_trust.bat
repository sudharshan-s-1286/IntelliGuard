@echo off
REM IntelliGuard Trust Agent - Backend Launcher
REM Starts the FastAPI backend server using uvicorn

title IntelliGuard Trust Agent - Backend

REM Navigate to the backend directory relative to this script's location
cd /d "%~dp0backend"

REM Check if virtual environment exists
if not exist ".venv\Scripts\activate.bat" (
    echo.
    echo [ERROR] Virtual environment not found at: %~dp0backend\.venv
    echo.
    echo Please create the virtual environment first by running:
    echo   python -m venv .venv
    echo   .venv\Scripts\activate
    echo   pip install -r ..\requirements.txt
    echo.
    pause
    exit /b 1
)

REM Activate the virtual environment
call ".venv\Scripts\activate.bat"

REM Verify that app\main.py exists
if not exist "app\main.py" (
    echo.
    echo [ERROR] Backend entry point not found at: %~dp0backend\app\main.py
    echo.
    pause
    exit /b 1
)

echo.
echo [INFO] Starting IntelliGuard Trust Agent Backend...
echo [INFO] Press Ctrl+C to stop the server.
echo.

REM Use PORT and HOST environment variables with defaults
if "%PORT%"=="" set "PORT=8000"
if "%HOST%"=="" set "HOST=0.0.0.0"

REM Start the FastAPI server with auto-reload
uvicorn app.main:app --reload --host %HOST% --port %PORT%

REM Keep the terminal open after uvicorn exits
echo.
echo [INFO] Backend server has stopped.
pause
