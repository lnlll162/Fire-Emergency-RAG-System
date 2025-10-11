# Ollama服务API文档

## 概述

Ollama服务是基于Ollama的AI生成服务，提供救援方案生成和模型管理功能。该服务集成了Ollama大语言模型，能够根据物品和环境信息生成专业的火灾应急救援方案。

## 服务信息

- **服务名称**: Ollama服务
- **端口**: 8003
- **基础URL**: `http://localhost:8003`
- **API文档**: `http://localhost:8003/docs`

## 主要功能

1. **模型管理**: 列出可用模型、检查模型状态、加载模型
2. **文本生成**: 基于提示词生成文本内容
3. **救援方案生成**: 根据物品和环境信息生成专业救援方案
4. **缓存管理**: 缓存生成结果以提高性能
5. **健康检查**: 监控服务状态

## API端点

### 1. 健康检查

#### GET /health

检查服务健康状态。

**响应示例**:
```json
{
  "success": true,
  "data": {
    "status": "healthy"
  },
  "message": "服务健康检查完成",
  "timestamp": "2024-01-01T00:00:00Z"
}
```

### 2. 模型管理

#### GET /models

获取可用模型列表。

**响应示例**:
```json
{
  "success": true,
  "data": [
    {
      "name": "qwen2.5:7b",
      "size": 1000000000,
      "digest": "abc123",
      "modified_at": "2024-01-01T00:00:00Z",
      "family": "qwen",
      "format": "gguf",
      "parameter_size": "7B",
      "quantization_level": "Q4_0"
    }
  ],
  "message": "成功获取 1 个模型"
}
```

#### GET /models/{model_name}/status

获取指定模型的状态。

**参数**:
- `model_name` (string): 模型名称

**响应示例**:
```json
{
  "success": true,
  "data": {
    "name": "qwen2.5:7b",
    "loaded": true,
    "loading": false,
    "error": null,
    "last_used": "2024-01-01T00:00:00Z",
    "memory_usage": 1000000000
  },
  "message": "成功获取模型 qwen2.5:7b 的状态"
}
```

#### POST /models/{model_name}/load

加载指定模型。

**参数**:
- `model_name` (string): 模型名称

**响应示例**:
```json
{
  "success": true,
  "data": {
    "model_name": "qwen2.5:7b",
    "loaded": true
  },
  "message": "模型 qwen2.5:7b 加载成功"
}
```

### 3. 文本生成

#### POST /generate

生成文本内容。

**请求体**:
```json
{
  "prompt": "请简单介绍一下火灾应急救援的基本原则。",
  "model": "qwen2.5:7b",
  "temperature": 0.7,
  "top_p": 0.9,
  "max_tokens": 1000,
  "stream": false,
  "context": {
    "user_id": "user123"
  }
}
```

**参数说明**:
- `prompt` (string, 必需): 提示词
- `model` (string, 可选): 指定模型名称
- `temperature` (float, 可选): 温度参数 (0.0-2.0)
- `top_p` (float, 可选): Top-p参数 (0.0-1.0)
- `max_tokens` (int, 可选): 最大生成token数 (1-8192)
- `stream` (bool, 可选): 是否流式输出
- `context` (object, 可选): 上下文信息

**响应示例**:
```json
{
  "response": "火灾应急救援的基本原则包括：1. 人员安全第一...",
  "model": "qwen2.5:7b",
  "created_at": "2024-01-01T00:00:00Z",
  "tokens_used": 150,
  "generation_time": 2.5,
  "cached": false
}
```

### 4. 救援方案生成

#### POST /rescue-plan

生成火灾应急救援方案。

**请求体**:
```json
{
  "items": [
    {
      "name": "木质家具",
      "material": "木质",
      "quantity": 2,
      "location": "客厅",
      "condition": "良好",
      "flammability": "易燃",
      "toxicity": "低毒"
    }
  ],
  "environment": {
    "type": "室内",
    "area": "住宅",
    "floor": 2,
    "ventilation": "良好",
    "exits": 2,
    "occupancy": 4,
    "building_type": "住宅楼",
    "special_conditions": "无"
  },
  "additional_info": "客厅有木质家具起火",
  "urgency_level": "中",
  "model": "qwen2.5:7b",
  "temperature": 0.7
}
```

**响应示例**:
```json
{
  "success": true,
  "data": {
    "id": "plan_123",
    "title": "木质家具火灾救援方案",
    "priority": "高",
    "status": "active",
    "steps": [
      {
        "step_number": 1,
        "description": "评估现场情况，确保救援人员安全",
        "equipment": ["防护装备", "通信设备"],
        "warnings": ["注意现场安全", "保持通信畅通"],
        "estimated_time": 5
      },
      {
        "step_number": 2,
        "description": "制定具体救援方案并执行",
        "equipment": ["救援工具", "安全设备"],
        "warnings": ["严格按照安全程序操作"],
        "estimated_time": 30
      }
    ],
    "equipment_list": ["防护装备", "通信设备", "救援工具", "安全设备"],
    "warnings": ["注意现场安全", "保持通信畅通", "严格按照安全程序操作"],
    "estimated_duration": 60,
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-01T00:00:00Z"
  },
  "message": "救援方案生成成功"
}
```

