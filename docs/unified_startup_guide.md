# 消防应急RAG系统 - 统一启动指南

## 🚀 唯一推荐启动方法

### ⚠️ 重要说明
**本系统只提供一种正确的启动方法，其他方法可能导致系统不稳定！**

## 📋 系统架构

### 核心服务（5个）
- **应急服务** (8000) - 核心协调服务
- **知识图谱服务** (8001) - 材质和环境知识
- **Ollama服务** (8003) - AI文本生成
- **缓存服务** (8004) - 性能优化
- **RAG服务** (3000) - 文档检索

### 数据库服务（5个）
- **PostgreSQL** (5432) - 用户数据
- **Redis** (6379) - 缓存
- **Neo4j** (7474/7687) - 知识图谱
- **ChromaDB** (8007) - 向量数据库
- **Ollama** (11434) - 本地LLM

## 🎯 正确启动步骤

### 第一步：确保环境准备
```bash
# 1. 确保Docker Desktop正在运行
docker ps

# 2. 切换到项目根目录
cd "D:\Fire Emergency RAG System"
```

### 第二步：一键启动（推荐）
```bash
# 使用智能启动脚本
python scripts/start_system.py
```

**这个脚本会：**
- 自动启动所有Docker数据库服务
- 按正确顺序启动应用服务
- 处理端口冲突
- 等待服务健康检查
- 提供实时状态监控

### 第三步：验证系统状态
```bash
# 检查系统状态
python scripts/verify_system_status.py
```

**期望结果：**
- 所有5个核心服务显示 `[OK]` 状态
- 系统可用性达到 80% 以上
- 应急查询功能正常

## 🔧 故障排除

### 如果启动失败

1. **清理所有服务**
```bash
# 停止所有Python进程
tasklist | findstr python
# 手动终止相关进程

# 停止Docker容器
docker stop fire_emergency_postgres fire_emergency_redis fire_emergency_neo4j fire_emergency_chromadb fire_emergency_ollama
```

2. **重新启动**
```bash
# 重新运行启动脚本
python scripts/start_system.py
```

### 常见问题

1. **端口冲突**
   - 脚本会自动处理，无需手动操作

2. **Docker未运行**
   - 启动Docker Desktop
   - 等待Docker完全启动

3. **服务启动超时**
   - 等待更长时间（最多5分钟）
   - 检查Docker容器状态

## 📊 服务状态说明

### 健康状态
- `[OK]` - 服务正常运行
- `[ERROR]` - 服务异常
- `[TIMEOUT]` - 服务响应超时
- `[UNREACHABLE]` - 服务无法连接

### 系统可用性
- **100%** - 所有服务正常
- **80-99%** - 系统基本正常
- **<80%** - 系统异常，需要检查

## 🎯 访问地址

启动成功后，可以访问：

- **前端界面**: http://localhost:3001
- **应急服务API**: http://localhost:8000
- **API文档**: http://localhost:8000/docs
- **系统健康检查**: http://localhost:8000/health

## ❌ 不推荐的方法

**以下方法经过测试存在问题，不要使用：**

- ~~逐个启动服务~~ - 容易出错
- ~~手动启动Docker~~ - 依赖关系复杂
- ~~直接运行Python文件~~ - 缺少依赖检查
- ~~使用其他启动脚本~~ - 可能冲突

## 📝 最佳实践

1. **开发时**：使用 `python scripts/start_system.py`
2. **测试时**：启动后运行 `python scripts/verify_system_status.py`
3. **生产时**：使用 `start_system.bat`（Windows）
4. **监控时**：使用 `python scripts/monitor_system.py`

## 🆘 获取帮助

如果遇到问题：

1. 检查Docker Desktop是否运行
2. 确保在项目根目录运行命令
3. 查看启动日志输出
4. 运行系统验证脚本
5. 检查端口占用情况

---

**记住：只使用 `python scripts/start_system.py` 这一种方法启动系统！**
