# 用户服务 API 文档

## 概述

用户服务提供用户认证、授权和权限管理功能，包括用户注册、登录、JWT令牌管理、角色权限控制等。

**服务地址**: `http://localhost:8002`  
**API文档**: `http://localhost:8002/docs`

## 认证方式

用户服务使用JWT (JSON Web Token) 进行认证。需要在请求头中包含访问令牌：

```
Authorization: Bearer <access_token>
```

## API 端点

### 1. 健康检查

#### GET /health

检查服务健康状态。

**响应示例**:
```json
{
  "success": true,
  "message": "健康检查完成",
  "data": {
    "status": "healthy"
  }
}
```

### 2. 用户注册

#### POST /register

注册新用户。

**请求体**:
```json
{
  "username": "test_user",
  "email": "test@example.com",
  "password": "TestPass123",
  "confirm_password": "TestPass123",
  "full_name": "测试用户",
  "phone": "13800138001",
  "role": "user"
}
```

**字段说明**:
- `username`: 用户名，3-50个字符
- `email`: 邮箱地址，必须有效
- `password`: 密码，至少8位，包含大小写字母和数字
- `confirm_password`: 确认密码，必须与密码一致
- `full_name`: 全名，可选
- `phone`: 手机号，可选
- `role`: 用户角色，可选值：admin, operator, user, guest

**响应示例**:
```json
{
  "success": true,
  "message": "用户注册成功",
  "data": {
    "id": "user_id",
    "username": "test_user",
    "email": "test@example.com",
    "full_name": "测试用户",
    "phone": "13800138001",
    "role": "user",
    "status": "active",
    "created_at": "2025-01-11T12:00:00Z",
    "updated_at": "2025-01-11T12:00:00Z"
  }
}
```

### 3. 用户登录

#### POST /login

用户登录获取访问令牌。

**请求体**:
```json
{
  "username": "test_user",
  "password": "TestPass123"
}
```

**响应示例**:
```json
{
  "success": true,
  "message": "登录成功",
  "data": {
    "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "token_type": "bearer",
    "expires_in": 1800
  }
}
```

### 4. 用户登出

#### POST /logout

用户登出，使令牌失效。

**请求头**:
```
Authorization: Bearer <access_token>
```

**响应示例**:
```json
{
  "success": true,
  "message": "登出成功"
}
```

### 5. 获取用户信息

#### GET /profile

获取当前用户信息。

**请求头**:
```
Authorization: Bearer <access_token>
```

**响应示例**:
```json
{
  "success": true,
  "message": "获取用户信息成功",
  "data": {
    "id": "user_id",
    "username": "test_user",
    "email": "test@example.com",
    "full_name": "测试用户",
    "phone": "13800138001",
    "role": "user",
    "status": "active",
    "created_at": "2025-01-11T12:00:00Z",
    "updated_at": "2025-01-11T12:00:00Z",
    "last_login": "2025-01-11T12:30:00Z"
  }
}
```

## 用户角色和权限

### 角色定义

1. **admin**: 管理员
   - 拥有所有权限
   - 可以管理用户、系统配置等

2. **operator**: 操作员
   - 可以创建、查看、更新、删除救援方案
   - 可以查看知识库和日志

3. **user**: 普通用户
   - 可以创建和查看救援方案
   - 可以查看知识库

4. **guest**: 访客
   - 只能查看救援方案和知识库

### 权限列表

- `create_user`: 创建用户
- `read_user`: 查看用户
- `update_user`: 更新用户
- `delete_user`: 删除用户
- `create_rescue_plan`: 创建救援方案
- `read_rescue_plan`: 查看救援方案
- `update_rescue_plan`: 更新救援方案
- `delete_rescue_plan`: 删除救援方案
- `manage_knowledge`: 管理知识库
- `view_knowledge`: 查看知识库
- `manage_system`: 管理系统
- `view_logs`: 查看日志
- `manage_config`: 管理配置

## 错误处理

