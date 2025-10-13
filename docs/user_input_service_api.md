# 用户输入服务 API 文档

## 服务概述

**服务名称**: 用户输入服务  
**端口**: 8006  
**描述**: 用户交互界面API，处理用户输入数据，与应急服务对接  
**版本**: 1.0.0  

## 功能特性

- ✅ 用户输入数据验证和预处理
- ✅ 与应急服务的接口对接
- ✅ 用户输入历史记录管理
- ✅ 输入建议和自动补全
- ✅ 服务健康状态监控
- ✅ CORS支持，支持前端跨域访问

## API 端点

### 1. 服务信息

#### GET /
获取服务基本信息

**响应示例**:
```json
{
  "success": true,
  "message": "用户输入服务运行正常",
  "data": {
    "service": "用户输入服务",
    "version": "1.0.0",
    "description": "用户交互界面API，处理用户输入数据，与应急服务对接",
    "endpoints": {
      "health": "/health",
      "validate": "/validate",
      "submit": "/submit",
      "suggestions": "/suggestions",
      "history": "/history",
      "docs": "/docs"
    }
  }
}
```

### 2. 健康检查

#### GET /health
检查服务健康状态

**响应示例**:
```json
{
  "success": true,
  "message": "健康检查完成",
  "data": {
    "overall_status": "healthy",
    "services": [
      {
        "service_name": "emergency_service",
        "status": "healthy",
        "response_time": 45.2,
        "last_check": "2025-01-08T10:30:00Z",
        "error_message": null
      }
    ],
    "total_services": 6,
    "healthy_services": 6,
    "last_check": "2025-01-08T10:30:00Z"
  }
}
```

### 3. 输入验证

#### POST /validate
验证用户输入数据

**请求体**:
```json
{
  "items": [
    {
      "name": "木质桌子",
      "material": "木质",
      "quantity": 1,
      "location": "客厅",
      "condition": "良好",
      "flammability": "易燃",
      "toxicity": "无毒"
    }
  ],
  "environment": {
    "type": "室内",
    "area": "住宅",
    "floor": 2,
    "ventilation": "一般",
    "exits": 2,
    "occupancy": 4,
    "building_type": "住宅楼",
    "fire_safety_equipment": ["灭火器", "烟雾报警器"],
    "special_conditions": "无"
  },
  "additional_info": "客厅发生火灾",
  "urgency_level": "高",
  "contact_info": {
    "phone": "13800138000",
    "name": "张三"
  },
  "user_id": "user_123"
}
```

**响应示例**:
```json
{
  "success": true,
  "message": "输入验证完成",
  "data": {
    "is_valid": true,
    "errors": [],
    "warnings": ["人员数量较多，请确认数据准确性"],
    "suggestions": [
      {
        "type": "material",
        "value": "金属",
        "confidence": 0.7,
        "description": "考虑添加金属物品"
      }
    ]
  }
}
```

### 4. 提交救援请求

#### POST /submit
提交救援请求并获取救援方案

**请求体**: 同 `/validate` 端点

**响应示例**:
```json
{
  "success": true,
  "message": "救援请求提交成功",
  "data": {
    "id": "plan_123",
    "title": "客厅火灾救援方案",
    "priority": "高",
    "status": "active",
    "steps": [
      {
        "step_number": 1,
        "description": "立即疏散人员到安全区域",
        "equipment": ["对讲机", "扩音器"],
        "warnings": ["注意安全，避免吸入烟雾"],
        "estimated_time": 5
      },
      {
        "step_number": 2,
        "description": "使用干粉灭火器扑灭初期火灾",
        "equipment": ["干粉灭火器", "防护面具"],
        "warnings": ["保持安全距离", "注意风向"],
        "estimated_time": 10
      }
    ],
    "equipment_list": ["对讲机", "扩音器", "干粉灭火器", "防护面具"],
    "warnings": ["注意安全", "保持安全距离", "注意风向"],
    "estimated_duration": 15,
    "created_at": "2025-01-08T10:30:00Z",
    "updated_at": "2025-01-08T10:30:00Z"
  }
}
```

### 5. 获取输入建议

#### GET /suggestions
获取输入建议和自动补全

**查询参数**:
- `partial_input` (string, 必需): 部分输入内容
- `input_type` (string, 必需): 输入类型 (material, environment_type, area_type)

**请求示例**:
```
GET /suggestions?partial_input=木&input_type=material
```

**响应示例**:
```json
{
  "success": true,
  "message": "获取建议成功",
  "data": [
    {
      "type": "material",
      "value": "木质",
      "confidence": 0.8,
      "description": "材质: 木质"
    }
  ]
}
```

### 6. 获取用户输入历史

#### GET /history/{user_id}
获取用户输入历史记录

**路径参数**:
- `user_id` (string, 必需): 用户ID

**查询参数**:
- `page` (int, 可选): 页码，默认为1
- `size` (int, 可选): 每页大小，默认为10，最大100

**请求示例**:
```
GET /history/user_123?page=1&size=10
```

**响应示例**:
```json
{
  "success": true,
  "message": "获取历史记录成功",
  "data": {
    "items": [
      {
        "id": "history_123",
        "user_id": "user_123",
        "input_data": {
          "items": [...],
          "environment": {...},
          "additional_info": "客厅发生火灾",
          "urgency_level": "高",
          "user_id": "user_123"
        },
        "rescue_plan_id": "plan_123",
        "status": "completed",
        "created_at": "2025-01-08T10:30:00Z",
        "updated_at": "2025-01-08T10:30:00Z"
      }
    ],
    "total": 1,
    "page": 1,
    "size": 10,
    "pages": 1
  }
}
```

