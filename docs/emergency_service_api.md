# 应急服务 API 文档

## 概述

应急服务是火灾应急救援RAG系统的核心协调服务，负责集成知识图谱、RAG、Ollama、缓存等服务，提供完整的火灾应急救援方案生成功能。

**服务地址**: `http://localhost:8000`  
**API文档**: `http://localhost:8000/docs`  
**ReDoc文档**: `http://localhost:8000/redoc`

## 核心功能

- ✅ **服务集成** - 统一协调知识图谱、RAG、Ollama、缓存服务
- ✅ **救援方案生成** - 基于物品和环境信息生成专业救援方案
- ✅ **知识上下文收集** - 自动收集相关材质、环境、救援程序知识
- ✅ **智能缓存** - 缓存生成结果提高响应速度
- ✅ **降级机制** - 依赖服务不可用时提供基础救援方案
- ✅ **健康监控** - 实时监控所有依赖服务状态
- ✅ **数据验证** - 严格的输入数据验证和错误处理

## 依赖服务

| 服务名称 | 端口 | 必需性 | 功能描述 |
|---------|------|--------|----------|
| 知识图谱服务 | 8001 | 必需 | 提供材质和环境知识 |
| RAG服务 | 3000 | 必需 | 提供语义搜索和文档检索 |
| Ollama服务 | 8003 | 必需 | 提供AI生成功能 |
| 缓存服务 | 8004 | 可选 | 提供缓存功能 |

## API 端点

### 1. 基础信息

#### GET /
获取服务基本信息

**响应示例**:
```json
{
  "success": true,
  "message": "应急服务运行正常",
  "data": {
    "service": "应急服务",
    "version": "1.0.0",
    "description": "火灾应急救援系统核心协调服务",
    "endpoints": {
      "health": "/health",
      "rescue-plan": "/rescue-plan",
      "status": "/status",
      "docs": "/docs"
    }
  },
  "timestamp": "2024-01-01T12:00:00Z"
}
```

### 2. 健康检查

#### GET /health
检查服务健康状态，包括所有依赖服务

**响应示例**:
```json
{
  "success": true,
  "message": "健康检查完成，状态: healthy",
  "data": {
    "overall_status": "healthy",
    "services": [
      {
        "service_name": "knowledge_graph",
        "status": "healthy",
        "response_time": 15.2,
        "last_check": "2024-01-01T12:00:00Z",
        "error_message": null
      },
      {
        "service_name": "rag",
        "status": "healthy",
        "response_time": 25.8,
        "last_check": "2024-01-01T12:00:00Z",
        "error_message": null
      },
      {
        "service_name": "ollama",
        "status": "healthy",
        "response_time": 45.3,
        "last_check": "2024-01-01T12:00:00Z",
        "error_message": null
      },
      {
        "service_name": "cache",
        "status": "healthy",
        "response_time": 8.7,
        "last_check": "2024-01-01T12:00:00Z",
        "error_message": null
      }
    ],
    "total_services": 4,
    "healthy_services": 4,
    "last_check": "2024-01-01T12:00:00Z"
  },
  "timestamp": "2024-01-01T12:00:00Z"
}
```

**状态说明**:
- `healthy`: 所有必需服务正常
- `degraded`: 部分可选服务不可用，但核心功能正常
- `unhealthy`: 必需服务不可用

### 3. 服务状态

#### GET /status
获取详细的服务状态信息

**响应示例**:
```json
{
  "success": true,
  "message": "服务状态获取成功",
  "data": {
    "overall_status": "healthy",
    "services": {
      "knowledge_graph": {
        "service_name": "knowledge_graph",
        "status": "healthy",
        "response_time": 15.2,
        "last_check": "2024-01-01T12:00:00Z",
        "error_message": null
      },
      "rag": {
        "service_name": "rag",
        "status": "healthy",
        "response_time": 25.8,
        "last_check": "2024-01-01T12:00:00Z",
        "error_message": null
      },
      "ollama": {
        "service_name": "ollama",
        "status": "healthy",
        "response_time": 45.3,
        "last_check": "2024-01-01T12:00:00Z",
        "error_message": null
      },
      "cache": {
        "service_name": "cache",
        "status": "healthy",
        "response_time": 8.7,
        "last_check": "2024-01-01T12:00:00Z",
        "error_message": null
      }
    },
    "cache_enabled": true,
    "last_check": "2024-01-01T12:00:00Z"
  },
  "timestamp": "2024-01-01T12:00:00Z"
}
```

