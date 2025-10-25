# PostgreSQL工具说明

## 快速验证PostgreSQL配置

### 使用验证脚本

```bash
# 验证PostgreSQL配置和编码
python scripts/verify_postgres_config.py
```

### 脚本会检查：

1. ✅ **连接状态** - 能否成功连接到PostgreSQL
2. ✅ **服务器编码** - 检查是否为UTF-8
3. ✅ **客户端编码** - 检查是否为UTF-8
4. ✅ **数据库编码** - 检查fire_emergency数据库编码
5. ✅ **中文数据测试** - 测试中文字符的存储和读取
6. ✅ **PostgreSQL版本** - 显示版本信息
7. ✅ **连接数** - 显示当前活动连接
8. ✅ **数据库大小** - 显示数据库占用空间
9. ✅ **扩展检查** - 验证pgcrypto等扩展
10. ✅ **数据表检查** - 列出所有数据表

### 预期输出（成功）：

```
============================================================
  PostgreSQL配置验证
============================================================
时间: 2025-10-25 15:30:00

📡 正在连接PostgreSQL...
✅ PostgreSQL连接
   成功连接到数据库
✅ 服务器编码
   当前编码: UTF8
✅ 客户端编码
   当前编码: UTF8
✅ 数据库编码
   编码: UTF8, Collate: C, Ctype: C.UTF-8

📝 测试中文数据...
✅ 中文数据测试
   测试字符串: 测试中文字符：消防应急救援系统
   返回结果: 测试中文字符：消防应急救援系统
✅ PostgreSQL版本
   PostgreSQL 15.x on x86_64-pc-linux-musl, compiled by gcc
✅ 当前连接数
   3 个活动连接
✅ 数据库大小
   8192 kB

🔌 检查扩展...
✅ 扩展 pgcrypto
   版本 1.3

📊 检查数据表...
✅ 数据表
   找到 5 个表
   - rescue_plans
   - system_logs
   - user_inputs
   - users

============================================================
  验证结果
============================================================
✅ 所有检查通过！PostgreSQL配置正确。

📚 相关文档:
   - 最佳实践: docs/postgresql_best_practices.md
   - 启动指南: docs/startup_guide.md
```

---

## 常见问题解决

### 问题1: 连接失败

**错误信息：**
```
❌ PostgreSQL连接
   连接失败: could not connect to server
```

**解决方案：**
```bash
# 1. 检查PostgreSQL容器是否运行
docker ps | grep postgres

# 2. 如果未运行，启动它
cd "D:\Fire Emergency RAG System\infrastructure\docker"
docker-compose up -d postgres

# 3. 等待30秒后重试
python scripts/verify_postgres_config.py
```

---

### 问题2: 编码不是UTF-8

**错误信息：**
```
❌ 服务器编码
   当前编码: SQL_ASCII
```

**解决方案：**
```bash
# 1. 停止并删除PostgreSQL容器和卷
cd "D:\Fire Emergency RAG System\infrastructure\docker"
docker-compose down -v

# 2. 确认docker-compose.yml中有正确的编码配置
grep -A 3 "POSTGRES_INITDB_ARGS" docker-compose.yml

# 应该看到:
# POSTGRES_INITDB_ARGS: "--encoding=UTF8 --locale=C"
# LANG: C.UTF-8
# LC_ALL: C.UTF-8

# 3. 重新创建容器
docker-compose up -d postgres

# 4. 等待30秒后重新验证
python scripts/verify_postgres_config.py
```

---

### 问题3: 中文数据测试失败

**错误信息：**
```
❌ 中文数据测试
   ⚠️ 期望: 测试中文字符：消防应急救援系统
   ⚠️ 实际: ????????????
```

**解决方案：**

这表示客户端或服务器编码配置不正确。

```bash
# 1. 重建数据库（会丢失所有数据！）
cd "D:\Fire Emergency RAG System\infrastructure\docker"
docker-compose down -v
docker-compose up -d postgres

# 2. 重新初始化数据库
python backend/services/user_service.py
# （服务会自动执行初始化脚本）

# 3. 验证配置
python scripts/verify_postgres_config.py
```

---

### 问题4: 缺少扩展

**错误信息：**
```
🔌 检查扩展...
（没有找到pgcrypto）
```

**解决方案：**
```bash
# 手动创建扩展
docker exec fire_emergency_postgres psql -U postgres -d fire_emergency -c "CREATE EXTENSION IF NOT EXISTS pgcrypto;"

# 验证
python scripts/verify_postgres_config.py
```

---

### 问题5: 缺少数据表

**错误信息：**
```
❌ 数据表
   找到 0 个表
```

**解决方案：**
```bash
# 1. 检查初始化脚本是否执行
docker logs fire_emergency_postgres | grep "init.sql"

# 2. 手动执行初始化脚本
docker exec -i fire_emergency_postgres psql -U postgres -d fire_emergency < infrastructure/docker/postgres/init.sql

# 3. 或者启动用户服务（会自动初始化）
python backend/services/user_service.py

# 4. 验证
python scripts/verify_postgres_config.py
```

---

## 手动命令参考

### 直接连接PostgreSQL

```bash
# 使用psql连接
docker exec -it fire_emergency_postgres psql -U postgres -d fire_emergency

# 在psql中执行命令
\l                              # 列出所有数据库
\c fire_emergency               # 连接到数据库
\dt                             # 列出所有表
\d users                        # 查看users表结构
\q                              # 退出
```

### 检查编码

```bash
# 检查服务器编码
docker exec fire_emergency_postgres psql -U postgres -d fire_emergency -c "SHOW SERVER_ENCODING;"

# 检查客户端编码
docker exec fire_emergency_postgres psql -U postgres -d fire_emergency -c "SHOW CLIENT_ENCODING;"

# 检查数据库编码
docker exec fire_emergency_postgres psql -U postgres -c "SELECT datname, pg_encoding_to_char(encoding) FROM pg_database WHERE datname='fire_emergency';"
```

### 备份和恢复

```bash
# 备份数据库
docker exec fire_emergency_postgres pg_dump -U postgres fire_emergency > backup.sql

# 恢复数据库
docker exec -i fire_emergency_postgres psql -U postgres fire_emergency < backup.sql
```

---

## 相关文档

- **详细最佳实践:** [`docs/postgresql_best_practices.md`](../docs/postgresql_best_practices.md)
- **系统启动指南:** [`docs/startup_guide.md`](../docs/startup_guide.md)
- **项目状态:** [`docs/project_status.md`](../docs/project_status.md)

---

**最后更新:** 2025-10-25

