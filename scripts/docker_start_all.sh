#!/bin/bash
# Docker Compose 一键启动脚本

echo "🚀 启动火灾应急RAG系统 (Docker Compose)"
echo "=========================================="

# 检查Docker和Docker Compose是否安装
if ! command -v docker &> /dev/null; then
    echo "❌ Docker 未安装，请先安装Docker"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose 未安装，请先安装Docker Compose"
    exit 1
fi

# 切换到Docker配置目录
cd infrastructure/docker

# 检查docker-compose.yml文件是否存在
if [ ! -f "docker-compose.yml" ]; then
    echo "❌ docker-compose.yml 文件不存在"
    exit 1
fi

# 停止并删除现有容器
echo "🧹 清理现有容器..."
docker-compose down -v

# 构建并启动所有服务
echo "🔨 构建并启动所有服务..."
docker-compose up --build -d

# 等待服务启动
echo "⏳ 等待服务启动..."
sleep 30

# 检查服务状态
echo "🔍 检查服务状态..."
docker-compose ps

# 运行健康检查
echo "🏥 运行健康检查..."
cd ../../
python scripts/verify_system.py

echo "✅ 系统启动完成！"
echo ""
echo "🌐 服务访问地址:"
echo "  - 应急服务: http://localhost:8000"
echo "  - 知识图谱服务: http://localhost:8001"
echo "  - RAG服务: http://localhost:3000"
echo "  - Ollama服务: http://localhost:8003"
echo "  - 缓存服务: http://localhost:8004"
echo ""
echo "📝 管理命令:"
echo "  - 查看日志: docker-compose logs -f"
echo "  - 停止服务: docker-compose down"
echo "  - 重启服务: docker-compose restart"