### 4. 救援方案生成

#### POST /rescue-plan
生成火灾应急救援方案

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
      "toxicity": "低毒",
      "size": {"length": 2.0, "width": 0.8, "height": 1.2},
      "weight": {"value": 50, "unit": "kg"}
    },
    {
      "name": "电器设备",
      "material": "电子",
      "quantity": 1,
      "location": "客厅",
      "condition": "正常",
      "flammability": "易燃",
      "toxicity": "中毒"
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
    "fire_safety_equipment": ["灭火器", "烟雾报警器"],
    "special_conditions": "无"
  },
  "additional_info": "客厅有木质家具和电器设备起火，火势较小",
  "urgency_level": "中",
  "contact_info": {
    "phone": "13800138000",
    "address": "北京市朝阳区xxx街道xxx号"
  },
  "user_id": "user123"
}
```

**参数说明**:

**items** (必需): 物品列表
- `name` (string): 物品名称
- `material` (enum): 材质类型 (木质/金属/塑料/玻璃/陶瓷/布料/皮革/电子/化学/其他)
- `quantity` (int): 数量 (1-1000)
- `location` (string): 位置
- `condition` (string, 可选): 状态
- `flammability` (enum, 可选): 易燃性 (不燃/难燃/易燃/极易燃)
- `toxicity` (enum, 可选): 毒性 (无毒/低毒/中毒/高毒/剧毒)
- `size` (object, 可选): 尺寸信息
- `weight` (object, 可选): 重量信息

**environment** (必需): 环境信息
- `type` (enum): 环境类型 (室内/室外/半室外)
- `area` (enum): 区域类型 (住宅/商业/工业/公共建筑/交通工具/仓库/实验室/其他)
- `floor` (int, 可选): 楼层 (-10到200)
- `ventilation` (enum): 通风情况 (良好/一般/较差/很差)
- `exits` (int): 出口数量 (1-20)
- `occupancy` (int, 可选): 人员数量 (0-10000)
- `building_type` (string, 可选): 建筑类型
- `fire_safety_equipment` (array, 可选): 消防设备
- `special_conditions` (string, 可选): 特殊条件

**additional_info** (可选): 附加信息
**urgency_level** (string): 紧急程度 (低/一般/中/紧急/非常紧急)
**contact_info** (object, 可选): 联系信息
**user_id** (string, 可选): 用户ID

**响应示例**:
```json
{
  "success": true,
  "message": "救援方案生成成功",
  "data": {
    "id": "plan_12345678-1234-1234-1234-123456789abc",
    "title": "住宅客厅木质家具火灾救援方案",
    "priority": "高",
    "status": "active",
    "steps": [
      {
        "step_number": 1,
        "description": "立即报警并疏散人员，确保所有人员安全撤离",
        "equipment": ["通信设备", "疏散指示牌", "防护装备"],
        "warnings": ["确保所有人员安全撤离", "保持冷静", "注意电器设备断电"],
        "estimated_time": 5
      },
      {
        "step_number": 2,
        "description": "评估火势和现场情况，确定起火原因和蔓延趋势",
        "equipment": ["防护装备", "检测设备", "照明设备"],
        "warnings": ["注意自身安全", "避免进入危险区域", "注意电器设备可能带电"],
        "estimated_time": 10
      },
      {
        "step_number": 3,
        "description": "使用干粉灭火器扑灭木质家具火源，注意电器设备断电",
        "equipment": ["干粉灭火器", "绝缘工具", "防护手套"],
        "warnings": ["先断电再灭火", "选择合适的灭火器材", "注意风向"],
        "estimated_time": 15
      },
      {
        "step_number": 4,
        "description": "确保火势完全扑灭，检查是否有复燃风险",
        "equipment": ["检测设备", "照明设备", "温度计"],
        "warnings": ["确保无复燃风险", "检查是否有人员受伤", "保持通风"],
        "estimated_time": 10
      }
    ],
    "equipment_list": [
      "通信设备",
      "疏散指示牌", 
      "防护装备",
      "检测设备",
      "照明设备",
      "干粉灭火器",
      "绝缘工具",
      "防护手套",
      "温度计"
    ],
    "warnings": [
      "确保所有人员安全撤离",
      "保持冷静",
      "注意电器设备断电",
      "注意自身安全",
      "避免进入危险区域",
      "注意电器设备可能带电",
      "先断电再灭火",
      "选择合适的灭火器材",
      "注意风向",
      "确保无复燃风险",
      "检查是否有人员受伤",
      "保持通风"
    ],
    "estimated_duration": 40,
    "created_at": "2024-01-01T12:00:00Z",
    "updated_at": "2024-01-01T12:00:00Z"
  },
  "timestamp": "2024-01-01T12:00:00Z"
}
```

## 错误处理

### 常见错误码

- `400`: 请求参数错误 (数据验证失败)
- `408`: 请求超时 (依赖服务响应超时)
- `502`: 外部服务错误 (依赖服务调用失败)
- `500`: 服务器内部错误

### 错误响应格式

```json
{
  "success": false,
  "message": "错误描述",
  "data": null,
  "timestamp": "2024-01-01T12:00:00Z"
}
```

### 降级机制

当依赖服务不可用时，系统会自动使用降级救援方案：

1. **知识图谱服务不可用**: 跳过材质和环境知识收集
2. **RAG服务不可用**: 跳过文档检索，使用基础知识
3. **Ollama服务不可用**: 使用预定义的救援方案模板
4. **缓存服务不可用**: 禁用缓存功能，直接生成方案

## 使用示例

### Python 客户端示例

```python
import httpx
import asyncio
from datetime import datetime