### 5. 缓存管理

#### GET /cache/stats

获取缓存统计信息。

**响应示例**:
```json
{
  "success": true,
  "data": {
    "enabled": true,
    "total_keys": 10,
    "total_memory_bytes": 1048576,
    "total_memory_mb": 1.0
  },
  "message": "缓存统计信息获取成功"
}
```

#### DELETE /cache

清空缓存。

**响应示例**:
```json
{
  "success": true,
  "data": {
    "cleared": true
  },
  "message": "缓存清空成功"
}
```

## 错误处理

服务使用统一的错误响应格式：

```json
{
  "success": false,
  "data": null,
  "message": "错误描述",
  "timestamp": "2024-01-01T00:00:00Z"
}
```

常见HTTP状态码：
- `200`: 成功
- `400`: 请求参数错误
- `404`: 资源未找到
- `500`: 服务器内部错误
- `502`: 外部服务错误
- `408`: 请求超时

## 使用示例

### Python示例

```python
import httpx
import asyncio

async def test_ollama_service():
    async with httpx.AsyncClient() as client:
        # 健康检查
        response = await client.get("http://localhost:8003/health")
        print(f"健康状态: {response.json()}")
        
        # 生成文本
        generation_request = {
            "prompt": "请简单介绍一下火灾应急救援的基本原则。",
            "model": "qwen2.5:7b",
            "temperature": 0.7,
            "max_tokens": 500
        }
        
        response = await client.post(
            "http://localhost:8003/generate",
            json=generation_request
        )
        print(f"生成结果: {response.json()['response']}")

# 运行示例
asyncio.run(test_ollama_service())
```

### cURL示例

```bash
# 健康检查
curl -X GET "http://localhost:8003/health"

# 获取模型列表
curl -X GET "http://localhost:8003/models"

# 生成文本
curl -X POST "http://localhost:8003/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "请简单介绍一下火灾应急救援的基本原则。",
    "model": "qwen2.5:7b",
    "temperature": 0.7,
    "max_tokens": 500
  }'

# 生成救援方案
curl -X POST "http://localhost:8003/rescue-plan" \
  -H "Content-Type: application/json" \
  -d '{
    "items": [
      {
        "name": "木质家具",
        "material": "木质",
        "quantity": 2,
        "location": "客厅"
      }
    ],
    "environment": {
      "type": "室内",
      "area": "住宅",
      "ventilation": "良好",
      "exits": 2
    },
    "urgency_level": "中"
  }'
```

## 配置说明

### 环境变量

- `OLLAMA_HOST`: Ollama服务主机地址 (默认: localhost)
- `OLLAMA_PORT`: Ollama服务端口 (默认: 11434)
- `REDIS_HOST`: Redis主机地址 (默认: localhost)
- `REDIS_PORT`: Redis端口 (默认: 6379)
- `REDIS_DB`: Redis数据库编号 (默认: 0)
- `OLLAMA_SERVICE_HOST`: 服务绑定主机 (默认: 0.0.0.0)
- `OLLAMA_SERVICE_PORT`: 服务端口 (默认: 8003)

### 依赖服务

- **Ollama**: 大语言模型服务
- **Redis**: 缓存服务
- **FastAPI**: Web框架

## 部署说明

### Docker部署

```bash
# 构建镜像
docker build -f Dockerfile.ollama_service -t fire-emergency-ollama-service .

# 运行容器
docker run -d \
  --name fire-emergency-ollama-service \
  -p 8003:8003 \
  -e OLLAMA_HOST=ollama \
  -e REDIS_HOST=redis \
  fire-emergency-ollama-service
```

### Docker Compose部署

```bash
# 启动服务
docker-compose up -d ollama_service

# 查看日志
docker-compose logs -f ollama_service
```

## 监控和日志

### 健康检查

服务提供健康检查端点 `/health`，可用于监控服务状态。

### 日志

服务使用Python标准日志库，支持不同级别的日志输出：
- DEBUG: 详细调试信息
- INFO: 一般信息
- WARNING: 警告信息
- ERROR: 错误信息
- CRITICAL: 严重错误

### 性能监控

- 生成时间统计
- 缓存命中率
- 模型加载状态
- 内存使用情况

## 故障排除

### 常见问题

1. **模型加载失败**
   - 检查Ollama服务是否运行
   - 确认模型是否已下载
   - 检查网络连接

2. **Redis连接失败**
   - 检查Redis服务状态
   - 确认连接参数
   - 检查网络连接

3. **生成超时**
   - 检查模型大小和硬件资源
   - 调整超时参数
   - 考虑使用更小的模型

### 调试模式

设置环境变量 `LOG_LEVEL=DEBUG` 启用详细日志输出。

## 更新日志

### v1.0.0 (2024-01-01)
- 初始版本发布
- 支持基本的文本生成功能
- 支持救援方案生成
- 支持模型管理
- 支持缓存功能
