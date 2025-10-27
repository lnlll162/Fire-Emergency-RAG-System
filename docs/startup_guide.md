# 消防应急RAG系统 - 启动指南

## 🚀 快速启动摘要

### ✅ 系统状态更新 (2025-10-27)
- **Neo4j认证问题**: 已完全解决 ✅
- **Neo4j "Already Running" 问题**: 已完全解决 ✅
- **知识图谱数据**: 已成功导入 (80个节点, 100个关系) ✅
- **RAG文档**: 已准备就绪 (30篇) ✅
- **所有7个服务**: 正常运行 ✅
- **系统可用性**: 100% ✅
- **知识图谱功能**: 完全正常 ✅
- **自动化工具**: 完整的启动和监控脚本 ✅

### 一键启动所有服务
```bash
# 1. 启动数据库服务
cd "D:\Fire Emergency RAG System\infrastructure\docker"
docker-compose up -d postgres redis chromadb ollama

# 1.1 安全启动Neo4j（推荐方法）
cd "D:\Fire Emergency RAG System"
.\scripts\start_neo4j_safe.bat

# 2. 启动应用服务
python scripts/start_knowledge_graph_service.py
python scripts/start_ollama_service.py
python scripts/start_cache_service.py
python scripts/start_rag_service.py
python scripts/start_emergency_service.py
python backend/services/user_service.py
python backend/services/admin_service.py

# 3. 启动前端应用
cd "D:\Fire Emergency RAG System\frontend"
npm run dev

# 4. 验证系统状态
python scripts/verify_system_status.py

# 5. 检查Neo4j状态（可选）
.\scripts\check_neo4j_status.bat
```

### 系统包含7个核心服务 + 前端应用
- **应急服务** (8000) - 核心协调
- **知识图谱服务** (8001) - 知识管理
- **用户服务** (8002) - 用户认证
- **Ollama服务** (8003) - AI生成
- **缓存服务** (8004) - 性能优化
- **管理服务** (8005) - 系统管理
- **RAG服务** (3000) - 文档检索
- **前端应用** (3001) - Web界面

## 🚀 唯一正确的启动方法

### ⚠️ 重要说明

**本系统只提供一种正确的启动方法，其他方法可能导致系统不稳定！**

## 📋 系统架构

### 核心服务（7个后端服务 + 1个前端应用）
- **应急服务** (8000) - 核心协调服务
- **知识图谱服务** (8001) - 材质和环境知识
- **用户服务** (8002) - 用户认证和权限管理
- **Ollama服务** (8003) - AI文本生成
- **缓存服务** (8004) - 性能优化
- **管理服务** (8005) - 系统监控和管理
- **RAG服务** (3000) - 文档检索
- **前端应用** (3001) - Next.js Web界面

### 数据库服务（5个）
- **PostgreSQL** (5432) - 用户数据
- **Redis** (6379) - 缓存
- **Neo4j** (7474/7687) - 知识图谱
- **ChromaDB** (8007) - 向量数据库
- **Ollama** (11434) - 本地LLM

### ⚠️ 重要：PostgreSQL配置说明
**为避免编码和连接问题，请查看：** [`docs/postgresql_best_practices.md`](./postgresql_best_practices.md)

该文档包含：
- ✅ 已实施的所有编码修复
- ✅ 防止问题复现的检查清单
- ✅ 常见错误的解决方案
- ✅ 快速验证命令

## 🎯 正确启动步骤

### 第一步：确保环境准备
```bash
# 1. 确保Docker Desktop正在运行
docker ps

# 2. 切换到项目根目录
cd "D:\Fire Emergency RAG System"
```

### 第二步：启动数据库服务
```bash
# 启动所有Docker数据库服务
cd "D:\Fire Emergency RAG System\infrastructure\docker"
docker-compose up -d postgres redis neo4j chromadb ollama

# 等待数据库服务完全就绪（约30-60秒）
# 检查数据库状态
docker-compose ps
```

### 第二步之一：导入数据（首次运行或重置数据时）
```bash
# 切换到项目根目录
cd "D:\Fire Emergency RAG System"

# 导入Neo4j知识图谱数据
python scripts/import_neo4j_data.py

# 验证数据导入
python scripts/verify_data_import.py

# 注：RAG文档会在系统启动时自动导入到Qdrant向量数据库
```