async def emergency_service_example():
    base_url = "http://localhost:8000"
    
    async with httpx.AsyncClient() as client:
        # 1. 健康检查
        response = await client.get(f"{base_url}/health")
        print("健康状态:", response.json())
        
        # 2. 生成救援方案
        rescue_request = {
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
                "building_type": "住宅楼"
            },
            "additional_info": "客厅木质家具起火",
            "urgency_level": "中"
        }
        
        response = await client.post(
            f"{base_url}/rescue-plan",
            json=rescue_request
        )
        
        if response.status_code == 200:
            result = response.json()
            rescue_plan = result["data"]
            print(f"救援方案标题: {rescue_plan['title']}")
            print(f"预计时长: {rescue_plan['estimated_duration']} 分钟")
            print(f"救援步骤数: {len(rescue_plan['steps'])}")
            
            for step in rescue_plan["steps"]:
                print(f"步骤 {step['step_number']}: {step['description']}")
        else:
            print(f"生成救援方案失败: {response.text}")

# 运行示例
asyncio.run(emergency_service_example())
```

### JavaScript 客户端示例

```javascript
const baseUrl = 'http://localhost:8000';

async function emergencyServiceExample() {
    try {
        // 1. 健康检查
        const healthResponse = await fetch(`${baseUrl}/health`);
        const healthData = await healthResponse.json();
        console.log('健康状态:', healthData);
        
        // 2. 生成救援方案
        const rescueRequest = {
            items: [
                {
                    name: "木质家具",
                    material: "木质",
                    quantity: 2,
                    location: "客厅",
                    condition: "良好",
                    flammability: "易燃",
                    toxicity: "低毒"
                }
            ],
            environment: {
                type: "室内",
                area: "住宅",
                floor: 2,
                ventilation: "良好",
                exits: 2,
                occupancy: 4,
                building_type: "住宅楼"
            },
            additional_info: "客厅木质家具起火",
            urgency_level: "中"
        };
        
        const response = await fetch(`${baseUrl}/rescue-plan`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(rescueRequest)
        });
        
        if (response.ok) {
            const result = await response.json();
            const rescuePlan = result.data;
            console.log(`救援方案标题: ${rescuePlan.title}`);
            console.log(`预计时长: ${rescuePlan.estimated_duration} 分钟`);
            console.log(`救援步骤数: ${rescuePlan.steps.length}`);
            
            rescuePlan.steps.forEach(step => {
                console.log(`步骤 ${step.step_number}: ${step.description}`);
            });
        } else {
            console.error('生成救援方案失败:', await response.text());
        }
        
    } catch (error) {
        console.error('错误:', error);
    }
}

// 运行示例
emergencyServiceExample();
```

### cURL 示例

```bash
# 健康检查
curl -X GET "http://localhost:8000/health"

