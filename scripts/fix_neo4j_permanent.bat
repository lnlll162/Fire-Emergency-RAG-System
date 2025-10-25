@echo off
REM ========================================
REM Neo4j永久修复脚本
REM 解决"already running (pid:7)"和自动停止问题
REM ========================================

echo ========================================
echo Neo4j容器问题永久修复
echo ========================================
echo.

REM 步骤1: 停止所有相关容器
echo [步骤 1/6] 停止Neo4j容器...
docker stop fire_emergency_neo4j 2>nul
timeout /t 3 /nobreak >nul

REM 步骤2: 移除容器
echo [步骤 2/6] 移除Neo4j容器...
docker rm fire_emergency_neo4j 2>nul

REM 步骤3: 完全清理数据卷（可选，但能彻底解决问题）
echo [步骤 3/6] 清理Neo4j数据卷...
echo 警告: 这将删除所有Neo4j数据！
choice /C YN /M "是否清理数据卷（建议选Y以彻底修复）"
if errorlevel 2 goto skip_volume_clean
docker volume rm fire_emergency_neo4j_data 2>nul
docker volume rm fire_emergency_neo4j_logs 2>nul
echo 数据卷已清理

:skip_volume_clean

REM 步骤4: 清理悬空镜像和缓存
echo [步骤 4/6] 清理Docker缓存...
docker system prune -f >nul 2>&1

REM 步骤5: 使用新配置重新启动
echo [步骤 5/6] 使用新配置启动Neo4j...
cd /d "%~dp0..\infrastructure\docker"
docker-compose up -d neo4j

REM 步骤6: 等待并验证启动
echo [步骤 6/6] 等待Neo4j完全启动...
echo 这可能需要30-60秒，请耐心等待...
timeout /t 10 /nobreak >nul

echo.
echo 正在验证启动状态...
for /L %%i in (1,1,12) do (
    docker ps | findstr "fire_emergency_neo4j" | findstr "Up" >nul
    if not errorlevel 1 (
        echo [成功] Neo4j容器正在运行！
        goto check_health
    )
    echo 等待中... %%i/12
    timeout /t 5 /nobreak >nul
)

echo [警告] Neo4j可能启动失败，查看日志...
docker logs --tail 20 fire_emergency_neo4j
goto end

:check_health
echo.
echo 等待健康检查通过...
timeout /t 30 /nobreak >nul

docker ps | findstr "fire_emergency_neo4j"
echo.

REM 测试连接
echo 测试Neo4j连接...
curl -u neo4j:password http://localhost:7474/ >nul 2>&1
if not errorlevel 1 (
    echo [成功] Neo4j HTTP接口可访问！
) else (
    echo [警告] HTTP接口暂时不可访问，可能还在初始化
)

:end
echo.
echo ========================================
echo 修复完成！
echo ========================================
echo.
echo 提示:
echo 1. 如果问题仍然存在，请运行: docker logs -f fire_emergency_neo4j
echo 2. 检查Docker Desktop内存分配（建议至少4GB）
echo 3. 以后启动使用: docker-compose up -d neo4j
echo.
pause