**已导入的数据包括：**
- ✅ 80个知识图谱节点（物品、材质、环境、救援方案）
- ✅ 100个关系（材质关系、救援需求、环境适用性）
- ✅ 30篇RAG文档（救援程序、案例研究、设备指南）

### 第三步：逐个启动应用服务
```bash
# 切换到项目根目录
cd "D:\Fire Emergency RAG System"

# 按顺序启动服务，每个服务启动后等待健康检查
python scripts/start_knowledge_graph_service.py
# 等待知识图谱服务启动完成（约10秒）

python scripts/start_ollama_service.py
# 等待Ollama服务启动完成（约10秒）

python scripts/start_cache_service.py
# 等待缓存服务启动完成（约5秒）

python scripts/start_rag_service.py
# 等待RAG服务启动完成（约15秒）

python scripts/start_emergency_service.py
# 等待应急服务启动完成（约10秒）

# 启动用户服务和管理服务
python backend/services/user_service.py
# 等待用户服务启动完成（约5秒）

python backend/services/admin_service.py
# 等待管理服务启动完成（约5秒）

# 启动前端应用
cd "D:\Fire Emergency RAG System\frontend"
npm run dev
# 等待前端启动完成（约10-15秒）
```

### 第四步：验证系统状态
```bash
# 检查系统状态
cd "D:\Fire Emergency RAG System"
python scripts/verify_system_status.py
```

**期望结果：**
- 所有7个核心服务显示 `[OK]` 状态
- 系统可用性达到 100%
- 所有功能正常可用

## 🚀 快速启动用户服务和管理服务

### 用户服务启动
```bash
# 切换到项目根目录
cd "D:\Fire Emergency RAG System"

# 启动用户服务（端口8002）
python backend/services/user_service.py
```

### 管理服务启动
```bash
# 切换到项目根目录
cd "D:\Fire Emergency RAG System"

# 启动管理服务（端口8005）
python backend/services/admin_service.py
```

### 验证服务状态
```bash
# 检查用户服务
curl -X GET "http://localhost:8002/health"

# 检查管理服务
curl -X GET "http://localhost:8005/health"
```

## 🎨 前端应用启动

### 前端技术栈
- **框架**: Next.js 15 (App Router)
- **语言**: TypeScript 5.0+
- **样式**: Tailwind CSS 4.0
- **端口**: 3001

### 启动前端应用
```bash
# 切换到前端目录
cd "D:\Fire Emergency RAG System\frontend"

# 首次运行需要安装依赖（如果还没安装）
npm install

# 启动开发服务器
npm run dev
```

**启动成功标志：**
```
> frontend@0.1.0 dev
> next dev --port 3001

  ▲ Next.js 15.5.5
  - Local:        http://localhost:3001
  - Environments: .env.local

 ✓ Starting...
 ✓ Ready in 2.5s
```

### 访问前端应用

前端启动后，访问以下页面：

- **首页**: http://localhost:3001
- **应急查询页面**: http://localhost:3001/emergency
- **知识图谱页面**: http://localhost:3001/knowledge
- **管理后台页面**: http://localhost:3001/admin

### 前端配置

如需修改后端API地址，在 `frontend/.env.local` 中配置：

```env
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
NEXT_PUBLIC_APP_NAME=消防应急RAG系统
NEXT_PUBLIC_APP_VERSION=1.0.0
```

### 前端构建（生产环境）

```bash
# 构建生产版本
cd "D:\Fire Emergency RAG System\frontend"
npm run build

# 启动生产服务器
npm start
```

## 🔧 分步启动方法（备选）

如果一键启动遇到问题，可以使用分步启动：

### 第一步：启动数据库服务
```bash
# 确保Docker Desktop正在运行
cd "D:\Fire Emergency RAG System\infrastructure\docker"
docker-compose up -d postgres redis neo4j chromadb ollama
```

