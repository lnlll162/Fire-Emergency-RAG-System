@echo off
chcp 65001 >nul
echo ========================================
echo 重启应急服务
echo ========================================

echo.
echo [1/3] 查找并停止现有的应急服务进程...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":8000" ^| findstr "LISTENING"') do (
    echo 找到进程 PID: %%a
    taskkill /F /PID %%a 2>nul
    if errorlevel 1 (
        echo 停止进程失败或进程不存在
    ) else (
        echo 进程已停止
    )
)

echo.
echo [2/3] 等待端口释放...
timeout /t 2 /nobreak >nul

echo.
echo [3/3] 启动应急服务...
start "应急服务" cmd /k "cd /d D:\Fire Emergency RAG System && python scripts/start_emergency_service.py"

echo.
echo ========================================
echo 应急服务重启完成!
echo 服务地址: http://localhost:8000
echo 文档地址: http://localhost:8000/docs
echo ========================================
echo.
echo 按任意键关闭此窗口...
pause >nul

