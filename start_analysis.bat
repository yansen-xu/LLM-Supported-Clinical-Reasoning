@echo off
chcp 65001 >nul
echo ========================================
echo 启动 CHI26 分析模式
echo ========================================
echo.

echo [1/2] 启动后端服务（端口 5000）...
cd backend
start "CHI26 Backend - Analysis" cmd /k "python run.py"
timeout /t 3 /nobreak

cd ..\frontend
echo [2/2] 启动前端分析模式（端口 8080）...
start "CHI26 Frontend - Analysis" cmd /k "npm run analysis"

echo.
echo ========================================
echo 分析模式启动完成！
echo 前端地址: http://localhost:8080
echo 后端地址: http://localhost:5000
echo ========================================
pause
