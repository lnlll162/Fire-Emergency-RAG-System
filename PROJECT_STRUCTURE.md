# 🏗️ 消防应急RAG系统 - 项目结构说明

## 📁 目录结构

```
Fire Emergency RAG System/
│
├── backend/                      # 后端服务代码
│   ├── app/                      # FastAPI应用
│   ├── config/                   # 配置文件
│   │   └── ollama_config.json    # Ollama模型配置
│   ├── database/                 # 数据库模块
│   │   ├── user_database.py      # 用户数据库操作
│   │   └── user_schema.sql       # 数据库模式定义
│   ├── models/                   # 数据模型
│   ├── services/                 # 微服务（8个服务）
│   │   ├── admin_service.py      # 管理服务 (8005)
│   │   ├── cache_service.py      # 缓存服务 (8004)
│   │   ├── emergency_service.py  # 应急服务 (8000) ⭐核心
│   │   ├── knowledge_graph_service.py  # 知识图谱 (8001)
│   │   ├── ollama_service.py     # AI生成服务 (8003)
│   │   ├── rag_service.py        # RAG检索 (3000)
│   │   ├── user_input_service.py # 用户输入处理 (8006)
│   │   └── user_service.py       # 用户管理 (8002)
│   └── utils/                    # 工具函数
│
├── frontend/                     # Next.js前端应用
│   ├── src/
│   │   ├── app/                  # 页面路由
│   │   │   ├── admin/            # 系统管理页面
│   │   │   ├── emergency/        # 应急查询页面 ⭐核心
│   │   │   ├── knowledge/        # 知识图谱页面
│   │   │   └── layout.tsx        # 主布局
│   │   ├── components/           # React组件
│   │   │   └── ui/               # UI基础组件
│   │   └── lib/                  # 工具库
│   │       └── api.ts            # API调用封装
│   ├── package.json              # 依赖配置（端口3001）
│   └── next.config.ts            # Next.js配置
│
├── infrastructure/               # 基础设施配置
│   ├── docker/                   # Docker配置
│   │   ├── docker-compose.yml    # 容器编排 ⭐重要
│   │   ├── postgres/             # PostgreSQL初始化
│   │   │   └── init.sql
│   │   └── services/             # 服务配置文件
│   ├── kubernetes/               # K8s配置（未使用）
│   ├── monitoring/               # 监控配置
│   └── terraform/                # IaC配置
│
├── scripts/                      # 脚本集合
│   ├── database/                 # 数据库管理脚本 🆕
│   │   ├── init_postgres_schema.py    # 初始化数据库
│   │   ├── reset_postgres_schema.py   # 重置数据库
│   │   └── README.md
│   ├── data_initialization/      # 数据初始化
│   │   └── init_databases.py
│   ├── data_management/          # 数据管理
│   │   ├── add_new_data.py
│   │   └── quick_add.py
│   ├── start_*.py                # 服务启动脚本（7个）
│   ├── verify_system_status.py   # 系统状态验证
│   ├── service_manager.py        # 服务管理器
│   ├── restart_emergency_service.bat  # 快速重启应急服务 🆕
│   ├── fix_neo4j.bat             # Neo4j修复工具
│   └── README.md
│
├── shared/                       # 共享代码
│   ├── config.py                 # 配置管理
│   ├── models.py                 # 数据模型
│   ├── service_registry.py       # 服务注册
│   ├── http_client.py            # HTTP客户端
│   └── exceptions.py             # 异常定义
│
├── data/                         # 数据文件
│   ├── knowledge_base/           # 知识库数据
│   │   ├── rag_documents.json    # RAG文档
│   │   └── *.cypher              # Neo4j导入脚本
│   └── samples/                  # 示例数据
│
├── models/                       # AI模型文件
│   ├── embeddings/               # 嵌入模型
│   │   └── model_info.json
│   └── blobs/                    # 模型二进制（.gitignore）
│
├── docs/                         # 文档目录 📚
│   ├── startup_guide.md          # 启动指南 ⭐必读
│   ├── troubleshooting_guide.md  # 故障排查
│   ├── project_status.md         # 项目状态
│   ├── *_service_api.md          # 各服务API文档（8个）
│   ├── neo4j_*.md                # Neo4j相关文档
│   └── postgresql_best_practices.md
│
├── tests/                        # 测试代码
│   ├── test_*_service.py         # 单元测试（9个）
│   └── README.md
│
├── reports/                      # 验证报告
│   └── *.json
│
├── .env.example                  # 环境变量模板
├── .gitignore                    # Git忽略配置
├── requirements-py313.txt        # Python依赖
├── README.md                     # 项目说明 ⭐入口
├── PROJECT_STRUCTURE.md          # 本文件 🆕
└── system_verification_report.md # 系统验证报告
```

