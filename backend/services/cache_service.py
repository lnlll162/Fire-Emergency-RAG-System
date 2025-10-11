#!/usr/bin/env python3
"""
缓存服务
提供高性能缓存功能，包括Redis连接管理、缓存CRUD操作、缓存策略等
"""

import asyncio
import logging
import sys
import json
import hashlib
import time
from typing import List, Dict, Any, Optional, Union, Tuple
from datetime import datetime, timedelta
from pathlib import Path
from enum import Enum

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from pydantic import BaseModel, Field
import redis
import redis.asyncio as aioredis
from redis.exceptions import RedisError, ConnectionError, TimeoutError as RedisTimeoutError

from shared.config import get_config
from shared.exceptions import DatabaseConnectionError, ServiceError, TimeoutError

# 配置日志
logger = logging.getLogger(__name__)

# 数据模型
class CacheStrategy(str, Enum):
    """缓存策略枚举"""
    LRU = "lru"  # 最近最少使用
    LFU = "lfu"  # 最少使用频率
    TTL = "ttl"  # 基于时间过期
    FIFO = "fifo"  # 先进先出

class CacheOperation(str, Enum):
    """缓存操作枚举"""
    GET = "get"
    SET = "set"
    DELETE = "delete"
    EXISTS = "exists"
    EXPIRE = "expire"
    TTL = "ttl"
    KEYS = "keys"
    FLUSH = "flush"

class CacheItem(BaseModel):
    """缓存项模型"""
    key: str = Field(..., description="缓存键", min_length=1, max_length=500)
    value: Any = Field(..., description="缓存值")
    ttl: Optional[int] = Field(None, description="生存时间(秒)", ge=1, le=86400)
    strategy: CacheStrategy = Field(default=CacheStrategy.TTL, description="缓存策略")
    created_at: datetime = Field(default_factory=datetime.now, description="创建时间")
    updated_at: datetime = Field(default_factory=datetime.now, description="更新时间")
    access_count: int = Field(default=0, description="访问次数")
    last_accessed: datetime = Field(default_factory=datetime.now, description="最后访问时间")

class CacheStats(BaseModel):
    """缓存统计信息"""
    total_keys: int = Field(..., description="总键数")
    memory_usage: int = Field(..., description="内存使用量(字节)")
    hit_count: int = Field(..., description="命中次数")
    miss_count: int = Field(..., description="未命中次数")
    hit_rate: float = Field(..., description="命中率")
    eviction_count: int = Field(..., description="淘汰次数")
    connection_count: int = Field(..., description="连接数")
    uptime: float = Field(..., description="运行时间(秒)")

class CacheRequest(BaseModel):
    """缓存请求模型"""
    key: str = Field(..., description="缓存键", min_length=1, max_length=500)
    value: Optional[Any] = Field(None, description="缓存值")
    ttl: Optional[int] = Field(None, description="生存时间(秒)", ge=1, le=86400)
    strategy: CacheStrategy = Field(default=CacheStrategy.TTL, description="缓存策略")
    operation: CacheOperation = Field(..., description="操作类型")

class CacheResponse(BaseModel):
    """缓存响应模型"""
    success: bool = Field(..., description="操作是否成功")
    data: Optional[Any] = Field(None, description="响应数据")
    message: str = Field(..., description="响应消息")
    execution_time: float = Field(..., description="执行时间(毫秒)")
    timestamp: datetime = Field(default_factory=datetime.now, description="时间戳")

class BatchCacheRequest(BaseModel):
    """批量缓存请求模型"""
    operations: List[CacheRequest] = Field(..., description="操作列表", min_length=1, max_length=100)
    atomic: bool = Field(default=True, description="是否原子操作")

class QueryResponse(BaseModel):
    """查询响应模型"""
    success: bool = Field(..., description="查询是否成功")
    data: Any = Field(..., description="查询结果数据")
    message: str = Field(default="", description="响应消息")
    timestamp: datetime = Field(default_factory=datetime.now, description="响应时间")

