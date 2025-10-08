@echo off
REM 火灾应急救援RAG系统 - Windows开发环境启动脚本

echo 🔥 启动火灾应急救援RAG系统开发环境
echo ==================================

REM 检查Docker是否运行
docker info >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Docker未运行，请先启动Docker Desktop
    pause
    exit /b 1
)

REM 检查Docker Compose是否安装
docker-compose --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Docker Compose未安装，请先安装Docker Compose
    pause
    exit /b 1
)

REM 创建环境变量文件（如果不存在）
if not exist .env (
    echo 📝 创建环境变量文件...
    copy env.example .env
    echo ✅ 已创建 .env 文件，请根据需要修改配置
)

REM 启动数据库服务
echo 🚀 启动数据库服务...
docker-compose up -d postgres redis neo4j chromadb ollama

REM 等待数据库启动
echo ⏳ 等待数据库启动...
timeout /t 10 /nobreak >nul

REM 检查数据库健康状态
echo 🔍 检查数据库健康状态...

REM 检查PostgreSQL
docker-compose exec postgres pg_isready -U postgres >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ PostgreSQL 已就绪
) else (
    echo ❌ PostgreSQL 未就绪
    pause
    exit /b 1
)

REM 检查Redis
docker-compose exec redis redis-cli ping >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ Redis 已就绪
) else (
    echo ❌ Redis 未就绪
    pause
    exit /b 1
)

REM 检查Neo4j
curl -s http://localhost:7474 >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ Neo4j 已就绪
) else (
    echo ❌ Neo4j 未就绪
    pause
    exit /b 1
)

REM 检查ChromaDB
curl -s http://localhost:8007/api/v1/heartbeat >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ ChromaDB 已就绪
) else (
    echo ❌ ChromaDB 未就绪
    pause
    exit /b 1
)

REM 检查Ollama
curl -s http://localhost:11434/api/tags >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ Ollama 已就绪
) else (
    echo ❌ Ollama 未就绪
    pause
    exit /b 1
)

REM 初始化数据库
echo 🔧 初始化数据库...
python scripts/setup_databases.py

if %errorlevel% equ 0 (
    echo ✅ 数据库初始化成功
) else (
    echo ❌ 数据库初始化失败
    pause
    exit /b 1
)

echo.
echo 🎉 开发环境启动完成！
echo ==================================
echo 数据库服务状态：
echo   PostgreSQL: http://localhost:5432
echo   Redis:      http://localhost:6379
echo   Neo4j:      http://localhost:7474
echo   ChromaDB:   http://localhost:8007
echo   Ollama:     http://localhost:11434
echo.
echo 下一步：
echo   1. 安装Python依赖: pip install -r requirements.txt
echo   2. 启动后端服务: python -m uvicorn app.main:app --reload
echo   3. 启动前端服务: cd frontend ^&^& npm run dev
echo.
echo 查看日志: docker-compose logs -f
echo 停止服务: docker-compose down
pause
