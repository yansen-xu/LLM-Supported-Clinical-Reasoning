@echo off
chcp 65001 >nul
echo ========================================
echo 启动 CHI26 混合模式（分析 + 评估）
echo ========================================
echo.

echo [1/4] 启动后端服务（端口 5000 和 5001）...
cd backend
start "CHI26 Backend" cmd /k "python run_all.py"
timeout /t 3 /nobreak

echo [2/4] 等待后端服务就绪...
timeout /t 5 /nobreak

cd ..\frontend
echo [3/4] 启动前端混合模式（端口 8080）...
start "CHI26 Frontend" cmd /k "npm run mixed"

echo.
echo ========================================
echo 混合模式启动完成！
echo 前端地址: http://localhost:8080
echo 分析模式后端: http://localhost:5000
echo 评估模式后端: http://localhost:5001
echo ========================================
pause
