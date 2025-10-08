# 火灾应急救援RAG系统

## 项目概述

**项目名称**: Fire Emergency RAG System (火灾应急救援RAG系统)  
**项目类型**: 基于知识图谱和RAG技术的智能应急响应系统  
**核心功能**: 接收用户手动输入的物品和环境信息，通过知识图谱检索和RAG技术生成火灾救援方案

## 技术栈

### 后端技术栈
- **主框架**: FastAPI 0.104+ (Python 3.9+)
- **图数据库**: Neo4j 5.15+ (知识图谱存储)
- **关系数据库**: PostgreSQL 15+ (元数据管理)
- **向量数据库**: ChromaDB 0.4+ (RAG检索)
- **大语言模型**: Ollama (本地部署，支持qwen2.5/llama3.1)
- **缓存系统**: Redis 7+ (会话和缓存管理)
- **消息队列**: Celery + Redis (异步任务处理)

### 前端技术栈
- **主框架**: Next.js 14+ (App Router)
- **开发语言**: TypeScript 5.0+
- **样式框架**: Tailwind CSS 3.4+ + Headless UI
- **状态管理**: Zustand + React Query
- **图表可视化**: D3.js + React D3 Tree
- **表单处理**: React Hook Form + Zod

### 部署技术栈
- **容器化**: Docker + Docker Compose
- **反向代理**: Nginx 1.24+
- **CI/CD**: GitHub Actions
- **监控系统**: Prometheus + Grafana

## 系统架构

### 数据流架构
```
用户手动输入 → 物品列表+环境 → API接口 → 知识图谱检索 → RAG增强 → Ollama生成 → 救援方案
```

### 核心模块
1. **应急服务模块**: 核心协调者，处理用户输入并协调各服务
2. **知识图谱服务**: 管理Neo4j图数据库，提供知识检索和推理
3. **RAG服务**: 基于ChromaDB的向量检索和文档增强
4. **Ollama服务**: 集成本地大语言模型，生成救援方案
5. **缓存服务**: 提供高性能缓存，优化系统响应速度
6. **用户服务**: 用户认证、授权和权限管理

## 项目结构

```
fire-emergency-rag/
├── backend/                    # 后端服务
│   ├── app/                   # 应用代码
│   ├── config/                # 配置文件
│   ├── models/                # 数据模型
│   ├── services/              # 服务模块
│   └── utils/                 # 工具函数
├── frontend/                   # 前端应用
├── infrastructure/             # 基础设施配置
│   ├── docker/                # Docker配置
│   ├── kubernetes/            # K8s配置
│   ├── terraform/             # 基础设施即代码
│   └── monitoring/            # 监控配置
├── docs/                      # 项目文档
├── scripts/                   # 脚本文件
├── tests/                     # 测试文件
├── data/                      # 数据文件
└── .cursor/                   # Cursor IDE配置
```

## 快速开始

### 环境要求
- Python 3.9+
- Node.js 18+
- Docker & Docker Compose
- Git

### 一键启动（推荐）

**Windows用户：**
```bash
# 克隆项目
git clone https://github.com/lnlll162/Fire-Emergency-RAG-System.git
cd Fire-Emergency-RAG-System

# 一键启动开发环境
scripts\start_dev.bat
```

**Linux/Mac用户：**
```bash
# 克隆项目
git clone https://github.com/lnlll162/Fire-Emergency-RAG-System.git
cd Fire-Emergency-RAG-System

# 一键启动开发环境
./scripts/start_dev.sh
```

### 手动安装步骤

1. **克隆项目**
```bash
git clone https://github.com/lnlll162/Fire-Emergency-RAG-System.git
cd Fire-Emergency-RAG-System
```

2. **配置环境变量**
```bash
# 复制环境变量模板
cp env.example .env
# 根据需要修改 .env 文件
```

3. **启动数据库服务**
```bash
docker-compose up -d postgres redis neo4j chromadb ollama
```

4. **初始化数据库**
```bash
python scripts/setup_databases.py
```

5. **安装后端依赖**
```bash
pip install -r requirements.txt
```

6. **启动开发服务器**
```bash
# 后端服务
uvicorn app.main:app --reload

# 前端服务（待开发）
cd frontend
npm install
npm run dev
```

## 开发进度

### ✅ 已完成 (v0.2.0)
- [x] 项目架构设计
- [x] 技术栈选型
- [x] 数据库设计
- [x] API接口设计
- [x] 项目基础设施搭建
- [x] 共享基础库开发
- [x] Docker环境配置
- [x] 数据库初始化脚本
- [x] RAG服务开发 (100%)
- [x] 知识图谱服务开发 (100%)
- [x] 知识库构建
- [x] 系统集成测试 (93.3%通过率)

### ⏳ 进行中
- [ ] Ollama服务开发 (0%)
- [ ] 缓存服务开发 (0%)
- [ ] 用户服务开发 (0%)

### 📋 待开发
- [ ] 管理服务开发
- [ ] 用户输入服务开发
- [ ] 应急服务开发
- [ ] 前端界面开发
- [ ] 部署上线

**详细进度**: [项目状态报告](docs/project_status.md)

## 贡献指南

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开 Pull Request

## 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情

## 联系方式

- 项目链接: [https://github.com/lnlll162/Fire-Emergency-RAG-System](https://github.com/lnlll162/Fire-Emergency-RAG-System)
- 问题反馈: [Issues](https://github.com/lnlll162/Fire-Emergency-RAG-System/issues)

## 致谢

感谢所有为这个项目做出贡献的开发者和开源社区。
