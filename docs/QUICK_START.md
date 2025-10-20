# 快速启动指南

## 🚀 一键启动系统

### 前提条件
- Docker Desktop 正在运行
- Python 3.13+ 已安装

### 启动步骤

1. **切换到项目目录**
```bash
cd "D:\Fire Emergency RAG System"
```

2. **一键启动**
```bash
python scripts/start_system.py
```

3. **验证系统状态**
```bash
python scripts/verify_system_status.py
```

### 访问地址
- **前端界面**: http://localhost:3001
- **API文档**: http://localhost:8000/docs

### 故障排除
如果启动失败，请：
1. 确保Docker Desktop正在运行
2. 检查端口是否被占用
3. 重新运行启动脚本

---

**注意**: 这是唯一推荐的启动方法，其他方法可能导致系统不稳定。
