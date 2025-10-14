# 系统启动指南

## 🚀 正确的启动方法

### ⚠️ 重要说明

**现在有多种启动方法可供选择！** 推荐使用一键启动脚本。

### 方法1：一键启动（推荐）

**使用智能启动脚本：**
```bash
# 完整启动（包含所有服务）
python scripts/start_system.py

# 或使用批处理文件（Windows）
start_system.bat

# 快速启动（仅核心服务）
python scripts/quick_start.py
```

**特点：**
- 自动处理端口冲突
- 智能依赖管理
- 健康检查等待
- 错误恢复机制
- 实时状态监控

### 方法2：服务管理

**管理单个服务：**
```bash
# 列出所有服务
python scripts/service_manager.py list

# 启动单个服务
python scripts/service_manager.py start emergency

# 停止服务
python scripts/service_manager.py stop emergency

# 重启服务
python scripts/service_manager.py restart emergency

# 检查服务状态
python scripts/service_manager.py status emergency
```

### 方法3：逐个启动服务（传统方法）

**第一步：启动数据库服务**
```bash
# 确保Docker Desktop正在运行
# 启动所有数据库服务
cd "D:\Fire Emergency RAG System\infrastructure\docker"
docker-compose up -d postgres redis neo4j chromadb ollama
```

**第二步：逐个启动应用服务**
```bash
# 切换到项目根目录
cd "D:\Fire Emergency RAG System"

# 按顺序启动服务（必须使用完整路径）
python scripts/start_knowledge_graph_service.py
python scripts/start_ollama_service.py  
python scripts/start_emergency_service.py
python scripts/start_cache_service.py
python scripts/start_rag_service.py
```

**第三步：验证系统状态**
```bash
python scripts/verify_system_status.py
```

### ❌ 不推荐的方法

以下方法经过测试都存在问题，**不要使用**：

- ~~`python scripts/start_system_step_by_step.py`~~ - 文件不存在
- ~~`python scripts/start_emergency_system.py`~~ - 文件不存在  
- ~~`docker-compose up -d`~~ - 应用服务启动失败
- ~~直接运行Python命令~~ - 模块导入失败

## 🔧 服务启动顺序和依赖关系

### 正确的启动顺序

**必须按以下顺序启动，否则会出现依赖问题：**

1. **知识图谱服务** (端口8001) - 可以独立启动
2. **Ollama服务** (端口8003) - 可以独立启动  
3. **应急服务** (端口8000) - 依赖缓存和Ollama服务
4. **缓存服务** (端口8004) - 可以独立启动
5. **RAG服务** (端口3000) - 可以独立启动

### 服务依赖关系

```
应急服务 (8000)
├── 需要: 缓存服务 (8004) ✅
├── 需要: Ollama服务 (8003) ✅  
├── 可选: 知识图谱服务 (8001) ⚠️ (Neo4j认证问题)
└── 可选: RAG服务 (3000) ✅

知识图谱服务 (8001)
└── 需要: Neo4j数据库 ⚠️ (认证失败，但服务仍可启动)

RAG服务 (3000)  
└── 需要: ChromaDB数据库 ✅

Ollama服务 (8003)
└── 需要: Ollama容器 ✅

缓存服务 (8004)
└── 需要: Redis数据库 ✅
```

## 🧪 测试系统

### 验证系统状态

```bash
# 检查所有服务健康状态
python scripts/verify_system_status.py
```

### 测试救援方案生成

```bash
# 创建测试数据文件
echo '{
  "items": [
    {
      "name": "木材",
      "material": "木质",
      "quantity": 1,
      "location": "客厅"
    },
    {
      "name": "汽油", 
      "material": "化学",
      "quantity": 1,
      "location": "车库"
    }
  ],
  "environment": {
    "type": "室内",
    "location": "客厅",
    "area": "住宅",
    "weather": "晴天",
    "wind_speed": "微风",
    "ventilation": "良好",
    "exits": 2
  }
}' > test_rescue_plan.json

# 测试救援方案生成
curl -X POST "http://localhost:8000/rescue-plan" -H "Content-Type: application/json" --data-binary "@test_rescue_plan.json"
```

## 📊 检查服务状态

### 系统监控

**实时监控系统状态：**
```bash
# 单次状态检查
python scripts/monitor_system.py --mode once

# 持续监控（每30秒检查一次）
python scripts/monitor_system.py --mode continuous --interval 30

# 监控并保存日志
python scripts/monitor_system.py --mode continuous --log

# 测试救援方案生成功能
python scripts/monitor_system.py --test
```

**传统检查方法：**
```bash
# 检查所有服务状态
python scripts/verify_system_status.py

# 检查端口占用
netstat -an | findstr "8000 8001 8003 8004 3000"

# 检查Python进程
tasklist | findstr python
```

### 访问服务

- **应急服务**: http://localhost:8000
- **API文档**: http://localhost:8000/docs  
- **健康检查**: http://localhost:8000/health
- **知识图谱服务**: http://localhost:8001
- **Ollama服务**: http://localhost:8003
- **缓存服务**: http://localhost:8004
- **RAG服务**: http://localhost:3000

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

1. **ModuleNotFoundError: No module named 'backend'**
   - **原因**: Python路径问题
   - **解决**: 必须使用 `cd "D:\Fire Emergency RAG System"` 切换到项目根目录
   - **不要使用**: 直接运行Python命令或从其他目录启动

2. **端口冲突错误 (Errno 10048)**
   - **原因**: 尝试启动多个相同端口的服务
   - **解决**: 确保每个服务只启动一次，检查端口占用情况
   - **检查**: `netstat -an | findstr "端口号"`

3. **Neo4j认证失败**
   - **现象**: 知识图谱服务显示认证错误但服务仍可启动
   - **影响**: 知识图谱功能受限，但不影响核心救援方案生成
   - **解决**: 这是已知问题，系统可以在降级模式下正常工作

4. **应急服务降级模式**
   - **现象**: 系统显示"degraded"状态
   - **原因**: 某些依赖服务不可用
   - **影响**: 核心功能正常，只是某些高级功能受限

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

### 完整启动流程

1. **启动数据库**: `docker-compose up -d postgres redis neo4j chromadb ollama`
2. **启动应用服务**: 按顺序逐个启动5个服务
3. **验证状态**: `python scripts/verify_system_status.py`
4. **测试功能**: 使用curl测试救援方案生成

### API使用

- **访问API文档**: http://localhost:8000/docs
- **生成救援方案**: POST http://localhost:8000/rescue-plan
- **健康检查**: GET http://localhost:8000/health
- **系统状态**: 通过验证脚本查看

### 成功标志

- 所有5个服务显示"healthy"状态
- 救援方案生成成功返回21个步骤
- 系统可用性达到100%

## 📞 获取帮助

### 诊断步骤

如果遇到问题，按以下顺序检查：

1. **检查Docker Desktop是否运行**
   ```bash
   docker ps
   ```

2. **检查数据库服务状态**
   ```bash
   docker-compose ps
   ```

3. **检查应用服务端口占用**
   ```bash
   netstat -an | findstr "8000 8001 8003 8004 3000"
   ```

4. **检查Python进程**
   ```bash
   tasklist | findstr python
   ```

5. **运行系统验证**
   ```bash
   python scripts/verify_system_status.py
   ```

### 常见错误解决

- **端口被占用**: 停止重复的服务进程
- **模块导入失败**: 确保在项目根目录运行命令
- **服务启动失败**: 检查依赖服务是否正常运行
