@echo off
setlocal enabledelayedexpansion
chcp 65001 >nul
echo ========================================
echo Starting CHI26 Mixed Mode (Analysis + Evaluation)
echo ========================================
echo.

REM Check if conda is available
where conda >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Error: conda not found. Please install Anaconda or Miniconda first.
    pause
    exit /b 1
)

echo Available Conda environments:
conda env list | findstr /v "^#"
echo.
set /p conda_env="Please enter Conda environment name (default: base): "
if "!conda_env!"=="" set "conda_env=base"

echo Using environment: !conda_env!
echo.
cd ..
echo [1/4] Starting backend services (ports 5000 and 5001)...
cd backend
start "CHI26 Backend" cmd /k "call conda activate !conda_env! && python run_all.py"
timeout /t 3 /nobreak

echo [2/4] Waiting for backend services to be ready...
timeout /t 5 /nobreak

cd ..\frontend
echo [3/4] Starting frontend mixed mode (port 8080)...
start "CHI26 Frontend" cmd /k "call conda activate !conda_env! && npm run mixed"

echo.
echo ========================================
echo Mixed mode started!
echo Frontend: http://localhost:8080
echo Analysis backend: http://localhost:5000
echo Evaluation backend: http://localhost:5001
echo ========================================
pause
