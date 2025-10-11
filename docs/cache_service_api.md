# 缓存服务 API 文档

## 概述

缓存服务提供高性能的Redis缓存功能，包括缓存CRUD操作、批量操作、缓存策略、预热功能等。

**服务地址**: `http://localhost:8004`  
**API文档**: `http://localhost:8004/docs`  
**ReDoc文档**: `http://localhost:8004/redoc`

## 核心功能

- ✅ **Redis连接管理** - 连接池、健康检查、重连机制
- ✅ **缓存CRUD操作** - 增删改查、批量操作、过期管理
- ✅ **缓存策略** - LRU、TTL、缓存穿透保护、缓存雪崩防护
- ✅ **缓存预热** - 启动时预加载、定时刷新、智能预热
- ✅ **命名空间隔离** - 支持多租户缓存隔离
- ✅ **统计监控** - 命中率、内存使用、连接数等

## API 端点

### 1. 基础信息

#### GET /
获取服务基本信息

**响应示例**:
```json
{
  "success": true,
  "data": {
    "service": "缓存服务",
    "version": "1.0.0",
    "description": "高性能缓存服务",
    "endpoints": {
      "health": "/health",
      "get": "/get/{key}",
      "set": "/set",
      "delete": "/delete/{key}",
      "exists": "/exists/{key}",
      "keys": "/keys",
      "stats": "/stats",
      "warmup": "/warmup",
      "batch": "/batch",
      "docs": "/docs"
    }
  },
  "message": "缓存服务运行正常"
}
```

### 2. 健康检查

#### GET /health
检查服务健康状态

**响应示例**:
```json
{
  "success": true,
  "data": {
    "status": "healthy",
    "connected": true,
    "version": "7.0.0",
    "uptime": 3600,
    "memory_usage": "1MB",
    "connected_clients": 5
  },
  "message": "健康检查完成"
}
```

### 3. 缓存操作

#### GET /get/{key}
获取缓存值

**参数**:
- `key` (string): 缓存键
- `namespace` (string, 可选): 命名空间，默认为 "default"

**响应示例**:
```json
{
  "success": true,
  "data": "cached_value",
  "message": "获取成功",
  "execution_time": 1.5,
  "timestamp": "2024-01-01T12:00:00Z"
}
```

#### POST /set
设置缓存值

**参数**:
- `key` (string): 缓存键
- `value` (any): 缓存值
- `ttl` (int, 可选): 生存时间(秒)，1-86400
- `namespace` (string, 可选): 命名空间，默认为 "default"
- `strategy` (string, 可选): 缓存策略，默认为 "ttl"

**支持的策略**:
- `lru`: 最近最少使用
- `lfu`: 最少使用频率
- `ttl`: 基于时间过期
- `fifo`: 先进先出

**响应示例**:
```json
{
  "success": true,
  "data": true,
  "message": "设置成功",
  "execution_time": 2.1,
  "timestamp": "2024-01-01T12:00:00Z"
}
```

#### DELETE /delete/{key}
删除缓存值

**参数**:
- `key` (string): 缓存键
- `namespace` (string, 可选): 命名空间，默认为 "default"

**响应示例**:
```json
{
  "success": true,
  "data": true,
  "message": "删除成功",
  "execution_time": 1.2,
  "timestamp": "2024-01-01T12:00:00Z"
}
```

#### GET /exists/{key}
检查键是否存在

**参数**:
- `key` (string): 缓存键
- `namespace` (string, 可选): 命名空间，默认为 "default"

**响应示例**:
```json
{
  "success": true,
  "data": true,
  "message": "键存在",
  "execution_time": 0.8,
  "timestamp": "2024-01-01T12:00:00Z"
}
```

#### GET /keys
获取键列表

**参数**:
- `pattern` (string, 可选): 匹配模式，默认为 "*"
- `namespace` (string, 可选): 命名空间，默认为 "default"

**响应示例**:
```json
{
  "success": true,
  "data": ["key1", "key2", "key3"],
  "message": "找到 3 个键",
  "timestamp": "2024-01-01T12:00:00Z"
}
```

### 4. 统计信息

#### GET /stats
获取缓存统计信息

**响应示例**:
```json
{
  "success": true,
  "data": {
    "total_keys": 100,
    "memory_usage": 1024000,
    "hit_count": 80,
    "miss_count": 20,
    "hit_rate": 0.8,
    "eviction_count": 5,
    "connection_count": 10,
    "uptime": 3600.0
  },
  "message": "统计信息获取成功"
}
```

### 5. 缓存预热

#### POST /warmup
缓存预热

**请求体**:
```json
{
  "key1": "value1",
  "key2": "value2",
  "key3": {"nested": "object"}
}
```

**参数**:
- `namespace` (string, 可选): 命名空间，默认为 "default"

**响应示例**:
```json
{
  "success": true,
  "data": {
    "warmed_up": true,
    "count": 3
  },
  "message": "缓存预热成功"
}
```

### 6. 批量操作

#### POST /batch
批量执行缓存操作

**请求体**:
```json
{
  "operations": [
    {
      "key": "key1",
      "value": "value1",
      "operation": "set",
      "ttl": 3600
    },
    {
      "key": "key2",
      "operation": "get"
    },
    {
      "key": "key1",
      "operation": "exists"
    }
  ],
  "atomic": true
}
```

**参数**:
- `namespace` (string, 可选): 命名空间，默认为 "default"

