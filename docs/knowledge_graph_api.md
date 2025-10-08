# 知识图谱服务 API 文档

## 概述

知识图谱服务提供火灾应急救援相关的知识图谱查询功能，包括材质信息、环境信息、救援程序等。

**服务地址**: `http://localhost:8001`  
**API文档**: `http://localhost:8001/docs`

## API 端点

### 1. 健康检查

**GET** `/health`

检查服务健康状态。

**响应示例**:
```json
{
  "success": true,
  "data": {
    "status": "healthy"
  },
  "message": "服务健康检查完成",
  "timestamp": "2025-10-08T20:08:30.582868"
}
```

### 2. 获取材质信息

**GET** `/materials/{material_name}`

获取指定材质的详细信息。

**路径参数**:
- `material_name` (string): 材质名称

**响应示例**:
```json
{
  "success": true,
  "data": {
    "name": "木材",
    "properties": {
      "燃点": "300°C"
    },
    "hazards": [
      "燃烧速度快",
      "燃烧时产生大量烟雾"
    ],
    "safety_measures": [
      "使用水灭火",
      "使用泡沫灭火器"
    ]
  },
  "message": "成功获取材质 木材 的信息",
  "timestamp": "2025-10-08T20:08:39.223033"
}
```

### 3. 获取环境信息

**GET** `/environments/{location}`

获取指定环境的详细信息。

**路径参数**:
- `location` (string): 环境位置

**响应示例**:
```json
{
  "success": true,
  "data": {
    "location": "住宅",
    "conditions": {
      "温度": "常温",
      "通风": "良好"
    },
    "risks": [
      "火势蔓延快",
      "烟雾浓度高"
    ],
    "recommendations": [
      "立即疏散人员",
      "关闭电源"
    ]
  },
  "message": "成功获取环境 住宅 的信息",
  "timestamp": "2025-10-08T20:08:46.773274"
}
```

### 4. 获取救援程序

**GET** `/procedures`

获取救援程序列表。

**查询参数**:
- `material_name` (string, 可选): 材质名称过滤
- `environment` (string, 可选): 环境位置过滤

**响应示例**:
```json
{
  "success": true,
  "data": [
    {
      "procedure_id": "PROC001",
      "title": "木材火灾救援程序",
      "description": "处理木材火灾的标准救援程序",
      "steps": [
        "评估火势大小和蔓延情况",
        "确定安全撤离路线",
        "选择合适的灭火器材",
        "从安全距离开始灭火",
        "监控火势变化",
        "确保火势完全扑灭"
      ],
      "materials_needed": [
        "纸张",
        "布料",
        "木材"
      ],
      "safety_notes": [
        "防止复燃",
        "注意烟雾中毒"
      ]
    }
  ],
  "message": "成功获取 1 个救援程序",
  "timestamp": "2025-10-08T20:09:57.259430"
}
```

### 5. 搜索材质

**GET** `/materials/search/{keyword}`

根据关键词搜索材质。

**路径参数**:
- `keyword` (string): 搜索关键词

**响应示例**:
```json
{
  "success": true,
  "data": [
    "木材"
  ],
  "message": "搜索到 1 个相关材质",
  "timestamp": "2025-10-08T20:10:02.951939"
}
```

### 6. 获取相关材质

**GET** `/materials/{material_name}/related`

获取与指定材质相关的其他材质。

**路径参数**:
- `material_name` (string): 材质名称

**响应示例**:
```json
{
  "success": true,
  "data": [
    "布料",
    "纸张"
  ],
  "message": "找到 2 个相关材质",
  "timestamp": "2025-10-08T20:10:07.964843"
}
```

## 数据模型

### MaterialInfo
```json
{
  "name": "string",
  "properties": {
    "key": "value"
  },
  "hazards": ["string"],
  "safety_measures": ["string"]
}
```

### EnvironmentInfo
```json
{
  "location": "string",
  "conditions": {
    "key": "value"
  },
  "risks": ["string"],
  "recommendations": ["string"]
}
```

### RescueProcedure
```json
{
  "procedure_id": "string",
  "title": "string",
  "description": "string",
  "steps": ["string"],
  "materials_needed": ["string"],
  "safety_notes": ["string"]
}
```

### QueryResponse
```json
{
  "success": "boolean",
  "data": "any",
  "message": "string",
  "timestamp": "datetime"
}
```

## 错误处理

所有API都返回统一的错误格式：

```json
{
  "detail": "错误描述"
}
```

**HTTP状态码**:
- `200`: 成功
- `404`: 资源未找到
- `500`: 服务器内部错误

## 使用示例

### 使用curl

```bash
# 健康检查
curl http://localhost:8001/health

# 获取材质信息
curl http://localhost:8001/materials/木材

# 获取环境信息
curl http://localhost:8001/environments/住宅

# 获取救援程序
curl "http://localhost:8001/procedures?material_name=木材"

# 搜索材质
curl http://localhost:8001/materials/search/木

# 获取相关材质
curl http://localhost:8001/materials/木材/related
```

### 使用Python

```python
import httpx

# 创建HTTP客户端
async with httpx.AsyncClient() as client:
    # 获取材质信息
    response = await client.get("http://localhost:8001/materials/木材")
    material_data = response.json()
    
    # 获取救援程序
    response = await client.get("http://localhost:8001/procedures?material_name=木材")
    procedures = response.json()
```

## 启动服务

```bash
cd "C:\Users\ln281\Desktop\Fire Emergency RAG System"
python backend/services/knowledge_graph_service.py
```

服务将在 `http://localhost:8001` 启动，API文档可在 `http://localhost:8001/docs` 查看。