### 第二步：逐个启动应用服务
```bash
# 切换到项目根目录
cd "D:\Fire Emergency RAG System"

# 按顺序启动服务
python scripts/start_knowledge_graph_service.py
python scripts/start_ollama_service.py  
python scripts/start_cache_service.py
python scripts/start_rag_service.py
python scripts/start_emergency_service.py

# 启动用户服务和管理服务
python backend/services/user_service.py
python backend/services/admin_service.py

# 启动前端应用
cd "D:\Fire Emergency RAG System\frontend"
npm run dev
```

### 第三步：验证系统状态
```bash
python scripts/verify_system_status.py
```

## ❌ 不推荐的方法

以下方法经过测试都存在问题，**不要使用**：

- ~~直接运行Python文件~~ - 模块导入失败
- ~~使用其他启动脚本~~ - 可能冲突

## 🔧 服务启动顺序和依赖关系

### 正确的启动顺序

**必须按以下顺序启动，否则会出现依赖问题：**

1. **知识图谱服务** (端口8001) - 可以独立启动
2. **Ollama服务** (端口8003) - 可以独立启动  
3. **缓存服务** (端口8004) - 可以独立启动
4. **RAG服务** (端口3000) - 可以独立启动
5. **应急服务** (端口8000) - 依赖缓存和Ollama服务
6. **用户服务** (端口8002) - 可以独立启动
7. **管理服务** (端口8005) - 可以独立启动

### 服务依赖关系

```
应急服务 (8000)
├── 需要: 缓存服务 (8004) ✅
├── 需要: Ollama服务 (8003) ✅  
├── 可选: 知识图谱服务 (8001) ✅
└── 可选: RAG服务 (3000) ✅

用户服务 (8002)
├── 需要: PostgreSQL数据库 ✅
└── 需要: Redis数据库 ✅

管理服务 (8005)
├── 需要: PostgreSQL数据库 ✅
├── 需要: Redis数据库 ✅
├── 需要: Neo4j数据库 ✅
└── 需要: ChromaDB数据库 ✅

知识图谱服务 (8001)
└── 需要: Neo4j数据库 ✅

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

#### 前端应用 (Web界面)
- **前端首页**: http://localhost:3001
- **应急查询**: http://localhost:3001/emergency
- **知识图谱**: http://localhost:3001/knowledge
- **管理后台**: http://localhost:3001/admin

#### 后端API服务
- **应急服务**: http://localhost:8000
  - **API文档**: http://localhost:8000/docs  
  - **健康检查**: http://localhost:8000/health
- **知识图谱服务**: http://localhost:8001
  - **API文档**: http://localhost:8001/docs
- **用户服务**: http://localhost:8002
  - **API文档**: http://localhost:8002/docs
- **Ollama服务**: http://localhost:8003
  - **API文档**: http://localhost:8003/docs
- **缓存服务**: http://localhost:8004
  - **API文档**: http://localhost:8004/docs
- **管理服务**: http://localhost:8005
  - **API文档**: http://localhost:8005/docs
- **RAG服务**: http://localhost:3000
  - **API文档**: http://localhost:3000/docs

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

3. **Neo4j认证问题** ✅ **已解决**
   - **现象**: 之前可能显示认证错误，但服务仍可启动
   - **影响**: 无影响，知识图谱功能完全正常
   - **解决**: Neo4j认证问题已完全解决，所有功能正常

4. **应急服务降级模式** ✅ **已解决**
   - **现象**: 之前可能显示"degraded"状态
   - **原因**: 某些依赖服务不可用
   - **影响**: 无影响，所有服务现在都正常运行

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
前端层:
    └── Next.js Web应用 (3001) ← 用户界面

应用层:
    应急服务 (8000) ← 核心协调服务
        ├── 知识图谱服务 (8001) ← 材质和环境知识
        ├── 用户服务 (8002) ← 用户认证和权限管理
        ├── Ollama服务 (8003) ← AI生成
        ├── 缓存服务 (8004) ← 性能优化
        ├── 管理服务 (8005) ← 系统监控和管理
        └── RAG服务 (3000) ← 文档检索

数据库层:
    ├── PostgreSQL (5432) ← 用户数据
    ├── Redis (6379) ← 缓存
    ├── Neo4j (7474/7687) ← 知识图谱
    ├── ChromaDB (8007) ← 向量存储
    └── Ollama (11434) ← 本地LLM
```