## 🚀 核心文件说明

### 必读文档
1. **README.md** - 项目概述和快速开始
2. **docs/startup_guide.md** - 详细启动指南
3. **docs/troubleshooting_guide.md** - 常见问题解决

### 核心服务
1. **backend/services/emergency_service.py** (端口8000)
   - 系统核心协调服务
   - 整合所有其他服务
   - 提供应急查询API

2. **backend/services/ollama_service.py** (端口8003)
   - AI文本生成
   - 救援方案生成
   - 支持多种Ollama模型

3. **backend/services/knowledge_graph_service.py** (端口8001)
   - 材质和环境知识查询
   - Neo4j图数据库操作

4. **backend/services/rag_service.py** (端口3000)
   - 文档检索
   - ChromaDB向量数据库

### 启动脚本
- **scripts/start_system.py** - 一键启动所有服务
- **scripts/service_manager.py** - 服务管理器
- **scripts/start_*_service.py** - 单个服务启动（7个）

### 数据库脚本 🆕
- **scripts/database/init_postgres_schema.py** - 初始化数据库
- **scripts/database/reset_postgres_schema.py** - 重置数据库

### Docker配置
- **infrastructure/docker/docker-compose.yml** - 容器编排
  - PostgreSQL (5432)
  - Redis (6379)
  - Neo4j (7474/7687)
  - ChromaDB (8007)
  - Ollama (11434)

## 🔧 快速操作

### 启动系统
```bash
python scripts/start_system.py
```

### 重启应急服务
```bash
scripts\restart_emergency_service.bat
```

### 初始化数据库
```bash
python scripts/database/init_postgres_schema.py
```

### 验证系统状态
```bash
python scripts/verify_system_status.py
```

## 📝 文件命名规范

### Python脚本
- `start_*.py` - 服务启动脚本
- `test_*.py` - 测试脚本（.gitignore）
- `verify_*.py` - 验证脚本

### 文档
- `*_api.md` - API文档
- `*_guide.md` - 使用指南
- `*_troubleshooting.md` - 故障排查

### 配置文件
- `*.json` - JSON配置
- `*.sql` - SQL脚本
- `*.cypher` - Neo4j Cypher脚本

## 🗑️ .gitignore 规则

以下文件类型会被Git忽略：
- `__pycache__/` - Python缓存
- `*.log` - 日志文件
- `test_*.py` - 临时测试脚本
- `test_*.json` - 测试数据
- `models/blobs/` - AI模型二进制
- `reports/*.json` - 验证报告
- `.env` - 环境变量

## 📚 相关资源

- [启动指南](docs/startup_guide.md)
- [API文档索引](docs/)
- [故障排查](docs/troubleshooting_guide.md)
- [Neo4j解决方案](docs/neo4j_solution_summary.md)
- [PostgreSQL最佳实践](docs/postgresql_best_practices.md)

## 🎯 项目状态

查看 [docs/project_status.md](docs/project_status.md) 了解当前进度和待办事项。

---

**更新时间**: 2025-10-25  
**维护者**: 项目团队

