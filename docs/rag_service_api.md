# RAG服务API文档

## 概述

RAG（检索增强生成）服务提供文档管理、语义搜索和上下文增强功能。服务运行在端口3000上。

## 基础信息

- **服务名称**: RAG服务
- **版本**: 1.0.0
- **端口**: 3000
- **基础URL**: `http://localhost:3000`
- **API文档**: `http://localhost:3000/docs`

## 数据模型

### DocumentInfo
```json
{
  "id": "string",
  "title": "string",
  "content": "string",
  "metadata": {},
  "created_at": "datetime",
  "updated_at": "datetime"
}
```

### SearchResult
```json
{
  "document_id": "string",
  "title": "string",
  "content": "string",
  "score": "float",
  "metadata": {}
}
```

### SearchRequest
```json
{
  "query": "string",
  "limit": "integer",
  "filter_metadata": {}
}
```

### SearchResponse
```json
{
  "query": "string",
  "results": [SearchResult],
  "total_count": "integer",
  "search_time": "float"
}
```

### ContextEnhancementRequest
```json
{
  "query": "string",
  "context_documents": [SearchResult],
  "max_context_length": "integer"
}
```

### ContextEnhancementResponse
```json
{
  "enhanced_query": "string",
  "context_summary": "string",
  "relevant_sections": ["string"],
  "confidence_score": "float"
}
```

## API端点

### 1. 服务信息

#### GET /
获取服务基本信息

**响应示例**:
```json
{
  "success": true,
  "data": {
    "service": "RAG服务",
    "version": "1.0.0",
    "description": "检索增强生成服务",
    "endpoints": {
      "health": "/health",
      "search": "/search",
      "documents": "/documents",
      "upload": "/upload",
      "stats": "/stats",
      "docs": "/docs"
    }
  },
  "message": "RAG服务运行正常",
  "timestamp": "2025-10-08T20:44:42.956802"
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
    "status": "healthy"
  },
  "message": "服务健康检查完成",
  "timestamp": "2025-10-08T20:44:07.538095"
}
```

### 3. 文档管理

#### POST /documents
添加新文档到知识库

**请求参数**:
- `title` (string): 文档标题
- `content` (string): 文档内容
- `metadata` (object, 可选): 文档元数据

**响应示例**:
```json
{
  "document_id": "doc_1759927807597",
  "title": "火灾救援基础知识",
  "status": "success",
  "message": "文档添加成功"
}
```

#### GET /documents/{document_id}
获取指定文档的详细信息

**路径参数**:
- `document_id` (string): 文档ID

**响应示例**:
```json
{
  "success": true,
  "data": {
    "id": "doc_1759927807597",
    "title": "火灾救援基础知识",
    "content": "火灾是一种常见的灾害...",
    "metadata": {
      "created_at": "2025-10-08T20:50:07.597373",
      "title": "火灾救援基础知识",
      "updated_at": "2025-10-08T20:50:07.597378"
    },
    "created_at": "2025-10-08T20:50:07.597373",
    "updated_at": "2025-10-08T20:50:07.597378"
  },
  "message": "文档获取成功",
  "timestamp": "2025-10-08T20:50:07.597373"
}
```

#### PUT /documents/{document_id}
更新指定文档

**路径参数**:
- `document_id` (string): 文档ID

**请求参数**:
- `title` (string, 可选): 新标题
- `content` (string, 可选): 新内容
- `metadata` (object, 可选): 新元数据

**响应示例**:
```json
{
  "success": true,
  "data": {
    "document_id": "doc_1759927807597"
  },
  "message": "文档更新成功",
  "timestamp": "2025-10-08T20:50:07.597373"
}
```

#### DELETE /documents/{document_id}
删除指定文档

**路径参数**:
- `document_id` (string): 文档ID

**响应示例**:
```json
{
  "success": true,
  "data": {
    "document_id": "doc_1759927807597"
  },
  "message": "文档删除成功",
  "timestamp": "2025-10-08T20:50:07.597373"
}
```

### 4. 语义搜索

#### POST /search
搜索相关文档

**请求体**:
```json
{
  "query": "火灾救援",
  "limit": 10,
  "filter_metadata": {}
}
```