## 📝 使用说明

### 完整启动流程

1. **启动数据库**: `docker-compose up -d postgres redis neo4j chromadb ollama`
2. **启动应用服务**: 按顺序逐个启动7个后端服务
3. **启动前端应用**: `cd frontend && npm run dev`
4. **验证状态**: `python scripts/verify_system_status.py`
5. **测试功能**: 使用curl测试救援方案生成或访问Web界面

### 应用使用

#### Web界面 (推荐)
- **访问前端**: http://localhost:3001
- **应急查询**: 通过Web界面提交查询
- **知识图谱**: 可视化查看知识实体
- **管理后台**: 监控系统状态

#### API直接调用
- **访问API文档**: http://localhost:8000/docs
- **生成救援方案**: POST http://localhost:8000/rescue-plan
- **健康检查**: GET http://localhost:8000/health
- **系统状态**: 通过验证脚本查看

### 成功标志

- 所有7个后端服务显示"healthy"状态
- 前端应用正常访问
- 救援方案生成成功返回多个步骤
- 系统可用性达到100%
- 用户认证功能正常
- 系统管理功能正常
- Web界面正常响应

## 🔧 故障排除指南

### 常见问题及解决方案

#### 1. RAG服务不可达问题

**问题现象：**
- RAG服务启动失败
- ChromaDB连接测试失败
- 系统验证显示RAG服务unreachable

**原因分析：**
- ChromaDB API版本不匹配
- RAG服务使用v1 API，但ChromaDB容器返回v2 API

**解决方案：**
```bash
# 1. 检查ChromaDB状态
curl -X GET "http://localhost:8007/api/v1/heartbeat"

# 2. 如果返回API废弃错误，说明是v2版本
# 3. RAG服务已自动兼容v1和v2 API，无需手动修复
# 4. 重新启动RAG服务
python scripts/start_rag_service.py
```

#### 2. 数据库连接问题

**问题现象：**
- Neo4j连接失败
- Redis连接被拒绝
- 服务健康检查失败

**解决方案：**
```bash
# 1. 重启Docker数据库服务
cd "D:\Fire Emergency RAG System\infrastructure\docker"
docker-compose restart

# 2. 等待服务完全启动
docker-compose ps

# 3. 重新启动应用服务
```

#### 3. 端口冲突问题

**问题现象：**
- 服务启动失败
- 端口已被占用错误

**解决方案：**
```bash
# 1. 查找占用端口的进程
netstat -ano | findstr :8000

# 2. 终止占用进程
taskkill /PID <进程ID> /F

# 3. 重新启动服务
```

#### 4. 前端启动问题

**问题现象：**
- 前端启动失败
- 依赖安装错误
- 编译错误

**解决方案：**

**依赖问题：**
```bash
# 清理node_modules和package-lock.json
cd "D:\Fire Emergency RAG System\frontend"
rmdir /s /q node_modules
del package-lock.json

# 重新安装依赖
npm install
```

**端口被占用：**
```bash
# 检查3001端口
netstat -ano | findstr :3001

# 终止占用进程
taskkill /PID <进程ID> /F

# 或修改端口（在package.json中修改 --port 参数）
```

**Node版本问题：**
```bash
# 检查Node版本（需要18.0+）
node --version

# 如版本过低，升级Node.js
# 下载地址：https://nodejs.org/
```

**环境变量配置：**
```bash
# 创建.env.local文件
cd "D:\Fire Emergency RAG System\frontend"
echo NEXT_PUBLIC_API_BASE_URL=http://localhost:8000 > .env.local
```

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

5. **检查Node.js进程（前端）**
   ```bash
   tasklist | findstr node
   netstat -ano | findstr :3001
   ```

6. **运行系统验证**
   ```bash
   python scripts/verify_system_status.py
   ```

### 成功启动验证

**完全成功的标志：**
- 所有7个后端服务显示 `[OK]` 状态
- 前端应用正常运行（端口3001）
- 系统可用性达到 100%
- Web界面正常访问
- 应急查询功能正常
- 知识图谱查询正常
- RAG文档检索正常
- 用户认证功能正常
- 系统管理功能正常

