@echo off
REM ========================================
REM Neo4j快速状态检查
REM 一键检查Neo4j所有关键指标
REM ========================================

echo ========================================
echo Neo4j容器状态检查
echo ========================================
echo.

REM 检查Docker
echo [1/6] 检查Docker服务...
docker info >nul 2>&1
if errorlevel 1 (
    echo [X] Docker未运行
    goto end_error
) else (
    echo [V] Docker正常运行
)
echo.

REM 检查容器是否存在
echo [2/6] 检查容器存在性...
docker ps -a | findstr "fire_emergency_neo4j" >nul 2>&1
if errorlevel 1 (
    echo [X] Neo4j容器不存在
    echo 提示: 运行 docker-compose up -d neo4j
    goto end_error
) else (
    echo [V] 容器存在
)
echo.

REM 检查容器运行状态
echo [3/6] 检查容器运行状态...
docker ps | findstr "fire_emergency_neo4j" | findstr "Up" >nul 2>&1
if errorlevel 1 (
    echo [X] 容器未运行
    docker ps -a | findstr "fire_emergency_neo4j"
    echo.
    echo 提示: 运行 scripts\start_neo4j_safe.bat
    goto end_error
) else (
    echo [V] 容器正在运行
    docker ps | findstr "fire_emergency_neo4j"
)
echo.

REM 检查健康状态
echo [4/6] 检查健康状态...
docker ps | findstr "fire_emergency_neo4j" | findstr "healthy" >nul 2>&1
if not errorlevel 1 (
    echo [V] 容器健康
) else (
    docker ps | findstr "fire_emergency_neo4j" | findstr "unhealthy" >nul 2>&1
    if not errorlevel 1 (
        echo [!] 容器不健康
        echo 最近日志:
        docker logs --tail 10 fire_emergency_neo4j
    ) else (
        echo [~] 健康检查进行中（启动阶段）
    )
)
echo.

REM 测试HTTP接口
echo [5/6] 测试HTTP接口 (7474)...
curl -s -u neo4j:password http://localhost:7474/ >nul 2>&1
if errorlevel 1 (
    echo [X] HTTP接口不可访问
) else (
    echo [V] HTTP接口正常
    echo URL: http://localhost:7474
)
echo.

REM 测试Bolt接口（简单端口检查）
echo [6/6] 测试Bolt接口 (7687)...
netstat -an | findstr "7687" | findstr "LISTENING" >nul 2>&1
if errorlevel 1 (
    echo [X] Bolt端口未监听
) else (
    echo [V] Bolt端口正常
    echo URL: bolt://localhost:7687
)
echo.

REM 显示资源使用
echo ========================================
echo 资源使用情况
echo ========================================
docker stats fire_emergency_neo4j --no-stream --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.MemPerc}}"
echo.

REM 检查是否有错误
echo ========================================
echo 错误检查
echo ========================================
docker logs --tail 20 fire_emergency_neo4j | findstr /I "error already running failed" >nul 2>&1
if not errorlevel 1 (
    echo [!] 检测到错误，最近20行日志:
    docker logs --tail 20 fire_emergency_neo4j | findstr /I "error already running failed"
    echo.
    echo 提示: 如果看到 "already running"，运行 scripts\fix_neo4j_permanent.bat
) else (
    echo [V] 未检测到严重错误
)
echo.

REM 显示登录信息
echo ========================================
echo 登录信息
echo ========================================
echo Neo4j Browser: http://localhost:7474
echo 用户名: neo4j
echo 密码: password
echo.

goto end_success

:end_error
echo.
echo ========================================
echo 状态: 有问题需要处理
echo ========================================
echo.
echo 快速修复:
echo   1. 运行 scripts\start_neo4j_safe.bat
echo   2. 如果问题持续，运行 scripts\fix_neo4j_permanent.bat
echo.
pause
exit /b 1

:end_success
echo ========================================
echo 状态: 一切正常！
echo ========================================
echo.
pause
exit /b 0