# 获取服务状态
curl -X GET "http://localhost:8000/status"

# 生成救援方案
curl -X POST "http://localhost:8000/rescue-plan" \
  -H "Content-Type: application/json" \
  -d '{
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
      "building_type": "住宅楼"
    },
    "additional_info": "客厅木质家具起火",
    "urgency_level": "中"
  }'
```

## 性能优化

### 缓存策略

- **缓存键**: 基于请求内容的MD5哈希值
- **缓存时间**: 1小时 (3600秒)
- **缓存命名空间**: `emergency:rescue_plan:`
- **缓存条件**: 成功生成的救援方案

### 并发处理

- **并行知识收集**: 同时调用多个服务收集知识上下文
- **异步处理**: 所有外部服务调用都是异步的
- **超时控制**: 每个服务都有独立的超时设置

### 监控指标

- **响应时间**: 各服务的响应时间统计
- **成功率**: 救援方案生成成功率
- **缓存命中率**: 缓存使用情况
- **降级频率**: 降级方案使用频率

## 配置说明

### 环境变量

- `EMERGENCY_SERVICE_HOST`: 服务绑定主机 (默认: 0.0.0.0)
- `EMERGENCY_SERVICE_PORT`: 服务端口 (默认: 8000)
- `KNOWLEDGE_GRAPH_URL`: 知识图谱服务地址 (默认: http://localhost:8001)
- `RAG_SERVICE_URL`: RAG服务地址 (默认: http://localhost:3000)
- `OLLAMA_SERVICE_URL`: Ollama服务地址 (默认: http://localhost:8003)
- `CACHE_SERVICE_URL`: 缓存服务地址 (默认: http://localhost:8004)

### 服务配置

```python
services = {
    "knowledge_graph": {
        "url": "http://localhost:8001",
        "timeout": 10.0,
        "required": True
    },
    "rag": {
        "url": "http://localhost:3000", 
        "timeout": 15.0,
        "required": True
    },
    "ollama": {
        "url": "http://localhost:8003",
        "timeout": 120.0,
        "required": True
    },
    "cache": {
        "url": "http://localhost:8004",
        "timeout": 5.0,
        "required": False
    }
}
```

## 部署说明

### Docker 部署

```bash
# 构建镜像
docker build -f Dockerfile.emergency_service -t fire-emergency-service .

# 运行容器
docker run -d \
  --name fire-emergency-service \
  -p 8000:8000 \
  -e KNOWLEDGE_GRAPH_URL=http://knowledge-graph:8001 \
  -e RAG_SERVICE_URL=http://rag-service:3000 \
  -e OLLAMA_SERVICE_URL=http://ollama-service:8003 \
  -e CACHE_SERVICE_URL=http://cache-service:8004 \
  fire-emergency-service
```

### Docker Compose 部署

```bash
# 启动应急服务
docker-compose up emergency_service

# 查看日志
docker-compose logs -f emergency_service

# 停止服务
docker-compose down
```

## 监控和运维

### 健康检查

```bash
# 检查服务健康状态
curl http://localhost:8000/health

# 检查详细状态
curl http://localhost:8000/status
```

### 日志监控

```bash
# Docker 环境
docker-compose logs -f emergency_service

# 本地环境
python backend/services/emergency_service.py
```

### 性能监控

- 监控各依赖服务的响应时间
- 监控救援方案生成成功率
- 监控缓存命中率
- 监控降级方案使用频率

## 故障排除

### 常见问题

1. **依赖服务不可用**
   - 检查各服务的健康状态
   - 确认网络连接
   - 查看服务日志

2. **救援方案生成失败**
   - 检查输入数据格式
   - 确认Ollama服务状态
   - 查看错误日志

3. **响应时间过长**
   - 检查各服务性能
   - 考虑启用缓存
   - 优化知识收集策略

### 调试模式

设置环境变量 `LOG_LEVEL=DEBUG` 启用详细日志输出。

## 更新日志

### v1.0.0 (2024-01-01)
- ✅ 初始版本发布
- ✅ 集成所有依赖服务
- ✅ 实现救援方案生成核心逻辑
- ✅ 添加智能缓存功能
- ✅ 实现降级机制
- ✅ 添加健康监控
- ✅ 完善错误处理
