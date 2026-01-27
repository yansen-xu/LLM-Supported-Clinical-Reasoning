@echo off
setlocal enabledelayedexpansion
chcp 65001 >nul
echo ========================================
echo Starting CHI26 Evaluation Mode
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
echo [1/2] Starting backend service (port 5001)...
cd backend
start "CHI26 Backend - Evaluation" cmd /k "call conda activate !conda_env! && python run_evaluation.py"
timeout /t 3 /nobreak

cd ..\frontend
echo [2/2] Starting frontend evaluation mode (port 8081)...
start "CHI26 Frontend - Evaluation" cmd /k "call conda activate !conda_env! && npm run evaluation"

echo.
echo ========================================
echo Evaluation mode started!
echo Frontend: http://localhost:8081
echo Backend: http://localhost:5001
echo ========================================
pause
