# PostgreSQL 最佳实践 - 避免编码和连接问题

## 📋 问题总结

### 之前遇到的问题：
1. **GBK编码错误** - Windows PostgreSQL默认使用GBK编码
2. **连接编码不一致** - 客户端和服务器编码不匹配
3. **中文字符乱码** - 数据存储和读取编码不统一
4. **认证失败** - 密码或连接配置错误

---

## ✅ 解决方案（已实施）

### 1. **Docker PostgreSQL配置**（推荐方式）

#### `docker-compose.yml` 中的关键配置：

```yaml
postgres:
  image: postgres:15-alpine
  environment:
    POSTGRES_DB: fire_emergency
    POSTGRES_USER: postgres
    POSTGRES_PASSWORD: password
    # 关键：强制UTF-8编码
    POSTGRES_INITDB_ARGS: "--encoding=UTF8 --locale=C"
    LANG: C.UTF-8
    LC_ALL: C.UTF-8
```

**说明：**
- `POSTGRES_INITDB_ARGS`: 数据库初始化时使用UTF-8编码
- `LANG` 和 `LC_ALL`: 设置容器环境的语言编码
- `--locale=C`: 使用C locale避免本地化问题

---

### 2. **Python客户端配置**

#### `backend/database/user_database.py` 中的关键配置：

```python
# 1. 环境变量设置（文件开头）
os.environ['PGCLIENTENCODING'] = 'UTF8'
os.environ['PGOPTIONS'] = '--client-encoding=UTF8'

# Windows特殊处理
if sys.platform == 'win32':
    try:
        locale.setlocale(locale.LC_ALL, 'C')
    except:
        pass

# 2. 连接字符串配置
def _build_connection_string(self) -> str:
    host = self.config.database.postgres_host
    # 避免 Windows 下 IPv6/解析问题
    if host == "localhost":
        host = "127.0.0.1"
    return (
        f"host={host} "
        f"port={self.config.database.postgres_port} "
        f"dbname={self.config.database.postgres_db} "
        f"user={self.config.database.postgres_user} "
        f"password={self.config.database.postgres_password} "
        f"sslmode=disable connect_timeout=10 client_encoding=UTF8"
    )

# 3. 每个连接强制设置编码
def initialize(self):
    test_conn = psycopg2.connect(self._connection_string)
    test_conn.set_client_encoding('UTF8')
    with test_conn.cursor() as cur:
        cur.execute("SET client_encoding TO 'UTF8'")
```

**关键点：**
- ✅ 环境变量预设编码
- ✅ localhost → 127.0.0.1（避免IPv6问题）
- ✅ 连接字符串指定 `client_encoding=UTF8`
- ✅ 连接后再次确认编码设置

---

### 3. **SQL文件编码**

#### `infrastructure/docker/postgres/init.sql`:

```sql
-- 确保文件本身是UTF-8编码保存
-- 启用pgcrypto扩展
CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- 创建表时使用TEXT类型存储中文
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    username VARCHAR(50) UNIQUE NOT NULL,
    full_name VARCHAR(100),  -- 支持中文姓名
    ...
);
```

**注意事项：**
- ✅ SQL文件必须使用UTF-8编码保存（无BOM）
- ✅ 使用 `TEXT` 或 `VARCHAR` 存储中文，不要使用 `CHAR`
- ✅ 避免在SQL文件中使用特殊字符

---

## 🔍 如何确保下次不出现这些问题

### **检查清单（Checklist）**

#### ✅ 启动前检查

1. **确认Docker配置正确**
```bash
# 检查docker-compose.yml中的环境变量
cd "D:\Fire Emergency RAG System\infrastructure\docker"
grep -A 5 "POSTGRES_INITDB_ARGS" docker-compose.yml
```

应该看到：
```
POSTGRES_INITDB_ARGS: "--encoding=UTF8 --locale=C"
LANG: C.UTF-8
LC_ALL: C.UTF-8
```