**支持的操作**:
- `get`: 获取值
- `set`: 设置值
- `delete`: 删除值
- `exists`: 检查存在性
- `expire`: 设置过期时间
- `ttl`: 获取剩余时间

**响应示例**:
```json
{
  "success": true,
  "data": [
    {
      "success": true,
      "data": true,
      "message": "操作 set 执行成功",
      "execution_time": 0.0
    },
    {
      "success": true,
      "data": "value2",
      "message": "操作 get 执行成功",
      "execution_time": 0.0
    },
    {
      "success": true,
      "data": true,
      "message": "操作 exists 执行成功",
      "execution_time": 0.0
    }
  ],
  "message": "批量操作完成，共 3 个操作"
}
```

### 7. 清空缓存

#### POST /flush
清空缓存

**参数**:
- `namespace` (string, 可选): 命名空间，默认为 "default"，设置为 "all" 清空所有

**响应示例**:
```json
{
  "success": true,
  "data": {
    "flushed": true,
    "namespace": "default"
  },
  "message": "缓存清空成功"
}
```

## 使用示例

### Python 客户端示例

```python
import httpx
import asyncio

async def cache_example():
    base_url = "http://localhost:8004"
    
    async with httpx.AsyncClient() as client:
        # 1. 设置缓存
        response = await client.post(
            f"{base_url}/set",
            params={
                "key": "user:123",
                "value": {"name": "张三", "age": 25},
                "ttl": 3600,
                "namespace": "users"
            }
        )
        print("设置缓存:", response.json())
        
        # 2. 获取缓存
        response = await client.get(
            f"{base_url}/get/user:123",
            params={"namespace": "users"}
        )
        print("获取缓存:", response.json())
        
        # 3. 批量操作
        batch_request = {
            "operations": [
                {"key": "key1", "value": "value1", "operation": "set"},
                {"key": "key2", "operation": "get"},
                {"key": "key1", "operation": "exists"}
            ],
            "atomic": True
        }
        
        response = await client.post(
            f"{base_url}/batch",
            json=batch_request
        )
        print("批量操作:", response.json())
        
        # 4. 获取统计信息
        response = await client.get(f"{base_url}/stats")
        print("统计信息:", response.json())

# 运行示例
asyncio.run(cache_example())
```

### JavaScript 客户端示例

```javascript
const baseUrl = 'http://localhost:8004';

async function cacheExample() {
    try {
        // 1. 设置缓存
        const setResponse = await fetch(`${baseUrl}/set?key=user:123&value=${encodeURIComponent(JSON.stringify({name: '张三', age: 25}))}&ttl=3600&namespace=users`, {
            method: 'POST'
        });
        console.log('设置缓存:', await setResponse.json());
        
        // 2. 获取缓存
        const getResponse = await fetch(`${baseUrl}/get/user:123?namespace=users`);
        console.log('获取缓存:', await getResponse.json());
        
        // 3. 批量操作
        const batchResponse = await fetch(`${baseUrl}/batch`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                operations: [
                    {key: 'key1', value: 'value1', operation: 'set'},
                    {key: 'key2', operation: 'get'},
                    {key: 'key1', operation: 'exists'}
                ],
                atomic: true
            })
        });
        console.log('批量操作:', await batchResponse.json());
        
        // 4. 获取统计信息
        const statsResponse = await fetch(`${baseUrl}/stats`);
        console.log('统计信息:', await statsResponse.json());
        
    } catch (error) {
        console.error('错误:', error);
    }
}

// 运行示例
cacheExample();
```

## 错误处理

### 常见错误码

- `400`: 请求参数错误
- `500`: 服务器内部错误
- `503`: 服务不可用（Redis连接失败）

### 错误响应格式

```json
{
  "success": false,
  "data": null,
  "message": "错误描述",
  "timestamp": "2024-01-01T12:00:00Z"
}
```

## 性能优化建议

1. **使用连接池**: 服务已配置连接池，避免频繁创建连接
2. **合理设置TTL**: 根据数据特性设置合适的过期时间
3. **使用命名空间**: 避免键冲突，提高查询效率
4. **批量操作**: 优先使用批量操作减少网络开销
5. **监控统计**: 定期查看命中率和内存使用情况

## 配置说明

### 环境变量

- `REDIS_HOST`: Redis主机地址 (默认: localhost)
- `REDIS_PORT`: Redis端口 (默认: 6379)
- `REDIS_PASSWORD`: Redis密码 (可选)
- `REDIS_DB`: Redis数据库编号 (默认: 0)
- `REDIS_POOL_SIZE`: 连接池大小 (默认: 20)

### Docker 部署

```bash
# 启动缓存服务
docker-compose up cache_service

# 查看日志
docker-compose logs cache_service

# 停止服务
docker-compose down
```

## 监控和运维

### 健康检查

```bash
curl http://localhost:8004/health
```

### 性能监控

```bash
# 获取统计信息
curl http://localhost:8004/stats

# 获取键列表
curl http://localhost:8004/keys
```

### 日志查看

```bash
# Docker 环境
docker-compose logs -f cache_service

# 本地环境
python scripts/start_cache_service.py
```

## 更新日志

### v1.0.0 (2024-01-01)
- ✅ 初始版本发布
- ✅ 基础缓存CRUD操作
- ✅ 批量操作支持
- ✅ 缓存预热功能
- ✅ 统计监控功能
- ✅ 命名空间隔离
- ✅ 单元测试覆盖
