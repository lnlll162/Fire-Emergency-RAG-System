@echo off
REM ========================================
REM Neo4j健康监控脚本
REM 持续监控Neo4j容器状态，自动检测问题
REM ========================================

echo ========================================
echo Neo4j容器健康监控
echo ========================================
echo.
echo 此脚本将持续监控Neo4j容器状态
echo 按 Ctrl+C 停止监控
echo.
echo 监控间隔: 每5分钟检查一次
echo.

:loop
REM 获取当前时间
for /f "tokens=1-4 delims=/ " %%a in ('date /t') do (set mydate=%%a-%%b-%%c)
for /f "tokens=1-2 delims=: " %%a in ('time /t') do (set mytime=%%a:%%b)

echo [%mydate% %mytime%] 检查中...

REM 检查Docker是否运行
docker info >nul 2>&1
if errorlevel 1 (
    echo [严重] Docker未运行！
    echo 请启动Docker Desktop
    goto wait
)

REM 检查容器是否存在
docker ps -a | findstr "fire_emergency_neo4j" >nul 2>&1
if errorlevel 1 (
    echo [严重] Neo4j容器不存在！
    echo 运行修复: scripts\fix_neo4j_permanent.bat
    goto wait
)

REM 检查容器是否运行
docker ps | findstr "fire_emergency_neo4j" | findstr "Up" >nul 2>&1
if errorlevel 1 (
    echo [警告] Neo4j容器已停止！
    docker ps -a | findstr "fire_emergency_neo4j"
    
    REM 检查日志中的错误
    docker logs --tail 10 fire_emergency_neo4j | findstr "already running" >nul 2>&1
    if not errorlevel 1 (
        echo [错误] 检测到 "already running" 错误！
        echo 需要运行修复: scripts\fix_neo4j_permanent.bat
    )
    
    goto wait
)

REM 检查健康状态
docker ps | findstr "fire_emergency_neo4j" | findstr "healthy" >nul 2>&1
if not errorlevel 1 (
    echo [正常] Neo4j容器运行正常且健康
) else (
    docker ps | findstr "fire_emergency_neo4j" | findstr "unhealthy" >nul 2>&1
    if not errorlevel 1 (
        echo [警告] Neo4j容器不健康！
        docker logs --tail 5 fire_emergency_neo4j
    ) else (
        echo [信息] Neo4j容器运行中，健康检查进行中...
    )
)

REM 测试HTTP接口
curl -s -u neo4j:password http://localhost:7474/ >nul 2>&1
if errorlevel 1 (
    echo [警告] HTTP接口不可访问
) else (
    echo [正常] HTTP接口可访问
)

REM 检查资源使用
echo [资源] CPU/内存使用情况:
docker stats fire_emergency_neo4j --no-stream --format "table {{.CPUPerc}}\t{{.MemUsage}}" | findstr /V "CPU"

:wait
echo.
echo 下次检查: 5分钟后...
echo ----------------------------------------
echo.
timeout /t 300 /nobreak >nul
goto loop