2. **验证PostgreSQL容器编码**
```bash
# 启动容器后检查编码
docker exec fire_emergency_postgres psql -U postgres -d fire_emergency -c "SHOW SERVER_ENCODING;"
docker exec fire_emergency_postgres psql -U postgres -d fire_emergency -c "SHOW CLIENT_ENCODING;"
```

应该都返回 `UTF8`。

3. **测试中文数据存储**
```bash
# 创建测试脚本
python -c "
import psycopg2
conn = psycopg2.connect('host=127.0.0.1 port=5432 dbname=fire_emergency user=postgres password=password client_encoding=UTF8')
conn.set_client_encoding('UTF8')
cur = conn.cursor()
cur.execute(\"SELECT '测试中文'::text\")
print(cur.fetchone())
conn.close()
"
```

应该正确显示中文。

---

#### ✅ 代码检查

**在修改Python代码时，确保：**

1. **数据库连接代码包含编码设置**
```python
# ❌ 错误示例
conn = psycopg2.connect("host=localhost port=5432 dbname=fire_emergency user=postgres password=password")

# ✅ 正确示例
conn = psycopg2.connect(
    "host=127.0.0.1 port=5432 dbname=fire_emergency user=postgres password=password client_encoding=UTF8"
)
conn.set_client_encoding('UTF8')
```

2. **读取SQL文件时指定UTF-8编码**
```python
# ❌ 错误示例
with open('schema.sql', 'r') as f:
    sql = f.read()

# ✅ 正确示例
with open('schema.sql', 'r', encoding='utf-8') as f:
    sql = f.read()
```

3. **Windows环境下设置locale**
```python
import sys
import locale

if sys.platform == 'win32':
    try:
        locale.setlocale(locale.LC_ALL, 'C')
    except:
        pass
```

---

#### ✅ 新服务开发

**创建新服务时遵循以下模板：**

```python
#!/usr/bin/env python3
import os
import sys
import locale

# 1. 在导入psycopg2之前设置环境变量
os.environ['PGCLIENTENCODING'] = 'UTF8'
os.environ['PGOPTIONS'] = '--client-encoding=UTF8'

# 2. Windows环境处理
if sys.platform == 'win32':
    try:
        locale.setlocale(locale.LC_ALL, 'C')
    except:
        pass

import psycopg2

# 3. 创建连接池或连接
class MyDatabase:
    def _build_connection_string(self):
        host = "127.0.0.1"  # 不要使用 localhost
        return (
            f"host={host} "
            f"port=5432 "
            f"dbname=fire_emergency "
            f"user=postgres "
            f"password=password "
            f"sslmode=disable "
            f"connect_timeout=10 "
            f"client_encoding=UTF8"
        )
    
    def initialize(self):
        conn = psycopg2.connect(self._connection_string)
        conn.set_client_encoding('UTF8')
        with conn.cursor() as cur:
            cur.execute("SET client_encoding TO 'UTF8'")
```

---

## 🚨 常见错误及解决方案

### 错误1: `UnicodeDecodeError: 'gbk' codec can't decode...`

**原因：** Windows PostgreSQL或Python客户端使用GBK编码

**解决方案：**
```python
# 在文件开头添加
os.environ['PGCLIENTENCODING'] = 'UTF8'
os.environ['PGOPTIONS'] = '--client-encoding=UTF8'
if sys.platform == 'win32':
    locale.setlocale(locale.LC_ALL, 'C')
```

---

### 错误2: `psycopg2.OperationalError: FATAL: password authentication failed`

**原因：** 
- 密码错误
- PostgreSQL未启动
- pg_hba.conf配置问题

**解决方案：**
```bash
# 1. 检查PostgreSQL是否运行
docker ps | grep postgres

# 2. 重启PostgreSQL
docker restart fire_emergency_postgres

# 3. 确认密码
# 检查 .env 文件或 docker-compose.yml 中的 POSTGRES_PASSWORD

# 4. 测试连接
docker exec fire_emergency_postgres psql -U postgres -d fire_emergency -c "SELECT 1"
```

