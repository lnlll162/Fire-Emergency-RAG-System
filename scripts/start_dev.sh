#!/bin/bash
# 火灾应急救援RAG系统 - 开发环境启动脚本

set -e

echo "🔥 启动火灾应急救援RAG系统开发环境"
echo "=================================="

# 检查Docker是否运行
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker未运行，请先启动Docker"
    exit 1
fi

# 检查Docker Compose是否安装
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose未安装，请先安装Docker Compose"
    exit 1
fi

# 创建环境变量文件（如果不存在）
if [ ! -f .env ]; then
    echo "📝 创建环境变量文件..."
    cp env.example .env
    echo "✅ 已创建 .env 文件，请根据需要修改配置"
fi

# 启动数据库服务
echo "🚀 启动数据库服务..."
docker-compose up -d postgres redis neo4j chromadb ollama

# 等待数据库启动
echo "⏳ 等待数据库启动..."
sleep 10

# 检查数据库健康状态
echo "🔍 检查数据库健康状态..."

# 检查PostgreSQL
if docker-compose exec postgres pg_isready -U postgres > /dev/null 2>&1; then
    echo "✅ PostgreSQL 已就绪"
else
    echo "❌ PostgreSQL 未就绪"
    exit 1
fi

# 检查Redis
if docker-compose exec redis redis-cli ping > /dev/null 2>&1; then
    echo "✅ Redis 已就绪"
else
    echo "❌ Redis 未就绪"
    exit 1
fi

# 检查Neo4j
if curl -s http://localhost:7474 > /dev/null 2>&1; then
    echo "✅ Neo4j 已就绪"
else
    echo "❌ Neo4j 未就绪"
    exit 1
fi

# 检查ChromaDB
if curl -s http://localhost:8007/api/v1/heartbeat > /dev/null 2>&1; then
    echo "✅ ChromaDB 已就绪"
else
    echo "❌ ChromaDB 未就绪"
    exit 1
fi

# 检查Ollama
if curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
    echo "✅ Ollama 已就绪"
else
    echo "❌ Ollama 未就绪"
    exit 1
fi

# 初始化数据库
echo "🔧 初始化数据库..."
python scripts/setup_databases.py

if [ $? -eq 0 ]; then
    echo "✅ 数据库初始化成功"
else
    echo "❌ 数据库初始化失败"
    exit 1
fi

echo ""
echo "🎉 开发环境启动完成！"
echo "=================================="
echo "数据库服务状态："
echo "  PostgreSQL: http://localhost:5432"
echo "  Redis:      http://localhost:6379"
echo "  Neo4j:      http://localhost:7474"
echo "  ChromaDB:   http://localhost:8007"
echo "  Ollama:     http://localhost:11434"
echo ""
echo "下一步："
echo "  1. 安装Python依赖: pip install -r requirements.txt"
echo "  2. 启动后端服务: python -m uvicorn app.main:app --reload"
echo "  3. 启动前端服务: cd frontend && npm run dev"
echo ""
echo "查看日志: docker-compose logs -f"
echo "停止服务: docker-compose down"
