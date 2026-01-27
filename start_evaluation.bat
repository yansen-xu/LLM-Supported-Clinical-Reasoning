@echo off
chcp 65001 >nul
echo ========================================
echo 启动 CHI26 评估模式
echo ========================================
echo.

echo [1/2] 启动后端服务（端口 5001）...
cd backend
start "CHI26 Backend - Evaluation" cmd /k "python run_evaluation.py"
timeout /t 3 /nobreak

cd ..\frontend
echo [2/2] 启动前端评估模式（端口 8081）...
start "CHI26 Frontend - Evaluation" cmd /k "npm run evaluation"

echo.
echo ========================================
echo 评估模式启动完成！
echo 前端地址: http://localhost:8081
echo 后端地址: http://localhost:5001
echo ========================================
pause