### 常见错误码

- `400`: 请求参数错误
- `401`: 认证失败
- `403`: 权限不足
- `404`: 资源不存在
- `409`: 资源冲突（如用户名已存在）
- `500`: 服务器内部错误

### 错误响应格式

```json
{
  "success": false,
  "message": "错误描述",
  "data": null
}
```

## 使用示例

### Python 示例

```python
import httpx
import asyncio

async def test_user_service():
    base_url = "http://localhost:8002"
    
    async with httpx.AsyncClient() as client:
        # 1. 注册用户
        register_data = {
            "username": "test_user",
            "email": "test@example.com",
            "password": "TestPass123",
            "confirm_password": "TestPass123",
            "role": "user"
        }
        
        response = await client.post(f"{base_url}/register", json=register_data)
        print("注册结果:", response.json())
        
        # 2. 用户登录
        login_data = {
            "username": "test_user",
            "password": "TestPass123"
        }
        
        response = await client.post(f"{base_url}/login", json=login_data)
        login_result = response.json()
        
        if login_result["success"]:
            access_token = login_result["data"]["access_token"]
            headers = {"Authorization": f"Bearer {access_token}"}
            
            # 3. 获取用户信息
            response = await client.get(f"{base_url}/profile", headers=headers)
            print("用户信息:", response.json())
            
            # 4. 用户登出
            response = await client.post(f"{base_url}/logout", headers=headers)
            print("登出结果:", response.json())

# 运行示例
asyncio.run(test_user_service())
```

### cURL 示例

```bash
# 1. 注册用户
curl -X POST "http://localhost:8002/register" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "test_user",
    "email": "test@example.com",
    "password": "TestPass123",
    "confirm_password": "TestPass123",
    "role": "user"
  }'

# 2. 用户登录
curl -X POST "http://localhost:8002/login" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "test_user",
    "password": "TestPass123"
  }'

# 3. 获取用户信息（需要替换 <access_token>）
curl -X GET "http://localhost:8002/profile" \
  -H "Authorization: Bearer <access_token>"

# 4. 用户登出（需要替换 <access_token>）
curl -X POST "http://localhost:8002/logout" \
  -H "Authorization: Bearer <access_token>"
```

## 配置说明

### 环境变量

- `USER_SERVICE_HOST`: 服务主机地址 (默认: localhost)
- `USER_SERVICE_PORT`: 服务端口 (默认: 8002)
- `REDIS_HOST`: Redis主机地址 (默认: localhost)
- `REDIS_PORT`: Redis端口 (默认: 6379)
- `POSTGRES_HOST`: PostgreSQL主机地址 (默认: localhost)
- `POSTGRES_PORT`: PostgreSQL端口 (默认: 5432)
- `POSTGRES_DB`: 数据库名称 (默认: fire_emergency)
- `POSTGRES_USER`: 数据库用户名 (默认: postgres)
- `POSTGRES_PASSWORD`: 数据库密码 (默认: password)
- `JWT_SECRET_KEY`: JWT密钥 (必须修改)
- `JWT_ALGORITHM`: JWT算法 (默认: HS256)
- `JWT_ACCESS_TOKEN_EXPIRE_MINUTES`: 访问令牌过期时间(分钟) (默认: 30)
- `JWT_REFRESH_TOKEN_EXPIRE_DAYS`: 刷新令牌过期时间(天) (默认: 7)

## 安全注意事项

1. **JWT密钥**: 生产环境中必须使用强密钥
2. **密码策略**: 密码必须包含大小写字母和数字
3. **令牌过期**: 访问令牌默认30分钟过期
4. **刷新令牌**: 用于获取新的访问令牌
5. **令牌黑名单**: 登出后令牌会被加入黑名单

## 监控和日志

用户服务提供以下监控端点：

- `/health`: 健康检查
- `/metrics`: Prometheus指标（如果启用）

日志级别可通过环境变量 `LOG_LEVEL` 配置。
