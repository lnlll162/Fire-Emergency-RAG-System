#!/bin/bash
# RAG服务嵌入模型修复测试脚本

set -e

echo "🔥 RAG服务嵌入模型修复测试"
echo "================================"

# 检查Python环境
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3未安装或不在PATH中"
    exit 1
fi

# 检查依赖包
echo "📦 检查依赖包..."
if ! python3 -c "import sentence_transformers, chromadb, fastapi" 2>/dev/null; then
    echo "❌ 缺少必要的依赖包"
    echo "请运行: pip install sentence-transformers chromadb fastapi"
    exit 1
fi

echo "✅ 依赖包检查通过"

# 启动RAG服务（后台）
echo "🚀 启动RAG服务..."
cd backend/services
python3 rag_service.py &
RAG_PID=$!
cd ../..

# 等待服务启动
echo "⏳ 等待服务启动..."
sleep 5

# 检查服务是否启动
echo "🔍 检查服务状态..."
if curl -s http://localhost:3000/health > /dev/null 2>&1; then
    echo "✅ RAG服务已启动"
else
    echo "❌ RAG服务启动失败"
    echo "请检查端口3000是否被占用"
    kill $RAG_PID 2>/dev/null || true
    exit 1
fi

# 运行测试
echo "🧪 运行测试..."
python3 test_rag_embedding_fix.py

# 显示服务信息
echo ""
echo "📊 服务信息:"
echo "  RAG服务: http://localhost:3000"
echo "  API文档: http://localhost:3000/docs"
echo "  模型状态: http://localhost:3000/model-status"
echo ""

echo "🎉 测试完成！"
echo "按任意键退出..."
read -n 1 -s

# 清理后台进程
kill $RAG_PID 2>/dev/null || true
