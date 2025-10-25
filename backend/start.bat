@echo off
REM Startup script for Farmer Budget Optimizer (Windows)

setlocal

REM Default values
if "%ENVIRONMENT%"=="" set ENVIRONMENT=development
if "%HOST%"=="" set HOST=127.0.0.1
if "%PORT%"=="" set PORT=8000
if "%WORKERS%"=="" set WORKERS=1

echo Starting Farmer Budget Optimizer API...
echo Environment: %ENVIRONMENT%
echo Host: %HOST%
echo Port: %PORT%
echo Workers: %WORKERS%

REM Activate virtual environment if it exists
if exist "venv\Scripts\activate.bat" (
    echo Activating virtual environment...
    call venv\Scripts\activate.bat
)

REM Create necessary directories
if not exist "logs" mkdir logs
if not exist "data" mkdir data
if not exist "cache" mkdir cache
if not exist "backups" mkdir backups

REM Set environment file
if exist ".env.%ENVIRONMENT%" (
    echo Using environment file: .env.%ENVIRONMENT%
    copy ".env.%ENVIRONMENT%" .env
)

REM Start the application
if "%ENVIRONMENT%"=="development" (
    echo Starting in development mode with auto-reload...
    uvicorn app.main:app --host %HOST% --port %PORT% --reload
) else if "%ENVIRONMENT%"=="production" (
    echo Starting in production mode...
    uvicorn app.main:app --host %HOST% --port %PORT% --workers %WORKERS%
) else (
    echo Starting in %ENVIRONMENT% mode...
    uvicorn app.main:app --host %HOST% --port %PORT% --workers 2
)

endlocal