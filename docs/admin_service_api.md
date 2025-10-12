# 管理服务 API 文档

## 概述

管理服务提供系统监控、数据管理、日志查询、健康检查等管理功能。

**服务端口**: 8005  
**基础URL**: `http://localhost:8005`

## 接口列表

### 1. 服务信息

#### GET /

获取服务基本信息。

**响应示例**:
```json
{
  "success": true,
  "message": "管理服务运行正常",
  "data": {
    "service": "管理服务",
    "version": "1.0.0",
    "description": "系统监控、数据管理、日志查询、健康检查服务",
    "endpoints": {
      "health": "/health",
      "system_metrics": "/system/metrics",
      "service_status": "/services/status",
      "data_stats": "/data/statistics",
      "logs": "/logs",
      "backups": "/backups",
      "cleanup": "/cleanup",
      "docs": "/docs"
    }
  }
}
```

### 2. 健康检查

#### GET /health

获取系统整体健康状态。

**响应示例**:
```json
{
  "success": true,
  "message": "健康检查完成",
  "data": {
    "overall_status": "healthy",
    "services": [
      {
        "name": "emergency_service",
        "status": "healthy",
        "port": 8000,
        "response_time": 15.5,
        "last_check": "2024-01-01T12:00:00Z",
        "error_message": null,
        "version": "1.0.0",
        "uptime": 3600.0
      }
    ],
    "databases": [
      {
        "name": "postgresql",
        "status": "healthy",
        "connection_count": 5,
        "size_mb": 100.5,
        "last_backup": "2024-01-01T10:00:00Z",
        "error_message": null
      }
    ],
    "system_metrics": {
      "timestamp": "2024-01-01T12:00:00Z",
      "cpu_usage": 45.2,
      "memory_usage": 62.8,
      "disk_usage": 35.5,
      "network_io": {
        "bytes_sent": 1024000,
        "bytes_recv": 2048000,
        "packets_sent": 1000,
        "packets_recv": 2000
      },
      "process_count": 25,
      "load_average": [1.2, 1.5, 1.8]
    },
    "check_time": "2024-01-01T12:00:00Z"
  }
}
```

### 3. 系统指标

#### GET /system/metrics

获取系统性能指标。

**响应示例**:
```json
{
  "success": true,
  "message": "系统指标获取成功",
  "data": {
    "timestamp": "2024-01-01T12:00:00Z",
    "cpu_usage": 45.2,
    "memory_usage": 62.8,
    "disk_usage": 35.5,
    "network_io": {
      "bytes_sent": 1024000,
      "bytes_recv": 2048000,
      "packets_sent": 1000,
      "packets_recv": 2000
    },
    "process_count": 25,
    "load_average": [1.2, 1.5, 1.8]
  }
}
```

### 4. 服务状态

#### GET /services/status

获取所有服务的状态信息。

**响应示例**:
```json
{
  "success": true,
  "message": "服务状态获取成功",
  "data": {
    "overall_status": "healthy",
    "services": [
      {
        "name": "emergency_service",
        "status": "healthy",
        "port": 8000,
        "response_time": 15.5,
        "last_check": "2024-01-01T12:00:00Z",
        "error_message": null
      },
      {
        "name": "knowledge_graph_service",
        "status": "healthy",
        "port": 8001,
        "response_time": 8.2,
        "last_check": "2024-01-01T12:00:00Z",
        "error_message": null
      }
    ]
  }
}
```

### 5. 数据统计

#### GET /data/statistics

获取系统数据统计信息。

**响应示例**:
```json
{
  "success": true,
  "message": "数据统计获取成功",
  "data": {
    "total_users": 150,
    "total_rescue_plans": 75,
    "total_documents": 500,
    "total_knowledge_nodes": 1000,
    "cache_hit_rate": 0.85,
    "last_updated": "2024-01-01T12:00:00Z"
  }
}
```

### 6. 日志查询

#### POST /logs/query

查询系统日志。

**请求体**:
```json
{
  "start_time": "2024-01-01T10:00:00Z",
  "end_time": "2024-01-01T12:00:00Z",
  "level": "ERROR",
  "service": "emergency_service",
  "keyword": "error",
  "limit": 100
}
```

**响应示例**:
```json
{
  "success": true,
  "message": "日志查询成功",
  "data": [
    {
      "id": "log_1",
      "timestamp": "2024-01-01T11:30:00Z",
      "level": "ERROR",
      "service": "emergency_service",
      "message": "Database connection failed",
      "metadata": {
        "trace_id": "trace_123",
        "user_id": "user_456"
      },
      "trace_id": "trace_123"
    }
  ]
}
```

### 7. 备份管理

#### POST /backups/create

创建系统备份。

**请求参数**:
- `backup_type` (string): 备份类型 (full, incremental, differential)
- `name` (string): 备份名称

