# 启动脚本使用指南

## 📋 概述

本系统提供了多种启动脚本，满足不同场景的需求：

- **一键启动**：智能启动所有服务
- **快速启动**：仅启动核心服务
- **服务管理**：管理单个服务
- **系统监控**：实时监控系统状态

## 🚀 启动脚本列表

### 1. 一键启动脚本

#### `start_system.py` - 完整系统启动
```bash
python scripts/start_system.py
```

**功能特点：**
- 自动启动所有数据库服务（Docker）
- 按依赖顺序启动应用服务
- 自动处理端口冲突
- 健康检查等待机制
- 错误恢复和重试
- 实时状态监控

**适用场景：**
- 生产环境部署
- 完整功能测试
- 系统演示

#### `start_system.bat` - Windows批处理启动
```bash
start_system.bat
```

**功能特点：**
- Windows用户友好
- 自动检查Python和Docker环境
- 调用Python启动脚本

### 2. 快速启动脚本

#### `quick_start.py` - 核心服务快速启动
```bash
python scripts/quick_start.py
```

**功能特点：**
- 仅启动核心服务
- 跳过可选服务（RAG、知识图谱）
- 快速启动，适合开发调试
- 自动健康检查

**启动的服务：**
- PostgreSQL, Redis, Neo4j, ChromaDB, Ollama
- 知识图谱服务
- Ollama服务
- 缓存服务
- RAG服务
- 应急服务

### 3. 服务管理脚本

#### `service_manager.py` - 单个服务管理
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

**支持的服务：**
- `knowledge_graph` - 知识图谱服务
- `ollama` - Ollama服务
- `cache` - 缓存服务
- `rag` - RAG服务
- `emergency` - 应急服务

### 4. 系统监控脚本

#### `monitor_system.py` - 系统状态监控
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

**监控指标：**
- 服务健康状态
- 响应时间
- 错误信息
- 系统可用性

## 🔧 使用场景

### 开发环境
```bash
# 快速启动，适合日常开发
python scripts/quick_start.py

# 启动后监控状态
python scripts/monitor_system.py --mode continuous
```

### 测试环境
```bash
# 完整启动，测试所有功能
python scripts/start_system.py

# 测试救援方案生成
python scripts/monitor_system.py --test
```

### 生产环境
```bash
# 使用批处理文件（Windows）
start_system.bat

# 或使用Python脚本
python scripts/start_system.py
```

### 故障排查
```bash
# 检查单个服务状态
python scripts/service_manager.py status emergency

# 重启有问题的服务
python scripts/service_manager.py restart emergency

# 监控系统状态
python scripts/monitor_system.py --mode once
```

## 📊 状态监控

### 服务状态说明
- `[OK]` - 服务正常运行
- `[ERROR]` - 服务异常
- `[TIMEOUT]` - 服务响应超时
- `[UNREACHABLE]` - 服务无法连接
- `[WARNING]` - 服务警告
- `[?]` - 状态未知

### 系统可用性
- **100%** - 所有服务正常
- **80-99%** - 系统基本正常，部分服务异常
- **<80%** - 系统异常，需要检查

## 🛠️ 故障排除

### 常见问题

1. **端口冲突**
   ```bash
   # 检查端口占用
   netstat -an | findstr "8000 8001 8003 8004 3000"
   
   # 脚本会自动处理端口冲突
   ```

2. **Docker未运行**
   ```bash
   # 启动Docker Desktop
   # 检查Docker状态
   docker ps
   ```

3. **服务启动失败**
   ```bash
   # 检查服务日志
   python scripts/service_manager.py status emergency
   
   # 重启服务
   python scripts/service_manager.py restart emergency
   ```

4. **Python模块导入错误**
   ```bash
   # 确保在项目根目录运行
   cd "D:\Fire Emergency RAG System"
   python scripts/start_system.py
   ```

### 日志文件
- `system_startup.log` - 启动日志
- `system_status.log` - 状态监控日志

## 📝 最佳实践

1. **开发时**：使用 `quick_start.py` 快速启动
2. **测试时**：使用 `start_system.py` 完整启动
3. **生产时**：使用 `start_system.bat` 或 `start_system.py`
4. **监控时**：使用 `monitor_system.py` 持续监控
5. **调试时**：使用 `service_manager.py` 管理单个服务

## 🔄 服务依赖关系

```
应急服务 (8000)
├── 需要: 缓存服务 (8004)
├── 需要: Ollama服务 (8003)
├── 可选: 知识图谱服务 (8001)
└── 可选: RAG服务 (3000)

知识图谱服务 (8001)
└── 需要: Neo4j数据库

RAG服务 (3000)
└── 需要: ChromaDB数据库

Ollama服务 (8003)
└── 需要: Ollama容器

缓存服务 (8004)
└── 需要: Redis数据库
```

## 📞 技术支持

如果遇到问题，请：
1. 检查日志文件
2. 使用监控脚本诊断
3. 查看启动指南文档
4. 检查服务依赖关系
