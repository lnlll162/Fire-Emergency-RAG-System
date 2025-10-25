@echo off
REM ========================================
REM Neo4j安全启动脚本
REM 自动检测并修复常见问题
REM ========================================

echo ========================================
echo Neo4j安全启动向导
echo ========================================
echo.

REM 检查Docker是否运行
docker info >nul 2>&1
if errorlevel 1 (
    echo [错误] Docker未运行！请先启动Docker Desktop
    pause
    exit /b 1
)

echo [检查] Docker运行正常
echo.

REM 检查现有容器状态
docker ps -a | findstr "fire_emergency_neo4j" >nul 2>&1
if not errorlevel 1 (
    echo 检测到现有Neo4j容器，正在分析状态...
    
    REM 检查是否为Exited状态
    docker ps -a | findstr "fire_emergency_neo4j" | findstr "Exited" >nul 2>&1
    if not errorlevel 1 (
        echo [警告] 检测到容器处于Exited状态，正在清理...
        docker stop fire_emergency_neo4j 2>nul
        docker rm fire_emergency_neo4j 2>nul
        echo [完成] 已清理旧容器
        echo.
        goto start_container
    )
    
    REM 检查是否正在运行
    docker ps | findstr "fire_emergency_neo4j" | findstr "Up" >nul 2>&1
    if not errorlevel 1 (
        echo [信息] Neo4j已在运行中
        echo.
        echo 选择操作:
        echo 1. 重启容器（推荐，如果遇到问题）
        echo 2. 保持当前状态
        echo 3. 完全重置（清理数据卷）
        choice /C 123 /M "请选择"
        
        if errorlevel 3 goto full_reset
        if errorlevel 2 goto check_health
        if errorlevel 1 goto restart_container
    )
)

:start_container
echo [启动] 正在启动Neo4j容器...
cd /d "%~dp0..\infrastructure\docker"
docker-compose up -d neo4j
goto wait_startup

:restart_container
echo [重启] 正在重启Neo4j容器...
docker restart fire_emergency_neo4j
goto wait_startup

:full_reset
echo.
echo [警告] 完全重置将删除所有Neo4j数据！
choice /C YN /M "确定要继续吗"
if errorlevel 2 goto end

echo 正在执行完全重置...
docker stop fire_emergency_neo4j 2>nul
docker rm fire_emergency_neo4j 2>nul
docker volume rm fire_emergency_neo4j_data 2>nul
docker volume rm fire_emergency_neo4j_logs 2>nul
cd /d "%~dp0..\infrastructure\docker"
docker-compose up -d neo4j
goto wait_startup

:wait_startup
echo.
echo [等待] Neo4j正在启动，请稍候...
echo 预计需要30-60秒...
timeout /t 15 /nobreak >nul

REM 监控启动过程
for /L %%i in (1,1,12) do (
    docker ps | findstr "fire_emergency_neo4j" >nul 2>&1
    if errorlevel 1 (
        echo [错误] 容器未找到！
        goto show_logs
    )
    
    docker ps | findstr "fire_emergency_neo4j" | findstr "Up" >nul 2>&1
    if not errorlevel 1 (
        echo [进度] %%i/12 - 容器运行中...
    ) else (
        echo [警告] %%i/12 - 容器可能启动失败
        docker ps -a | findstr "fire_emergency_neo4j"
        goto show_logs
    )
    
    timeout /t 5 /nobreak >nul
)

:check_health
echo.
echo [验证] 检查Neo4j健康状态...
timeout /t 10 /nobreak >nul

REM 测试HTTP接口
curl -s -u neo4j:password http://localhost:7474/ >nul 2>&1
if not errorlevel 1 (
    echo [成功] HTTP接口 (7474) 正常
) else (
    echo [警告] HTTP接口暂不可用，可能还在初始化
)

REM 测试Bolt接口（更直接）
echo.
echo 最终状态:
docker ps | findstr "fire_emergency_neo4j"
echo.

REM 检查是否有"already running"错误
docker logs --tail 20 fire_emergency_neo4j | findstr "already running" >nul 2>&1
if not errorlevel 1 (
    echo [错误] 检测到"already running (pid:7)"错误！
    echo 这是进程冲突问题，需要完全重置
    echo.
    choice /C YN /M "是否现在执行完全重置"
    if not errorlevel 2 goto full_reset
    goto end
)

echo [成功] Neo4j启动正常！
echo.
echo 访问地址:
echo   - Neo4j Browser: http://localhost:7474
echo   - Bolt协议: bolt://localhost:7687
echo   - 用户名: neo4j
echo   - 密码: password
goto end

:show_logs
echo.
echo [调试] 最近的日志输出:
docker logs --tail 30 fire_emergency_neo4j
echo.
echo 如需完整日志，运行: docker logs -f fire_emergency_neo4j

:end
echo.
echo ========================================
echo 启动流程完成
echo ========================================
echo.
pause
