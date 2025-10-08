"""
火灾应急救援RAG系统 - 统一异常处理
定义系统中所有服务使用的统一异常类
"""

from typing import Optional, Dict, Any
from datetime import datetime


class FireEmergencyError(Exception):
    """系统基础异常类"""
    
    def __init__(
        self,
        message: str,
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.details = details or {}
        self.timestamp = datetime.utcnow()


class ValidationError(FireEmergencyError):
    """数据验证异常"""
    
    def __init__(
        self,
        message: str,
        field: Optional[str] = None,
        value: Optional[Any] = None,
        **kwargs
    ):
        super().__init__(message, error_code="VALIDATION_ERROR", **kwargs)
        self.field = field
        self.value = value


class AuthenticationError(FireEmergencyError):
    """认证异常"""
    
    def __init__(self, message: str = "认证失败", **kwargs):
        super().__init__(message, error_code="AUTHENTICATION_ERROR", **kwargs)


class AuthorizationError(FireEmergencyError):
    """授权异常"""
    
    def __init__(self, message: str = "权限不足", **kwargs):
        super().__init__(message, error_code="AUTHORIZATION_ERROR", **kwargs)


class NotFoundError(FireEmergencyError):
    """资源未找到异常"""
    
    def __init__(self, message: str = "资源未找到", resource_type: Optional[str] = None, **kwargs):
        super().__init__(message, error_code="NOT_FOUND", **kwargs)
        self.resource_type = resource_type


class ConflictError(FireEmergencyError):
    """资源冲突异常"""
    
    def __init__(self, message: str = "资源冲突", **kwargs):
        super().__init__(message, error_code="CONFLICT", **kwargs)


class ServiceError(FireEmergencyError):
    """服务异常基类"""
    
    def __init__(
        self,
        message: str,
        service_name: str,
        error_code: Optional[str] = None,
        **kwargs
    ):
        super().__init__(message, error_code=error_code, **kwargs)
        self.service_name = service_name


class DatabaseError(ServiceError):
    """数据库异常"""
    
    def __init__(
        self,
        message: str,
        service_name: str,
        operation: Optional[str] = None,
        **kwargs
    ):
        super().__init__(
            message,
            service_name,
            error_code="DATABASE_ERROR",
            **kwargs
        )
        self.operation = operation


class DatabaseConnectionError(DatabaseError):
    """数据库连接异常"""
    
    def __init__(self, message: str, **kwargs):
        super().__init__(message, "database", operation="connection", **kwargs)


class QueryExecutionError(DatabaseError):
    """查询执行异常"""
    
    def __init__(self, message: str, **kwargs):
        super().__init__(message, "database", operation="query", **kwargs)


class ExternalServiceError(ServiceError):
    """外部服务异常"""
    
    def __init__(
        self,
        message: str,
        service_name: str,
        status_code: Optional[int] = None,
        **kwargs
    ):
        super().__init__(
            message,
            service_name,
            error_code="EXTERNAL_SERVICE_ERROR",
            **kwargs
        )
        self.status_code = status_code


class TimeoutError(ServiceError):
    """超时异常"""
    
    def __init__(
        self,
        message: str,
        service_name: str,
        timeout_duration: Optional[float] = None,
        **kwargs
    ):
        super().__init__(
            message,
            service_name,
            error_code="TIMEOUT_ERROR",
            **kwargs
        )
        self.timeout_duration = timeout_duration


class ConfigurationError(FireEmergencyError):
    """配置异常"""
    
    def __init__(
        self,
        message: str,
        config_key: Optional[str] = None,
        **kwargs
    ):
        super().__init__(message, error_code="CONFIGURATION_ERROR", **kwargs)
        self.config_key = config_key


class BusinessLogicError(FireEmergencyError):
    """业务逻辑异常"""
    
    def __init__(
        self,
        message: str,
        operation: Optional[str] = None,
        **kwargs
    ):
        super().__init__(message, error_code="BUSINESS_LOGIC_ERROR", **kwargs)
        self.operation = operation


# 特定服务异常
class KnowledgeGraphError(ServiceError):
    """知识图谱服务异常"""
    
    def __init__(self, message: str, **kwargs):
        super().__init__(message, "knowledge_graph", **kwargs)


class RAGServiceError(ServiceError):
    """RAG服务异常"""
    
    def __init__(self, message: str, **kwargs):
        super().__init__(message, "rag_service", **kwargs)


class OllamaServiceError(ServiceError):
    """Ollama服务异常"""
    
    def __init__(self, message: str, **kwargs):
        super().__init__(message, "ollama_service", **kwargs)


class CacheServiceError(ServiceError):
    """缓存服务异常"""
    
    def __init__(self, message: str, **kwargs):
        super().__init__(message, "cache_service", **kwargs)


class EmergencyServiceError(ServiceError):
    """应急服务异常"""
    
    def __init__(self, message: str, **kwargs):
        super().__init__(message, "emergency_service", **kwargs)


class UserServiceError(ServiceError):
    """用户服务异常"""
    
    def __init__(self, message: str, **kwargs):
        super().__init__(message, "user_service", **kwargs)


class AdminServiceError(ServiceError):
    """管理服务异常"""
    
    def __init__(self, message: str, **kwargs):
        super().__init__(message, "admin_service", **kwargs)


# 异常处理工具函数
def handle_exception(exc: Exception) -> Dict[str, Any]:
    """
    统一异常处理函数
    
    Args:
        exc: 异常对象
        
    Returns:
        Dict[str, Any]: 标准化的错误响应
    """
    if isinstance(exc, FireEmergencyError):
        return {
            "error": exc.error_code or "UNKNOWN_ERROR",
            "message": exc.message,
            "details": exc.details,
            "timestamp": exc.timestamp.isoformat(),
            "service_name": getattr(exc, "service_name", None)
        }
    else:
        return {
            "error": "INTERNAL_ERROR",
            "message": str(exc),
            "details": {},
            "timestamp": datetime.utcnow().isoformat(),
            "service_name": None
        }


def get_http_status_code(exc: Exception) -> int:
    """
    根据异常类型获取HTTP状态码
    
    Args:
        exc: 异常对象
        
    Returns:
        int: HTTP状态码
    """
    if isinstance(exc, ValidationError):
        return 400
    elif isinstance(exc, AuthenticationError):
        return 401
    elif isinstance(exc, AuthorizationError):
        return 403
    elif isinstance(exc, NotFoundError):
        return 404
    elif isinstance(exc, ConflictError):
        return 409
    elif isinstance(exc, TimeoutError):
        return 408
    elif isinstance(exc, ExternalServiceError):
        return 502
    elif isinstance(exc, ConfigurationError):
        return 500
    else:
        return 500