---

### 错误3: 中文数据存储后显示乱码

**原因：** 编码设置不一致

**检查步骤：**
```bash
# 1. 检查数据库编码
docker exec fire_emergency_postgres psql -U postgres -d fire_emergency -c "SHOW SERVER_ENCODING;"

# 2. 检查客户端编码
python -c "import psycopg2; conn=psycopg2.connect('host=127.0.0.1 dbname=fire_emergency user=postgres password=password'); print(conn.encoding)"

# 3. 如果不是UTF8，重新创建数据库
docker-compose down -v
docker-compose up -d postgres
```

---

### 错误4: `could not connect to server: Connection refused`

**原因：** 
- Docker容器未启动
- 端口被占用
- 防火墙阻止

**解决方案：**
```bash
# 1. 检查容器状态
docker-compose ps

# 2. 查看容器日志
docker logs fire_emergency_postgres

# 3. 检查端口占用
netstat -ano | findstr :5432

# 4. 重启服务
cd "D:\Fire Emergency RAG System\infrastructure\docker"
docker-compose restart postgres
```

---

## 📝 维护建议

### 定期检查（每周）

```bash
# 1. 检查数据库编码
docker exec fire_emergency_postgres psql -U postgres -d fire_emergency -c "
SELECT 
    datname, 
    pg_encoding_to_char(encoding) as encoding,
    datcollate,
    datctype
FROM pg_database 
WHERE datname='fire_emergency';
"

# 2. 检查连接数
docker exec fire_emergency_postgres psql -U postgres -c "
SELECT count(*) as connections, state 
FROM pg_stat_activity 
WHERE datname='fire_emergency' 
GROUP BY state;
"

# 3. 检查数据库大小
docker exec fire_emergency_postgres psql -U postgres -c "
SELECT 
    pg_size_pretty(pg_database_size('fire_emergency')) as size;
"
```

### 备份策略

```bash
# 每天备份数据库
docker exec fire_emergency_postgres pg_dump -U postgres fire_emergency > backup_$(date +%Y%m%d).sql

# 恢复备份
docker exec -i fire_emergency_postgres psql -U postgres fire_emergency < backup_20251025.sql
```

---

## 🎯 总结

### **三个黄金法则：**

1. **使用Docker PostgreSQL** - 避免Windows本地PostgreSQL的编码问题
2. **始终显式指定UTF-8编码** - 在所有连接和配置中
3. **使用127.0.0.1而不是localhost** - 避免IPv6解析问题

### **快速验证命令：**

```bash
# 一键验证PostgreSQL配置
python -c "
import psycopg2
import os
os.environ['PGCLIENTENCODING'] = 'UTF8'
conn = psycopg2.connect('host=127.0.0.1 port=5432 dbname=fire_emergency user=postgres password=password client_encoding=UTF8')
conn.set_client_encoding('UTF8')
cur = conn.cursor()
cur.execute('SELECT version(), current_setting(\\'server_encoding\\'), current_setting(\\'client_encoding\\')')
version, server_enc, client_enc = cur.fetchone()
print(f'服务器编码: {server_enc}')
print(f'客户端编码: {client_enc}')
print('✅ PostgreSQL配置正确' if server_enc == 'UTF8' and client_enc == 'UTF8' else '❌ 编码配置错误')
conn.close()
"
```

---

## 📚 参考资料

- [PostgreSQL Character Set Support](https://www.postgresql.org/docs/current/multibyte.html)
- [psycopg2 Documentation](https://www.psycopg.org/docs/)
- [Docker PostgreSQL Official Image](https://hub.docker.com/_/postgres)

---

**最后更新:** 2025-10-25  
**维护者:** Fire Emergency RAG System Team

