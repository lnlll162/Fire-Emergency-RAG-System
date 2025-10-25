# 数据库管理脚本

本目录包含数据库初始化和管理脚本。

## 📜 脚本列表

### `init_postgres_schema.py`
**功能**: 初始化PostgreSQL数据库模式
- 创建用户表、会话表等
- 设置必要的索引和触发器
- 初始化默认数据

**使用方法**:
```bash
cd "D:\Fire Emergency RAG System"
python scripts/database/init_postgres_schema.py
```

**前提条件**:
- PostgreSQL容器正在运行
- 数据库配置正确（.env文件）

---

### `reset_postgres_schema.py`
**功能**: 重置PostgreSQL数据库（清空所有数据）
- 删除所有表
- 重新创建表结构
- ⚠️ **警告**: 会清空所有用户数据！

**使用方法**:
```bash
cd "D:\Fire Emergency RAG System"
python scripts/database/reset_postgres_schema.py
```

**使用场景**:
- 开发环境数据损坏需要重置
- 需要清空测试数据
- 数据库结构需要完全重建

**⚠️ 注意事项**:
- 生产环境禁止使用！
- 执行前请确认数据已备份
- 会清空所有用户账户和历史记录

---

## 🔄 常见操作

### 首次安装系统
```bash
# 1. 启动Docker容器
cd infrastructure/docker
docker-compose up -d

# 2. 等待容器健康
docker ps

# 3. 初始化数据库
python scripts/database/init_postgres_schema.py
```

### 数据库损坏恢复
```bash
# 1. 重置数据库
python scripts/database/reset_postgres_schema.py

# 2. 重新初始化
python scripts/database/init_postgres_schema.py
```

---

## 📚 相关文档
- [数据库最佳实践](../../docs/postgresql_best_practices.md)
- [系统启动指南](../../docs/startup_guide.md)
- [故障排查指南](../../docs/troubleshooting_guide.md)