**响应示例**:
```json
{
  "query": "火灾救援",
  "results": [
    {
      "document_id": "doc_1759927807597",
      "title": "火灾救援基础知识",
      "content": "火灾是一种常见的灾害，需要及时有效的救援措施...",
      "score": 0.85465977,
      "metadata": {
        "created_at": "2025-10-08T20:50:07.597373",
        "title": "火灾救援基础知识",
        "updated_at": "2025-10-08T20:50:07.597378"
      }
    }
  ],
  "total_count": 1,
  "search_time": 0.009681
}
```

### 5. 上下文增强

#### POST /enhance-context
增强查询上下文

**请求体**:
```json
{
  "query": "如何应对火灾",
  "context_documents": [
    {
      "document_id": "doc_1759927807597",
      "title": "火灾救援基础知识",
      "content": "火灾是一种常见的灾害...",
      "score": 0.85465977,
      "metadata": {}
    }
  ],
  "max_context_length": 4000
}
```

**响应示例**:
```json
{
  "enhanced_query": "基于火灾救援知识库的查询: 如何应对火灾",
  "context_summary": "基于1个相关文档的上下文信息",
  "relevant_sections": [
    "火灾是一种常见的灾害",
    "需要及时有效的救援措施",
    "在火灾发生时，首先要确保人员安全"
  ],
  "confidence_score": 0.1
}
```

### 6. 统计信息

#### GET /stats
获取知识库统计信息

**响应示例**:
```json
{
  "success": true,
  "data": {
    "total_documents": 1,
    "collection_name": "fire_rescue_knowledge",
    "embedding_model": "simple_features"
  },
  "message": "统计信息获取成功",
  "timestamp": "2025-10-08T20:50:11.861857"
}
```

## 错误处理

### 常见错误码

- `400 Bad Request`: 请求参数错误
- `404 Not Found`: 资源不存在
- `422 Unprocessable Entity`: 请求格式错误
- `500 Internal Server Error`: 服务器内部错误

### 错误响应格式

```json
{
  "detail": [
    {
      "type": "error_type",
      "loc": ["field_name"],
      "msg": "错误描述",
      "input": "输入值"
    }
  ]
}
```

## 使用示例

### Python示例

```python
import requests

# 基础URL
RAG_URL = "http://localhost:3000"

# 1. 添加文档
doc_data = {
    "title": "火灾救援基础知识",
    "content": "火灾是一种常见的灾害，需要及时有效的救援措施。"
}
response = requests.post(f"{RAG_URL}/documents", params=doc_data)
print(response.json())

# 2. 搜索文档
search_data = {
    "query": "火灾救援",
    "limit": 5
}
response = requests.post(f"{RAG_URL}/search", json=search_data)
print(response.json())

# 3. 获取统计信息
response = requests.get(f"{RAG_URL}/stats")
print(response.json())
```

### curl示例

```bash
# 添加文档
curl -X POST "http://localhost:3000/documents" \
  -H "Content-Type: application/json" \
  -d "title=火灾救援基础知识&content=火灾是一种常见的灾害"

# 搜索文档
curl -X POST "http://localhost:3000/search" \
  -H "Content-Type: application/json" \
  -d '{"query": "火灾救援", "limit": 5}'

# 获取统计信息
curl "http://localhost:3000/stats"
```

## 技术特性

### 嵌入模型
- 主要模型: `paraphrase-multilingual-MiniLM-L12-v2`
- 备用方案: 简单特征向量（当主模型不可用时）
- 向量维度: 384

### 数据库
- ChromaDB: 向量数据库
- 集合名称: `fire_rescue_knowledge`
- 支持元数据过滤

### 性能特性
- 支持并发请求
- 自动文档嵌入生成
- 相似度搜索优化
- 上下文长度限制

## 注意事项

1. **文档大小**: 建议单个文档内容不超过10MB
2. **搜索限制**: 单次搜索最多返回100个结果
3. **上下文长度**: 默认最大上下文长度为4000字符
4. **编码支持**: 支持UTF-8编码的中文内容
5. **模型加载**: 首次启动时可能需要下载嵌入模型

## 更新日志

### v1.0.0 (2025-10-08)
- 初始版本发布
- 支持文档管理、语义搜索、上下文增强
- 集成ChromaDB向量数据库
- 提供完整的REST API
