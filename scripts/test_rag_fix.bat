@echo off
REM RAG服务嵌入模型修复测试脚本

echo 🔥 RAG服务嵌入模型修复测试
echo ================================

REM 检查Python环境
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python未安装或不在PATH中
    pause
    exit /b 1
)

REM 检查依赖包
echo 📦 检查依赖包...
python -c "import sentence_transformers, chromadb, fastapi" >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ 缺少必要的依赖包
    echo 请运行: pip install sentence-transformers chromadb fastapi
    pause
    exit /b 1
)

echo ✅ 依赖包检查通过

REM 启动RAG服务（后台）
echo 🚀 启动RAG服务...
cd backend/services
start /B python rag_service.py
cd ../..

REM 等待服务启动
echo ⏳ 等待服务启动...
timeout /t 5 /nobreak >nul

REM 检查服务是否启动
echo 🔍 检查服务状态...
curl -s http://localhost:3000/health >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ RAG服务已启动
) else (
    echo ❌ RAG服务启动失败
    echo 请检查端口3000是否被占用
    pause
    exit /b 1
)

REM 运行测试
echo 🧪 运行测试...
python test_rag_embedding_fix.py

REM 显示服务信息
echo.
echo 📊 服务信息:
echo   RAG服务: http://localhost:3000
echo   API文档: http://localhost:3000/docs
echo   模型状态: http://localhost:3000/model-status
echo.

echo 🎉 测试完成！
echo 按任意键退出...
pause >nul