class CacheService:
    """缓存服务类"""
    
    def __init__(self):
        self.config = get_config()
        self.redis_client = None
        self.connection_pool = None
        self.stats = {
            "hit_count": 0,
            "miss_count": 0,
            "eviction_count": 0,
            "start_time": time.time()
        }
        self._initialize_connection()
    
    def _initialize_connection(self):
        """初始化Redis连接"""
        try:
            # 创建连接池
            self.connection_pool = redis.ConnectionPool(
                host=self.config.database.redis_host,
                port=self.config.database.redis_port,
                password=self.config.database.redis_password,
                db=self.config.database.redis_db,
                max_connections=self.config.database.redis_pool_size,
                retry_on_timeout=True,
                socket_connect_timeout=5,
                socket_timeout=5
            )
            
            # 创建Redis客户端
            self.redis_client = redis.Redis(
                connection_pool=self.connection_pool,
                decode_responses=True
            )
            
            # 测试连接
            self.redis_client.ping()
            logger.info("Redis连接初始化成功")
        except Exception as e:
            logger.error(f"Redis连接初始化失败: {str(e)}")
            raise DatabaseConnectionError(f"无法连接到Redis数据库: {str(e)}")
    
    async def test_connection(self) -> bool:
        """测试数据库连接"""
        try:
            self.redis_client.ping()
            return True
        except Exception as e:
            logger.error(f"Redis连接测试失败: {str(e)}")
            return False
    
    def _serialize_value(self, value: Any) -> str:
        """序列化值"""
        if isinstance(value, (str, int, float, bool)):
            return str(value)
        return json.dumps(value, ensure_ascii=False, default=str)
    
    def _deserialize_value(self, value: str) -> Any:
        """反序列化值"""
        try:
            return json.loads(value)
        except (json.JSONDecodeError, TypeError):
            return value
    
    def _generate_key(self, key: str, namespace: str = "default") -> str:
        """生成带命名空间的键"""
        return f"{namespace}:{key}"
    
    def _update_stats(self, hit: bool = None, eviction: bool = False):
        """更新统计信息"""
        if hit is not None:
            if hit:
                self.stats["hit_count"] += 1
            else:
                self.stats["miss_count"] += 1
        
        if eviction:
            self.stats["eviction_count"] += 1
    
    def _calculate_hit_rate(self) -> float:
        """计算命中率"""
        total = self.stats["hit_count"] + self.stats["miss_count"]
        return self.stats["hit_count"] / total if total > 0 else 0.0
    
    async def get(self, key: str, namespace: str = "default") -> Optional[Any]:
        """获取缓存值"""
        try:
            full_key = self._generate_key(key, namespace)
            value = self.redis_client.get(full_key)
            
            if value is not None:
                self._update_stats(hit=True)
                return self._deserialize_value(value)
            else:
                self._update_stats(hit=False)
                return None
        except Exception as e:
            logger.error(f"获取缓存失败: {str(e)}")
            raise ServiceError(f"获取缓存失败: {str(e)}", "cache_service")
    
    async def set(self, key: str, value: Any, ttl: Optional[int] = None, 
                  namespace: str = "default", strategy: CacheStrategy = CacheStrategy.TTL) -> bool:
        """设置缓存值"""
        try:
            full_key = self._generate_key(key, namespace)
            serialized_value = self._serialize_value(value)
            
            if ttl:
                result = self.redis_client.setex(full_key, ttl, serialized_value)
            else:
                result = self.redis_client.set(full_key, serialized_value)
            
            return bool(result)
        except Exception as e:
            logger.error(f"设置缓存失败: {str(e)}")
            raise ServiceError(f"设置缓存失败: {str(e)}", "cache_service")
    
    async def delete(self, key: str, namespace: str = "default") -> bool:
        """删除缓存值"""
        try:
            full_key = self._generate_key(key, namespace)
            result = self.redis_client.delete(full_key)
            return bool(result)
        except Exception as e:
            logger.error(f"删除缓存失败: {str(e)}")
            raise ServiceError(f"删除缓存失败: {str(e)}", "cache_service")
    
    async def exists(self, key: str, namespace: str = "default") -> bool:
        """检查键是否存在"""
        try:
            full_key = self._generate_key(key, namespace)
            return bool(self.redis_client.exists(full_key))
        except Exception as e:
            logger.error(f"检查键存在性失败: {str(e)}")
            raise ServiceError(f"检查键存在性失败: {str(e)}", "cache_service")
    
    async def expire(self, key: str, ttl: int, namespace: str = "default") -> bool:
        """设置键的过期时间"""
        try:
            full_key = self._generate_key(key, namespace)
            return bool(self.redis_client.expire(full_key, ttl))
        except Exception as e:
            logger.error(f"设置过期时间失败: {str(e)}")
            raise ServiceError(f"设置过期时间失败: {str(e)}", "cache_service")
    
    async def ttl(self, key: str, namespace: str = "default") -> int:
        """获取键的剩余生存时间"""
        try:
            full_key = self._generate_key(key, namespace)
            return self.redis_client.ttl(full_key)
        except Exception as e:
            logger.error(f"获取TTL失败: {str(e)}")
            raise ServiceError(f"获取TTL失败: {str(e)}", "cache_service")
    
    async def keys(self, pattern: str = "*", namespace: str = "default") -> List[str]:
        """获取匹配的键列表"""
        try:
            full_pattern = self._generate_key(pattern, namespace)
            keys = self.redis_client.keys(full_pattern)
            # 移除命名空间前缀
            return [key.replace(f"{namespace}:", "", 1) for key in keys]
        except Exception as e:
            logger.error(f"获取键列表失败: {str(e)}")
            raise ServiceError(f"获取键列表失败: {str(e)}", "cache_service")
    
    async def flush(self, namespace: str = "default") -> bool:
        """清空指定命名空间的缓存"""
        try:
            if namespace == "all":
                self.redis_client.flushdb()
            else:
                pattern = f"{namespace}:*"
                keys = self.redis_client.keys(pattern)
                if keys:
                    self.redis_client.delete(*keys)
            return True
        except Exception as e:
            logger.error(f"清空缓存失败: {str(e)}")
            raise ServiceError(f"清空缓存失败: {str(e)}", "cache_service")
    
    async def batch_operations(self, operations: List[CacheRequest], 
                              namespace: str = "default", atomic: bool = True) -> List[CacheResponse]:
        """批量执行缓存操作"""
        try:
            results = []
            
            if atomic:
                # 原子操作：使用管道
                pipe = self.redis_client.pipeline()
                for op in operations:
                    full_key = self._generate_key(op.key, namespace)
                    
                    if op.operation == CacheOperation.GET:
                        pipe.get(full_key)
                    elif op.operation == CacheOperation.SET:
                        serialized_value = self._serialize_value(op.value)
                        if op.ttl:
                            pipe.setex(full_key, op.ttl, serialized_value)
                        else:
                            pipe.set(full_key, serialized_value)
                    elif op.operation == CacheOperation.DELETE:
                        pipe.delete(full_key)
                    elif op.operation == CacheOperation.EXISTS:
                        pipe.exists(full_key)
                    elif op.operation == CacheOperation.EXPIRE:
                        pipe.expire(full_key, op.ttl or 3600)
                    elif op.operation == CacheOperation.TTL:
                        pipe.ttl(full_key)
                
                # 执行管道
                pipe_results = pipe.execute()
                
                # 处理结果
                for i, op in enumerate(operations):
                    result = pipe_results[i]
                    if op.operation == CacheOperation.GET:
                        value = self._deserialize_value(result) if result else None
                        self._update_stats(hit=result is not None)
                    else:
                        value = result
                    
                    results.append(CacheResponse(
                        success=True,
                        data=value,
                        message=f"操作 {op.operation.value} 执行成功",
                        execution_time=0.0
                    ))
            else:
                # 非原子操作：逐个执行
                for op in operations:
                    start_time = time.time()
                    try:
                        if op.operation == CacheOperation.GET:
                            value = await self.get(op.key, namespace)
                            result = CacheResponse(
                                success=True,
                                data=value,
                                message="获取成功" if value is not None else "键不存在",
                                execution_time=(time.time() - start_time) * 1000
                            )
                        elif op.operation == CacheOperation.SET:
                            success = await self.set(op.key, op.value, op.ttl, namespace, op.strategy)
                            result = CacheResponse(
                                success=success,
                                data=success,
                                message="设置成功" if success else "设置失败",
                                execution_time=(time.time() - start_time) * 1000
                            )
                        elif op.operation == CacheOperation.DELETE:
                            success = await self.delete(op.key, namespace)
                            result = CacheResponse(
                                success=success,
                                data=success,
                                message="删除成功" if success else "键不存在",
                                execution_time=(time.time() - start_time) * 1000
                            )
                        elif op.operation == CacheOperation.EXISTS:
                            exists = await self.exists(op.key, namespace)
                            result = CacheResponse(
                                success=True,
                                data=exists,
                                message="键存在" if exists else "键不存在",
                                execution_time=(time.time() - start_time) * 1000
                            )
                        elif op.operation == CacheOperation.EXPIRE:
                            success = await self.expire(op.key, op.ttl or 3600, namespace)
                            result = CacheResponse(
                                success=success,
                                data=success,
                                message="设置过期时间成功" if success else "设置失败",
                                execution_time=(time.time() - start_time) * 1000
                            )
                        elif op.operation == CacheOperation.TTL:
                            ttl_value = await self.ttl(op.key, namespace)
                            result = CacheResponse(
                                success=True,
                                data=ttl_value,
                                message=f"TTL: {ttl_value}",
                                execution_time=(time.time() - start_time) * 1000
                            )
                        else:
                            result = CacheResponse(
                                success=False,
                                data=None,
                                message=f"不支持的操作: {op.operation}",
                                execution_time=(time.time() - start_time) * 1000
                            )
                    except Exception as e:
                        result = CacheResponse(
                            success=False,
                            data=None,
                            message=f"操作失败: {str(e)}",
                            execution_time=(time.time() - start_time) * 1000
                        )
                    
                    results.append(result)
            
            return results
        except Exception as e:
            logger.error(f"批量操作失败: {str(e)}")
            raise ServiceError(f"批量操作失败: {str(e)}", "cache_service")
    
    async def get_stats(self) -> CacheStats:
        """获取缓存统计信息"""
        try:
            # 获取Redis信息
            info = self.redis_client.info()
            
            # 计算运行时间
            uptime = time.time() - self.stats["start_time"]
            
            # 计算命中率
            hit_rate = self._calculate_hit_rate()
            
            return CacheStats(
                total_keys=info.get("db0", {}).get("keys", 0),
                memory_usage=info.get("used_memory", 0),
                hit_count=self.stats["hit_count"],
                miss_count=self.stats["miss_count"],
                hit_rate=hit_rate,
                eviction_count=self.stats["eviction_count"],
                connection_count=info.get("connected_clients", 0),
                uptime=uptime
            )
        except Exception as e:
            logger.error(f"获取统计信息失败: {str(e)}")
            raise ServiceError(f"获取统计信息失败: {str(e)}", "cache_service")
    
    async def warmup(self, warmup_data: Dict[str, Any], namespace: str = "default") -> bool:
        """缓存预热"""
        try:
            logger.info(f"开始缓存预热，数据量: {len(warmup_data)}")
            
            success_count = 0
            for key, value in warmup_data.items():
                try:
                    await self.set(key, value, namespace=namespace)
                    success_count += 1
                except Exception as e:
                    logger.warning(f"预热键 {key} 失败: {str(e)}")
            
            logger.info(f"缓存预热完成，成功: {success_count}/{len(warmup_data)}")
            return success_count == len(warmup_data)
        except Exception as e:
            logger.error(f"缓存预热失败: {str(e)}")
            raise ServiceError(f"缓存预热失败: {str(e)}", "cache_service")
    
    async def health_check(self) -> Dict[str, Any]:
        """健康检查"""
        try:
            # 测试连接
            is_connected = await self.test_connection()
            
            # 获取基本信息
            info = self.redis_client.info() if is_connected else {}
            
            return {
                "status": "healthy" if is_connected else "unhealthy",
                "connected": is_connected,
                "version": info.get("redis_version", "unknown"),
                "uptime": info.get("uptime_in_seconds", 0),
                "memory_usage": info.get("used_memory_human", "unknown"),
                "connected_clients": info.get("connected_clients", 0)
            }
        except Exception as e:
            logger.error(f"健康检查失败: {str(e)}")
            return {
                "status": "unhealthy",
                "connected": False,
                "error": str(e)
            }
    
    def close(self):
        """关闭连接"""
        if self.redis_client:
            self.redis_client.close()
        if self.connection_pool:
            self.connection_pool.disconnect()
        logger.info("Redis连接已关闭")

