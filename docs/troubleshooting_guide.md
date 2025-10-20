# 消防应急RAG系统 - 故障排除指南

## 📋 概述

本文档记录了系统启动过程中遇到的常见问题及其解决方案，帮助快速诊断和修复系统问题。

## 🔍 问题分类

### 1. RAG服务问题

#### 问题：RAG服务不可达

**症状：**
- 系统验证显示 `[X] RAG服务: unreachable`
- RAG服务启动后立即退出
- ChromaDB连接测试失败

**根本原因：**
ChromaDB API版本不匹配
- RAG服务使用ChromaDB v1 API
- 但ChromaDB容器默认使用v2 API
- 导致连接测试失败

**解决方案：**
1. **自动兼容修复（推荐）**
   ```bash
   # RAG服务已更新为自动兼容v1和v2 API
   python scripts/start_rag_service.py
   ```

2. **手动验证ChromaDB状态**
   ```bash
   # 检查ChromaDB API版本
   curl -X GET "http://localhost:8007/api/v1/heartbeat"
   # 如果返回 "API废弃" 错误，说明是v2版本
   
   curl -X GET "http://localhost:8007/api/v1"
   # 如果返回404，说明服务可用但API版本不同
   ```

3. **重新启动RAG服务**
   ```bash
   # 停止当前RAG服务
   taskkill /F /IM python.exe
   
   # 重新启动
   python scripts/start_rag_service.py
   ```

**验证修复：**
```bash
# 检查RAG服务健康状态
curl -X GET "http://localhost:3000/health"

# 运行系统验证
python scripts/verify_system_status.py
```

### 2. 数据库连接问题

#### 问题：Neo4j连接失败

**症状：**
- 知识图谱服务启动失败
- Neo4j连接超时
- 认证失败错误

**解决方案：**
```bash
# 1. 重启Neo4j容器
cd "D:\Fire Emergency RAG System\infrastructure\docker"
docker-compose restart neo4j

# 2. 等待Neo4j完全启动（约30秒）
docker-compose ps

# 3. 重新启动知识图谱服务
python scripts/start_knowledge_graph_service.py
```

#### 问题：Redis连接被拒绝

**症状：**
- 缓存服务启动失败
- Redis连接错误
- 端口6379无法连接

**解决方案：**
```bash
# 1. 重启Redis容器
docker-compose restart redis

# 2. 检查Redis状态
docker-compose ps

# 3. 重新启动缓存服务
python scripts/start_cache_service.py
```

### 3. 端口冲突问题

#### 问题：端口已被占用

**症状：**
- 服务启动失败
- `[Errno 10048] 通常每个套接字地址只能使用一次`
- 端口绑定失败

**解决方案：**
```bash
# 1. 查找占用端口的进程
netstat -ano | findstr :8000

# 2. 终止占用进程
taskkill /PID <进程ID> /F

# 3. 重新启动服务
python scripts/start_emergency_service.py
```

### 4. 服务依赖问题

#### 问题：服务启动顺序错误

**症状：**
- 应急服务启动失败
- 依赖服务不可用
- 健康检查失败

**正确启动顺序：**
```bash
# 1. 启动数据库服务
cd "D:\Fire Emergency RAG System\infrastructure\docker"
docker-compose up -d postgres redis neo4j chromadb ollama

# 2. 等待数据库就绪（约30-60秒）
docker-compose ps

# 3. 按顺序启动应用服务
python scripts/start_knowledge_graph_service.py
python scripts/start_ollama_service.py
python scripts/start_cache_service.py
python scripts/start_rag_service.py
python scripts/start_emergency_service.py
```

## 🛠️ 诊断工具

### 系统状态检查
```bash
# 检查所有服务状态
python scripts/verify_system_status.py

# 检查Docker容器状态
docker-compose ps

# 检查端口占用
netstat -an | findstr "8000 8001 8003 8004 3000"
```

### 服务健康检查
```bash
# 应急服务
curl -X GET "http://localhost:8000/health"

# 知识图谱服务
curl -X GET "http://localhost:8001/health"

# Ollama服务
curl -X GET "http://localhost:8003/health"

# 缓存服务
curl -X GET "http://localhost:8004/health"

# RAG服务
curl -X GET "http://localhost:3000/health"
```

### 数据库连接测试
```bash
# PostgreSQL
docker exec -it fire_emergency_postgres psql -U postgres -d fire_emergency

# Redis
docker exec -it fire_emergency_redis redis-cli ping

# Neo4j
curl -X GET "http://localhost:7474"

# ChromaDB
curl -X GET "http://localhost:8007/api/v1"

# Ollama
curl -X GET "http://localhost:11434/api/tags"
```

## 📊 成功启动验证

### 完全成功的标志
- 所有5个核心服务显示 `[OK]` 状态
- 系统可用性达到 100%
- 应急查询功能正常
- 知识图谱查询正常
- RAG文档检索正常

### 验证命令
```bash
# 1. 系统状态验证
python scripts/verify_system_status.py

# 2. 应急查询测试
curl -X POST "http://localhost:8000/api/v1/emergency/query" \
  -H "Content-Type: application/json" \
  -d '{"query": "火灾逃生路线"}'

# 3. 知识图谱测试
curl -X GET "http://localhost:8001/materials/木材"

# 4. RAG搜索测试
curl -X GET "http://localhost:3000/search?q=火灾预防"
```

## 🔄 完整重启流程

如果系统出现严重问题，按以下步骤完全重启：

```bash
# 1. 停止所有Python服务
taskkill /F /IM python.exe

# 2. 停止所有Docker容器
cd "D:\Fire Emergency RAG System\infrastructure\docker"
docker-compose down

# 3. 清理Docker资源（可选）
docker system prune -f

# 4. 重新启动数据库服务
docker-compose up -d postgres redis neo4j chromadb ollama

# 5. 等待数据库就绪
docker-compose ps

# 6. 按顺序启动应用服务
cd "D:\Fire Emergency RAG System"
python scripts/start_knowledge_graph_service.py
python scripts/start_ollama_service.py
python scripts/start_cache_service.py
python scripts/start_rag_service.py
python scripts/start_emergency_service.py

# 7. 验证系统状态
python scripts/verify_system_status.py
```

## 📝 问题记录

### 已解决的问题

1. **ChromaDB API版本不匹配** ✅
   - 问题：RAG服务无法连接ChromaDB
   - 解决：更新RAG服务支持v1和v2 API
   - 时间：2025-10-14

2. **服务启动顺序问题** ✅
   - 问题：应急服务依赖其他服务但启动顺序错误
   - 解决：建立正确的启动顺序和依赖检查
   - 时间：2025-10-14

3. **端口冲突问题** ✅
   - 问题：多个服务尝试使用同一端口
   - 解决：建立端口管理和冲突检测机制
   - 时间：2025-10-14

### 待解决的问题

- 应急查询API路径404错误（非关键功能）
- 部分服务响应时间较长（性能优化）

## 📞 获取帮助

如果遇到本文档未覆盖的问题：

1. 检查系统日志文件
2. 运行完整的系统诊断
3. 查看Docker容器日志
4. 检查网络连接和防火墙设置

**最后更新：** 2025-10-14  
**文档版本：** v1.0