**响应示例**:
```json
{
  "success": true,
  "message": "备份创建成功",
  "data": {
    "id": "backup_1704067200",
    "name": "daily_backup_2024-01-01",
    "type": "full",
    "size_mb": 0.0,
    "created_at": "2024-01-01T12:00:00Z",
    "status": "in_progress",
    "location": "/backups/backup_1704067200"
  }
}
```

#### GET /backups

获取所有备份列表。

**响应示例**:
```json
{
  "success": true,
  "message": "备份列表获取成功",
  "data": [
    {
      "id": "backup_1704067200",
      "name": "daily_backup_2024-01-01",
      "type": "full",
      "size_mb": 150.5,
      "created_at": "2024-01-01T12:00:00Z",
      "status": "completed",
      "location": "/backups/backup_1704067200"
    }
  ]
}
```

### 8. 数据清理

#### POST /cleanup

清理旧数据。

**请求参数**:
- `days` (integer): 保留天数，默认30天

**响应示例**:
```json
{
  "success": true,
  "message": "数据清理完成",
  "data": {
    "deleted_logs": 1000,
    "deleted_backups": 5,
    "freed_space_mb": 500.0,
    "cleanup_time": "2024-01-01T12:00:00Z"
  }
}
```

## 数据模型

### ServiceStatus 枚举
- `healthy`: 健康
- `unhealthy`: 不健康
- `unknown`: 未知
- `starting`: 启动中
- `stopping`: 停止中

### LogLevel 枚举
- `DEBUG`: 调试
- `INFO`: 信息
- `WARNING`: 警告
- `ERROR`: 错误
- `CRITICAL`: 严重

### SystemMetrics 模型
```json
{
  "timestamp": "2024-01-01T12:00:00Z",
  "cpu_usage": 45.2,
  "memory_usage": 62.8,
  "disk_usage": 35.5,
  "network_io": {
    "bytes_sent": 1024000,
    "bytes_recv": 2048000,
    "packets_sent": 1000,
    "packets_recv": 2000
  },
  "process_count": 25,
  "load_average": [1.2, 1.5, 1.8]
}
```

### ServiceInfo 模型
```json
{
  "name": "service_name",
  "status": "healthy",
  "port": 8000,
  "response_time": 15.5,
  "last_check": "2024-01-01T12:00:00Z",
  "error_message": null,
  "version": "1.0.0",
  "uptime": 3600.0
}
```

### DatabaseInfo 模型
```json
{
  "name": "postgresql",
  "status": "healthy",
  "connection_count": 5,
  "size_mb": 100.5,
  "last_backup": "2024-01-01T10:00:00Z",
  "error_message": null
}
```

### LogEntry 模型
```json
{
  "id": "log_1",
  "timestamp": "2024-01-01T11:30:00Z",
  "level": "ERROR",
  "service": "emergency_service",
  "message": "Database connection failed",
  "metadata": {
    "trace_id": "trace_123",
    "user_id": "user_456"
  },
  "trace_id": "trace_123"
}
```

### LogQuery 模型
```json
{
  "start_time": "2024-01-01T10:00:00Z",
  "end_time": "2024-01-01T12:00:00Z",
  "level": "ERROR",
  "service": "emergency_service",
  "keyword": "error",
  "limit": 100
}
```

### BackupInfo 模型
```json
{
  "id": "backup_1704067200",
  "name": "daily_backup_2024-01-01",
  "type": "full",
  "size_mb": 150.5,
  "created_at": "2024-01-01T12:00:00Z",
  "status": "completed",
  "location": "/backups/backup_1704067200"
}
```

### DataStats 模型
```json
{
  "total_users": 150,
  "total_rescue_plans": 75,
  "total_documents": 500,
  "total_knowledge_nodes": 1000,
  "cache_hit_rate": 0.85,
  "last_updated": "2024-01-01T12:00:00Z"
}
```

## 错误处理

所有接口都遵循统一的错误响应格式：

```json
{
  "success": false,
  "message": "错误描述",
  "data": {
    "error": "ERROR_CODE",
    "details": "详细错误信息"
  }
}
```

常见HTTP状态码：
- `200`: 成功
- `400`: 请求参数错误
- `500`: 服务器内部错误

## 使用示例

### 检查系统健康状态
```bash
curl -X GET "http://localhost:8005/health"
```

### 获取系统指标
```bash
curl -X GET "http://localhost:8005/system/metrics"
```

### 查询错误日志
```bash
curl -X POST "http://localhost:8005/logs/query" \
  -H "Content-Type: application/json" \
  -d '{
    "level": "ERROR",
    "limit": 50
  }'
```

### 创建备份
```bash
curl -X POST "http://localhost:8005/backups/create?backup_type=full&name=daily_backup"
```

### 清理30天前的数据
```bash
curl -X POST "http://localhost:8005/cleanup?days=30"
```