### 7. 获取历史记录详情

#### GET /history/detail/{history_id}
获取特定历史记录的详细信息

**路径参数**:
- `history_id` (string, 必需): 历史记录ID

**响应示例**:
```json
{
  "success": true,
  "message": "获取历史记录详情成功",
  "data": {
    "id": "history_123",
    "user_id": "user_123",
    "input_data": {...},
    "rescue_plan_id": "plan_123",
    "status": "completed",
    "created_at": "2025-01-08T10:30:00Z",
    "updated_at": "2025-01-08T10:30:00Z"
  }
}
```

## 数据模型

### UserInputRequest
用户输入请求模型

```json
{
  "items": [
    {
      "name": "string",
      "material": "木质|金属|塑料|玻璃|陶瓷|布料|皮革|电子|化学|其他",
      "quantity": 1,
      "location": "string",
      "condition": "string",
      "flammability": "不燃|难燃|易燃|极易燃",
      "toxicity": "无毒|低毒|中毒|高毒|剧毒",
      "size": {},
      "weight": {}
    }
  ],
  "environment": {
    "type": "室内|室外|半室外",
    "area": "住宅|商业|工业|公共建筑|交通工具|仓库|实验室|其他",
    "floor": 0,
    "ventilation": "良好|一般|较差|很差",
    "exits": 1,
    "occupancy": 0,
    "building_type": "string",
    "fire_safety_equipment": ["string"],
    "special_conditions": "string"
  },
  "additional_info": "string",
  "urgency_level": "低|中|高|紧急",
  "contact_info": {},
  "user_id": "string"
}
```

### InputValidationResult
输入验证结果模型

```json
{
  "is_valid": true,
  "errors": ["string"],
  "warnings": ["string"],
  "suggestions": [
    {
      "type": "string",
      "value": "string",
      "confidence": 0.8,
      "description": "string"
    }
  ]
}
```

### InputSuggestion
输入建议模型

```json
{
  "type": "material|environment_type|area_type|urgency",
  "value": "string",
  "confidence": 0.8,
  "description": "string"
}
```

## 错误处理

### HTTP 状态码

- `200 OK`: 请求成功
- `400 Bad Request`: 请求参数错误
- `404 Not Found`: 资源不存在
- `500 Internal Server Error`: 服务器内部错误
- `502 Bad Gateway`: 外部服务错误

### 错误响应格式

```json
{
  "success": false,
  "message": "错误描述",
  "data": {
    "error": "错误类型",
    "details": "详细错误信息"
  }
}
```

## 使用示例

### 1. 验证用户输入

```bash
curl -X POST "http://localhost:8006/validate" \
  -H "Content-Type: application/json" \
  -d '{
    "items": [
      {
        "name": "木质桌子",
        "material": "木质",
        "quantity": 1,
        "location": "客厅"
      }
    ],
    "environment": {
      "type": "室内",
      "area": "住宅",
      "floor": 2,
      "ventilation": "一般",
      "exits": 2,
      "occupancy": 4
    },
    "urgency_level": "高"
  }'
```

### 2. 提交救援请求

```bash
curl -X POST "http://localhost:8006/submit" \
  -H "Content-Type: application/json" \
  -d '{
    "items": [...],
    "environment": {...},
    "urgency_level": "高",
    "user_id": "user_123"
  }'
```

### 3. 获取输入建议

```bash
curl "http://localhost:8006/suggestions?partial_input=木&input_type=material"
```

## 配置说明

### 环境变量

- `USER_INPUT_SERVICE_HOST`: 服务主机地址 (默认: localhost)
- `USER_INPUT_SERVICE_PORT`: 服务端口 (默认: 8006)
- `EMERGENCY_SERVICE_HOST`: 应急服务主机地址
- `EMERGENCY_SERVICE_PORT`: 应急服务端口
- `KNOWLEDGE_GRAPH_HOST`: 知识图谱服务主机地址
- `KNOWLEDGE_GRAPH_PORT`: 知识图谱服务端口
- `RAG_SERVICE_HOST`: RAG服务主机地址
- `RAG_SERVICE_PORT`: RAG服务端口
- `OLLAMA_SERVICE_HOST`: Ollama服务主机地址
- `OLLAMA_SERVICE_PORT`: Ollama服务端口
- `CACHE_SERVICE_HOST`: 缓存服务主机地址
- `CACHE_SERVICE_PORT`: 缓存服务端口
- `USER_SERVICE_HOST`: 用户服务主机地址
- `USER_SERVICE_PORT`: 用户服务端口

## 启动服务

### 使用启动脚本

```bash
python scripts/start_user_input_service.py
```

### 直接启动

```bash
python backend/services/user_input_service.py
```

### 使用Docker

```bash
docker build -f infrastructure/docker/services/Dockerfile.user_input_service -t user-input-service .
docker run -p 8006:8006 user-input-service
```

## 测试

运行单元测试：

```bash
python -m pytest tests/test_user_input_service.py -v
```

## 注意事项

1. **依赖服务**: 用户输入服务依赖所有其他服务，确保相关服务正常运行
2. **CORS支持**: 已配置CORS中间件，支持前端跨域访问
3. **输入验证**: 所有输入数据都会进行严格验证
4. **错误处理**: 完善的错误处理机制，提供详细的错误信息
5. **历史记录**: 用户输入历史存储在内存中，重启服务会丢失
6. **建议缓存**: 输入建议会进行缓存，提高响应速度

## 更新日志

### v1.0.0 (2025-01-08)
- ✅ 初始版本发布
- ✅ 完整的API功能实现
- ✅ 单元测试覆盖
- ✅ 文档完善
