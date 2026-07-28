@echo off
REM IntelliGuard Trust Agent - Frontend Launcher
REM Starts the React development server using Vite

title IntelliGuard Trust Agent - Frontend

REM Navigate to the frontend directory relative to this script's location
cd /d "%~dp0frontend"

REM Check if package.json exists
if not exist "package.json" (
    echo.
    echo [ERROR] package.json not found at: %~dp0frontend\package.json
    echo.
    echo Please ensure the frontend directory is intact.
    echo.
    pause
    exit /b 1
)

echo.
echo [INFO] Starting IntelliGuard Trust Agent Frontend...
echo [INFO] Press Ctrl+C to stop the server.
echo.

REM Install dependencies if node_modules is missing
if not exist "node_modules" (
    echo [INFO] node_modules not found. Installing dependencies...
    call npm install
    echo.
)

REM Start the Vite development server
npm run dev

REM Keep the terminal open after the server exits
echo.
echo [INFO] Frontend server has stopped.
pause
