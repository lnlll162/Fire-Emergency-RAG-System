@echo off
REM Neo4j容器修复脚本
REM 解决"Neo4j is already running (pid:7)"问题
REM 基于 docs/neo4j_troubleshooting.md

echo ============================================================
echo Neo4j容器修复工具
echo ============================================================
echo.

echo [1/5] 检查Neo4j容器状态...
docker ps -a --filter name=fire_emergency_neo4j --format "table {{.Names}}\t{{.Status}}"

echo.
echo [2/5] 停止并移除旧容器（清理残留进程）...
docker stop fire_emergency_neo4j 2>nul
docker rm fire_emergency_neo4j 2>nul
echo     已清理

echo.
echo [3/5] 重新启动Neo4j容器...
cd /d "%~dp0..\infrastructure\docker"
docker-compose up -d neo4j

if errorlevel 1 (
    echo [ERROR] 启动失败！
    pause
    exit /b 1
)

echo.
echo [4/5] 等待Neo4j完全启动（约15秒）...
timeout /t 15 /nobreak >nul

echo.
echo [5/5] 验证容器健康状态...
docker ps --filter name=fire_emergency_neo4j --format "table {{.Names}}\t{{.Status}}"

echo.
echo 测试连接...
docker exec fire_emergency_neo4j cypher-shell -u neo4j -p password "RETURN 'Connection OK' as status;" 2>nul

if errorlevel 1 (
    echo [WARNING] 连接测试失败，容器可能还在启动中
    echo 请等待约30秒后重试，或运行: docker logs fire_emergency_neo4j
) else (
    echo.
    echo ============================================================
    echo [SUCCESS] Neo4j已成功修复并运行！
    echo ============================================================
    echo.
    echo 连接信息：
    echo   Browser: http://localhost:7474
    echo   Bolt: bolt://localhost:7687
    echo   用户名: neo4j
    echo   密码: password
    echo ============================================================
)

echo.
pause

