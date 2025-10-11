# 系统启动指南

## 🚀 快速启动

### 方法1：分步启动（推荐）

```bash
# 分步启动，先启动数据库再启动应用服务
python scripts/start_system_step_by_step.py
```

### 方法2：直接启动所有服务

```bash
# 直接启动所有服务（需要确保数据库已运行）
python scripts/start_emergency_system.py
```

### 方法3：Docker Compose启动

```bash
# 使用Docker Compose启动所有服务
docker-compose up -d
```

## 🔧 手动启动单个服务

如果某个服务启动失败，可以手动启动：

```bash
# 启动知识图谱服务
python scripts/start_knowledge_graph_service.py

# 启动RAG服务
python scripts/start_rag_service.py

# 启动Ollama服务
python scripts/start_ollama_service.py

# 启动缓存服务
python scripts/start_cache_service.py

# 启动应急服务
python scripts/start_emergency_service.py
```

## 🧪 测试系统

### 测试应急服务独立运行

```bash
# 测试应急服务是否可以在降级模式下工作
python scripts/test_emergency_only.py
```

### 测试完整系统

```bash
# 测试所有服务集成
python scripts/test_emergency_service.py

# 完整系统验证
python scripts/verify_emergency_system.py
```

## 📊 检查服务状态

### 检查所有服务健康状态

```bash
# 检查可用服务
python scripts/check_available_services.py

# 简单验证
python scripts/simple_verification.py
```

### 访问服务

- **应急服务**: http://localhost:8000
- **API文档**: http://localhost:8000/docs
- **健康检查**: http://localhost:8000/health
- **系统状态**: http://localhost:8000/status

## 🗄️ 数据库服务

系统需要以下数据库服务：

1. **PostgreSQL** (端口5432) - 用户数据存储
2. **Redis** (端口6379) - 缓存服务
3. **Neo4j** (端口7474/7687) - 知识图谱
4. **ChromaDB** (端口8007) - 向量数据库

### 启动数据库服务

```bash
# 使用Docker启动数据库
docker run -d --name fire_emergency_postgres -e POSTGRES_DB=fire_emergency -e POSTGRES_USER=postgres -e POSTGRES_PASSWORD=password -p 5432:5432 postgres:15-alpine

docker run -d --name fire_emergency_redis -p 6379:6379 redis:7-alpine

docker run -d --name fire_emergency_neo4j -e NEO4J_AUTH=neo4j/password -p 7474:7474 -p 7687:7687 neo4j:5.15-community

docker run -d --name fire_emergency_chromadb -p 8007:8000 chromadb/chroma:latest
```

## ⚠️ 故障排除

### 常见问题

1. **服务启动后立即停止**
   - 检查端口是否被占用
   - 检查依赖服务是否运行
   - 查看服务日志

2. **数据库连接失败**
   - 确保数据库容器正在运行
   - 检查数据库连接配置
   - 等待数据库完全启动

3. **应急服务降级模式**
   - 这是正常现象，应急服务可以在依赖服务不可用时工作
   - 会使用预定义的救援方案模板

### 查看日志

```bash
# 查看Docker容器日志
docker logs fire_emergency_postgres
docker logs fire_emergency_redis
docker logs fire_emergency_neo4j
docker logs fire_emergency_chromadb

# 查看应用服务日志
# 服务启动时会显示详细日志
```

### 重启服务

```bash
# 停止所有服务
docker stop fire_emergency_postgres fire_emergency_redis fire_emergency_neo4j fire_emergency_chromadb

# 重新启动
python scripts/start_system_step_by_step.py
```

## 🎯 系统架构

```
应急服务 (8000) ← 核心协调服务
    ├── 知识图谱服务 (8001) ← 材质和环境知识
    ├── RAG服务 (3000) ← 文档检索
    ├── Ollama服务 (8003) ← AI生成
    └── 缓存服务 (8004) ← 性能优化

数据库层:
    ├── PostgreSQL (5432) ← 用户数据
    ├── Redis (6379) ← 缓存
    ├── Neo4j (7474/7687) ← 知识图谱
    └── ChromaDB (8007) ← 向量存储
```

## 📝 使用说明

1. **启动系统**: 使用分步启动脚本
2. **访问API**: 打开 http://localhost:8000/docs
3. **生成救援方案**: 使用 POST /rescue-plan 端点
4. **监控状态**: 使用 GET /health 和 GET /status 端点

## 🔄 开发模式

如果需要开发模式（自动重载）：

```bash
# 设置环境变量
export DEVELOPMENT=true

# 启动服务（会启用自动重载）
python scripts/start_emergency_service.py
```

## 📞 获取帮助

如果遇到问题：

1. 查看服务日志
2. 检查端口占用情况
3. 验证数据库连接
4. 运行测试脚本诊断问题