**验证命令：**
```bash
# 检查系统状态
python scripts/verify_system_status.py

# 快速检查所有服务健康状态
python -c "
import asyncio
import httpx

async def check_services():
    services = {
        'emergency_service': 'http://localhost:8000',
        'rag_service': 'http://localhost:3000', 
        'knowledge_graph_service': 'http://localhost:8001',
        'user_service': 'http://localhost:8002',
        'ollama_service': 'http://localhost:8003',
        'cache_service': 'http://localhost:8004',
        'admin_service': 'http://localhost:8005'
    }
    
    async with httpx.AsyncClient(timeout=5.0) as client:
        for name, url in services.items():
            try:
                r = await client.get(f'{url}/health')
                status = '[OK]' if r.status_code == 200 else '[FAIL]'
                print(f'{name:20} | {status} | HTTP {r.status_code}')
            except:
                print(f'{name:20} | [ERROR] | 无法连接')

asyncio.run(check_services())
"

# 测试应急查询
curl -X POST "http://localhost:8000/api/v1/emergency/query" \
  -H "Content-Type: application/json" \
  -d '{"query": "火灾逃生路线"}'

# 验证前端应用
curl -I http://localhost:3001
# 应返回 HTTP 200 OK
```

## 🔧 Neo4j故障排除

### Neo4j常见问题和解决方案

#### 问题1：Neo4j启动失败 - "already running (pid:7)"

**症状：**
```
Error: already running (pid:7)
```

**原因：** PID文件残留，容器误认为已有实例运行

**解决方案（按推荐顺序）：**

1. **使用永久修复脚本（最推荐）：**
```bash
cd "D:\Fire Emergency RAG System"
.\scripts\fix_neo4j_permanent.bat
```

2. **使用安全启动脚本：**
```bash
.\scripts\start_neo4j_safe.bat
```

3. **手动修复：**
```bash
# 停止并移除容器
docker-compose stop neo4j
docker-compose rm -f neo4j

# 重新创建（已自动清理PID文件）
docker-compose up -d neo4j
```

#### 问题2：Neo4j健康检查失败

**症状：**
```
STATUS: Up 2 minutes (unhealthy)
```

**检查步骤：**
```bash
# 1. 查看日志
docker logs fire_emergency_neo4j --tail 50

# 2. 检查状态
.\scripts\check_neo4j_status.bat

# 3. 如果持续不健康，运行修复
.\scripts\fix_neo4j_permanent.bat
```

#### 问题3：Neo4j端口被占用

**症状：**
```
Error: Port 7474 is already allocated
```

**解决方案：**
```bash
# 查找占用进程
netstat -ano | findstr "7474"
netstat -ano | findstr "7687"

# 停止冲突服务或在docker-compose.yml中修改端口
```

#### 问题4：Neo4j数据卷权限问题

**症状：**
```
Permission denied: /data
```

**解决方案：**
```bash
# 完全重置（会丢失数据）
docker-compose down
docker volume rm fire_emergency_neo4j_data fire_emergency_neo4j_logs
docker-compose up -d neo4j
```

### Neo4j管理工具

系统提供以下自动化工具：

1. **fix_neo4j_permanent.bat** - 永久修复脚本
   - 彻底解决 "already running" 问题
   - 自动清理和重建容器
   - 推荐在遇到任何问题时使用

2. **start_neo4j_safe.bat** - 安全启动脚本
   - 智能检查和清理
   - 渐进式健康验证
   - 适合日常启动

3. **check_neo4j_status.bat** - 状态检查工具
   - 一键检查所有关键指标
   - 快速诊断问题
   - 建议每天使用前检查

4. **monitor_neo4j.bat** - 持续监控工具
   - 每5分钟自动检查
   - 实时错误检测
   - 适合长期运行

**推荐使用流程：**
```bash
# 日常启动
.\scripts\start_neo4j_safe.bat

# 检查状态
.\scripts\check_neo4j_status.bat

# 遇到问题
.\scripts\fix_neo4j_permanent.bat

# 长期监控（可选）
.\scripts\monitor_neo4j.bat
```

**详细文档：**
- 完整故障排除指南：`docs/neo4j_troubleshooting.md`
- 解决方案总结：`docs/neo4j_solution_summary.md`
