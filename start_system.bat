@echo off
chcp 65001 >nul
echo 火灾应急救援RAG系统 - 一键启动
echo ================================================

cd /d "%~dp0"

echo 检查Python环境...
python --version >nul 2>&1
if errorlevel 1 (
    echo 错误: 未找到Python，请确保Python已安装并添加到PATH
    pause
    exit /b 1
)

echo 检查Docker环境...
docker --version >nul 2>&1
if errorlevel 1 (
    echo 错误: 未找到Docker，请确保Docker Desktop已安装并运行
    pause
    exit /b 1
)

echo 启动系统...
python scripts/start_system.py

if errorlevel 1 (
    echo 系统启动失败！
    pause
    exit /b 1
) else (
    echo 系统启动成功！
)

pause