# 创建服务实例（延迟初始化）
cache_service = None

def get_cache_service_instance():
    """获取缓存服务实例（延迟初始化）"""
    global cache_service
    if cache_service is None:
        cache_service = CacheService()
    return cache_service

# FastAPI应用
app = FastAPI(
    title="缓存服务",
    description="高性能缓存服务，提供Redis连接管理和缓存操作功能",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# 依赖注入
def get_cache_service() -> CacheService:
    return get_cache_service_instance()

# API路由
@app.get("/", response_model=QueryResponse)
async def root():
    """根路径 - 服务信息"""
    return QueryResponse(
        success=True,
        data={
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
        message="缓存服务运行正常"
    )

@app.get("/health", response_model=QueryResponse)
async def health_check(service: CacheService = Depends(get_cache_service)):
    """健康检查"""
    try:
        health_info = await service.health_check()
        return QueryResponse(
            success=health_info["status"] == "healthy",
            data=health_info,
            message="健康检查完成"
        )
    except Exception as e:
        return QueryResponse(
            success=False,
            data={"status": "unhealthy", "error": str(e)},
            message=f"健康检查失败: {str(e)}"
        )

@app.get("/get/{key}", response_model=CacheResponse)
async def get_cache(
    key: str,
    namespace: str = "default",
    service: CacheService = Depends(get_cache_service)
):
    """获取缓存值"""
    try:
        start_time = time.time()
        value = await service.get(key, namespace)
        execution_time = (time.time() - start_time) * 1000
        
        return CacheResponse(
            success=True,
            data=value,
            message="获取成功" if value is not None else "键不存在",
            execution_time=execution_time
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取缓存失败: {str(e)}")

@app.post("/set", response_model=CacheResponse)
async def set_cache(
    key: str,
    value: Any,
    ttl: Optional[int] = None,
    namespace: str = "default",
    strategy: CacheStrategy = CacheStrategy.TTL,
    service: CacheService = Depends(get_cache_service)
):
    """设置缓存值"""
    try:
        start_time = time.time()
        success = await service.set(key, value, ttl, namespace, strategy)
        execution_time = (time.time() - start_time) * 1000
        
        return CacheResponse(
            success=success,
            data=success,
            message="设置成功" if success else "设置失败",
            execution_time=execution_time
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"设置缓存失败: {str(e)}")

@app.delete("/delete/{key}", response_model=CacheResponse)
async def delete_cache(
    key: str,
    namespace: str = "default",
    service: CacheService = Depends(get_cache_service)
):
    """删除缓存值"""
    try:
        start_time = time.time()
        success = await service.delete(key, namespace)
        execution_time = (time.time() - start_time) * 1000
        
        return CacheResponse(
            success=success,
            data=success,
            message="删除成功" if success else "键不存在",
            execution_time=execution_time
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"删除缓存失败: {str(e)}")

@app.get("/exists/{key}", response_model=CacheResponse)
async def exists_cache(
    key: str,
    namespace: str = "default",
    service: CacheService = Depends(get_cache_service)
):
    """检查键是否存在"""
    try:
        start_time = time.time()
        exists = await service.exists(key, namespace)
        execution_time = (time.time() - start_time) * 1000
        
        return CacheResponse(
            success=True,
            data=exists,
            message="键存在" if exists else "键不存在",
            execution_time=execution_time
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"检查键存在性失败: {str(e)}")

@app.get("/keys", response_model=QueryResponse)
async def list_keys(
    pattern: str = "*",
    namespace: str = "default",
    service: CacheService = Depends(get_cache_service)
):
    """获取键列表"""
    try:
        keys = await service.keys(pattern, namespace)
        return QueryResponse(
            success=True,
            data=keys,
            message=f"找到 {len(keys)} 个键"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取键列表失败: {str(e)}")

@app.get("/stats", response_model=QueryResponse)
async def get_stats(service: CacheService = Depends(get_cache_service)):
    """获取统计信息"""
    try:
        stats = await service.get_stats()
        return QueryResponse(
            success=True,
            data=stats.model_dump(),
            message="统计信息获取成功"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取统计信息失败: {str(e)}")

@app.post("/warmup", response_model=QueryResponse)
async def warmup_cache(
    warmup_data: Dict[str, Any],
    namespace: str = "default",
    service: CacheService = Depends(get_cache_service)
):
    """缓存预热"""
    try:
        success = await service.warmup(warmup_data, namespace)
        return QueryResponse(
            success=success,
            data={"warmed_up": success, "count": len(warmup_data)},
            message="缓存预热成功" if success else "缓存预热部分失败"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"缓存预热失败: {str(e)}")

@app.post("/batch", response_model=QueryResponse)
async def batch_operations(
    request: BatchCacheRequest,
    namespace: str = "default",
    service: CacheService = Depends(get_cache_service)
):
    """批量操作"""
    try:
        results = await service.batch_operations(
            request.operations, 
            namespace, 
            request.atomic
        )
        return QueryResponse(
            success=True,
            data=[result.model_dump() for result in results],
            message=f"批量操作完成，共 {len(results)} 个操作"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"批量操作失败: {str(e)}")

@app.post("/flush", response_model=QueryResponse)
async def flush_cache(
    namespace: str = "default",
    service: CacheService = Depends(get_cache_service)
):
    """清空缓存"""
    try:
        success = await service.flush(namespace)
        return QueryResponse(
            success=success,
            data={"flushed": success, "namespace": namespace},
            message="缓存清空成功" if success else "缓存清空失败"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"清空缓存失败: {str(e)}")

# 启动和关闭事件
@app.on_event("startup")
async def startup_event():
    """应用启动事件"""
    logger.info("缓存服务启动中...")
    try:
        service = get_cache_service_instance()
        is_healthy = await service.test_connection()
        if is_healthy:
            logger.info("缓存服务启动成功")
        else:
            logger.warning("缓存服务启动，但Redis连接异常")
    except Exception as e:
        logger.error(f"缓存服务启动失败: {str(e)}")

@app.on_event("shutdown")
async def shutdown_event():
    """应用关闭事件"""
    logger.info("缓存服务关闭中...")
    if cache_service:
        cache_service.close()
    logger.info("缓存服务已关闭")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8004)
