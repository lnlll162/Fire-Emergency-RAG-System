# Docker 配置说明

## 📁 目录结构

```
infrastructure/docker/
├── docker-compose.yml          # 完整的Docker Compose配置
├── postgres/                   # PostgreSQL配置
│   └── init.sql               # 数据库初始化脚本
└── services/                   # 各服务的Dockerfile
    ├── Dockerfile.cache_service
    ├── Dockerfile.emergency_service
    ├── Dockerfile.ollama_service
    └── Dockerfile.rag_service
```

## 🚀 使用方法

### 启动所有服务
```bash
cd infrastructure/docker
docker-compose up -d
```

### 启动特定服务
```bash
# 只启动数据库服务
docker-compose up -d postgres redis neo4j chromadb ollama

# 启动应用服务
docker-compose up -d knowledge_graph_service rag_service ollama_service cache_service emergency_service
```

### 停止所有服务
```bash
docker-compose down
```

### 停止并删除数据卷
```bash
docker-compose down -v
```

## 🔧 服务配置

### 数据库服务
- **PostgreSQL**: 端口 5432
- **Redis**: 端口 6379
- **Neo4j**: 端口 7474 (Web), 7687 (Bolt)
- **ChromaDB**: 端口 8007

### 应用服务
- **知识图谱服务**: 端口 8001
- **RAG服务**: 端口 3000
- **Ollama服务**: 端口 8003
- **缓存服务**: 端口 8004
- **应急服务**: 端口 8000

## 📝 注意事项

1. **数据持久化**: 所有数据都存储在Docker volumes中
2. **网络通信**: 所有服务都在同一个Docker网络中
3. **健康检查**: 每个服务都有健康检查机制
4. **依赖关系**: 应用服务依赖数据库服务启动完成
