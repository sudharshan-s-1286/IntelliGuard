@echo off
REM IntelliGuard Trust Agent - Master Launcher
REM Starts both backend and frontend services in separate windows

title IntelliGuard Trust Agent Launcher

REM Print startup banner
echo.
echo =====================================
echo       IntelliGuard Trust Agent
echo =====================================
echo.

REM Get the directory where this script is located
set "SCRIPT_DIR=%~dp0"

REM Verify that backend_trust.bat exists
if not exist "%SCRIPT_DIR%backend_trust.bat" (
    echo [ERROR] backend_trust.bat not found at: %SCRIPT_DIR%backend_trust.bat
    echo Please ensure all launcher scripts are in the same directory.
    pause
    exit /b 1
)

REM Verify that frontend_trust.bat exists
if not exist "%SCRIPT_DIR%frontend_trust.bat" (
    echo [ERROR] frontend_trust.bat not found at: %SCRIPT_DIR%frontend_trust.bat
    echo Please ensure all launcher scripts are in the same directory.
    pause
    exit /b 1
)

echo [INFO] Starting Backend...
echo.

REM Launch backend in a new Command Prompt window
start "Backend" cmd /k ""%SCRIPT_DIR%backend_trust.bat""

REM Wait approximately 2 seconds for the backend to initialize
timeout /t 2 /nobreak >nul

echo [INFO] Starting Frontend...
echo.

REM Launch frontend in a new Command Prompt window
start "Frontend" cmd /k ""%SCRIPT_DIR%frontend_trust.bat""

REM Wait a moment for the frontend window to open
timeout /t 1 /nobreak >nul

echo.
echo Backend Started.
echo Frontend Started.
echo All IntelliGuard Trust Agent services are running.
echo.
echo [INFO] Close this window to exit the launcher.
echo [INFO] The backend and frontend will continue running in their own windows.
echo.

REM Keep the launcher window open
pause
