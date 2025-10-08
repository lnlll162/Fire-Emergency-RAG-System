"""
火灾应急救援RAG系统 - 统一配置管理
管理所有服务的配置和环境变量
"""

import os
from typing import Optional, Dict, Any, List
from pydantic import Field, validator
from pydantic_settings import BaseSettings
from shared.service_registry import ServiceRegistry


class DatabaseConfig(BaseSettings):
    """数据库配置"""
    
    # PostgreSQL配置
    postgres_host: str = Field(default="localhost", env="POSTGRES_HOST")
    postgres_port: int = Field(default=5432, env="POSTGRES_PORT")
    postgres_db: str = Field(default="fire_emergency", env="POSTGRES_DB")
    postgres_user: str = Field(default="postgres", env="POSTGRES_USER")
    postgres_password: str = Field(default="password", env="POSTGRES_PASSWORD")
    postgres_pool_size: int = Field(default=20, env="POSTGRES_POOL_SIZE")
    postgres_max_overflow: int = Field(default=30, env="POSTGRES_MAX_OVERFLOW")
    
    # Redis配置
    redis_host: str = Field(default="localhost", env="REDIS_HOST")
    redis_port: int = Field(default=6379, env="REDIS_PORT")
    redis_password: Optional[str] = Field(default=None, env="REDIS_PASSWORD")
    redis_db: int = Field(default=0, env="REDIS_DB")
    redis_pool_size: int = Field(default=20, env="REDIS_POOL_SIZE")
    
    # Neo4j配置
    neo4j_host: str = Field(default="localhost", env="NEO4J_HOST")
    neo4j_port: int = Field(default=7687, env="NEO4J_PORT")
    neo4j_user: str = Field(default="neo4j", env="NEO4J_USER")
    neo4j_password: str = Field(default="password", env="NEO4J_PASSWORD")
    neo4j_max_connections: int = Field(default=50, env="NEO4J_MAX_CONNECTIONS")
    neo4j_connection_timeout: int = Field(default=30, env="NEO4J_CONNECTION_TIMEOUT")
    
    # ChromaDB配置
    chroma_host: str = Field(default="localhost", env="CHROMA_HOST")
    chroma_port: int = Field(default=8007, env="CHROMA_PORT")
    chroma_collection_name: str = Field(default="fire_rescue_knowledge", env="CHROMA_COLLECTION_NAME")
    
    # Ollama配置
    ollama_host: str = Field(default="localhost", env="OLLAMA_HOST")
    ollama_port: int = Field(default=11434, env="OLLAMA_PORT")
    ollama_model: str = Field(default="qwen2.5:7b", env="OLLAMA_MODEL")
    ollama_timeout: int = Field(default=120, env="OLLAMA_TIMEOUT")
    
    @property
    def postgres_url(self) -> str:
        return f"postgresql://{self.postgres_user}:{self.postgres_password}@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
    
    @property
    def redis_url(self) -> str:
        if self.redis_password:
            return f"redis://:{self.redis_password}@{self.redis_host}:{self.redis_port}/{self.redis_db}"
        return f"redis://{self.redis_host}:{self.redis_port}/{self.redis_db}"
    
    @property
    def neo4j_uri(self) -> str:
        return f"bolt://{self.neo4j_host}:{self.neo4j_port}"
    
    @property
    def chroma_url(self) -> str:
        return f"http://{self.chroma_host}:{self.chroma_port}"
    
    @property
    def ollama_url(self) -> str:
        return f"http://{self.ollama_host}:{self.ollama_port}"


class SecurityConfig(BaseSettings):
    """安全配置"""
    
    # JWT配置
    jwt_secret_key: str = Field(default="your-secret-key-here-change-in-production", env="JWT_SECRET_KEY")
    jwt_algorithm: str = Field(default="HS256", env="JWT_ALGORITHM")
    jwt_access_token_expire_minutes: int = Field(default=30, env="JWT_ACCESS_TOKEN_EXPIRE_MINUTES")
    jwt_refresh_token_expire_days: int = Field(default=7, env="JWT_REFRESH_TOKEN_EXPIRE_DAYS")
    
    # 密码配置
    password_min_length: int = Field(default=8, env="PASSWORD_MIN_LENGTH")
    password_require_special: bool = Field(default=True, env="PASSWORD_REQUIRE_SPECIAL")
    
    # CORS配置
    cors_origins: List[str] = Field(
        default=["http://localhost:3000", "http://127.0.0.1:3000"],
        env="CORS_ORIGINS"
    )
    cors_allow_credentials: bool = Field(default=True, env="CORS_ALLOW_CREDENTIALS")
    cors_allow_methods: List[str] = Field(default=["*"], env="CORS_ALLOW_METHODS")
    cors_allow_headers: List[str] = Field(default=["*"], env="CORS_ALLOW_HEADERS")
    
    # 安全头配置
    security_headers: Dict[str, str] = Field(
        default={
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY",
            "X-XSS-Protection": "1; mode=block"
        }
    )
    
    @validator('cors_origins', pre=True)
    def parse_cors_origins(cls, v):
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(',')]
        return v


class LoggingConfig(BaseSettings):
    """日志配置"""
    
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    log_format: str = Field(
        default="{time:YYYY-MM-DD HH:mm:ss} | {level} | {name}:{function}:{line} - {message}",
        env="LOG_FORMAT"
    )
    log_file: Optional[str] = Field(default=None, env="LOG_FILE")
    log_rotation: str = Field(default="1 day", env="LOG_ROTATION")
    log_retention: str = Field(default="30 days", env="LOG_RETENTION")
    log_compression: str = Field(default="zip", env="LOG_COMPRESSION")
    
    # 结构化日志
    structured_logging: bool = Field(default=True, env="STRUCTURED_LOGGING")
    log_json_format: bool = Field(default=False, env="LOG_JSON_FORMAT")
    
    @validator('log_level')
    def validate_log_level(cls, v):
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if v.upper() not in valid_levels:
            raise ValueError(f"日志级别必须是以下之一: {valid_levels}")
        return v.upper()


class PerformanceConfig(BaseSettings):
    """性能配置"""
    
    # 服务配置
    max_workers: int = Field(default=4, env="MAX_WORKERS")
    worker_timeout: int = Field(default=30, env="WORKER_TIMEOUT")
    
    # 缓存配置
    cache_default_ttl: int = Field(default=3600, env="CACHE_DEFAULT_TTL")
    cache_max_size: int = Field(default=1000, env="CACHE_MAX_SIZE")
    
    # 限流配置
    rate_limit_requests: int = Field(default=100, env="RATE_LIMIT_REQUESTS")
    rate_limit_window: int = Field(default=60, env="RATE_LIMIT_WINDOW")
    
    # 超时配置
    request_timeout: int = Field(default=30, env="REQUEST_TIMEOUT")
    database_timeout: int = Field(default=10, env="DATABASE_TIMEOUT")
    external_service_timeout: int = Field(default=60, env="EXTERNAL_SERVICE_TIMEOUT")
    
    # 重试配置
    max_retries: int = Field(default=3, env="MAX_RETRIES")
    retry_delay: float = Field(default=1.0, env="RETRY_DELAY")
    retry_backoff_factor: float = Field(default=2.0, env="RETRY_BACKOFF_FACTOR")


class MonitoringConfig(BaseSettings):
    """监控配置"""
    
    # Prometheus配置
    prometheus_enabled: bool = Field(default=True, env="PROMETHEUS_ENABLED")
    prometheus_port: int = Field(default=9090, env="PROMETHEUS_PORT")
    
    # 健康检查配置
    health_check_interval: int = Field(default=30, env="HEALTH_CHECK_INTERVAL")
    health_check_timeout: int = Field(default=5, env="HEALTH_CHECK_TIMEOUT")
    
    # 指标配置
    metrics_enabled: bool = Field(default=True, env="METRICS_ENABLED")
    metrics_interval: int = Field(default=60, env="METRICS_INTERVAL")
    
    # 告警配置
    alerting_enabled: bool = Field(default=False, env="ALERTING_ENABLED")
    alert_webhook_url: Optional[str] = Field(default=None, env="ALERT_WEBHOOK_URL")


class AppConfig(BaseSettings):
    """应用配置"""
    
    # 应用基本信息
    app_name: str = Field(default="Fire Emergency RAG System", env="APP_NAME")
    app_version: str = Field(default="1.0.0", env="APP_VERSION")
    app_description: str = Field(
        default="基于知识图谱和RAG技术的智能火灾应急响应系统",
        env="APP_DESCRIPTION"
    )
    
    # 环境配置
    environment: str = Field(default="development", env="ENVIRONMENT")
    debug: bool = Field(default=False, env="DEBUG")
    
    # 服务配置
    host: str = Field(default="0.0.0.0", env="HOST")
    port: int = Field(default=8000, env="PORT")
    
    # 开发配置
    reload: bool = Field(default=False, env="RELOAD")
    workers: int = Field(default=1, env="WORKERS")
    
    @validator('environment')
    def validate_environment(cls, v):
        valid_envs = ["development", "testing", "staging", "production"]
        if v not in valid_envs:
            raise ValueError(f"环境必须是以下之一: {valid_envs}")
        return v


class Config:
    """统一配置类"""
    
    def __init__(self):
        self.database = DatabaseConfig()
        self.security = SecurityConfig()
        self.logging = LoggingConfig()
        self.performance = PerformanceConfig()
        self.monitoring = MonitoringConfig()
        self.app = AppConfig()
    
    def get_database_config(self, db_name: str) -> Dict[str, Any]:
        """获取数据库配置"""
        return ServiceRegistry.get_database_config(db_name)
    
    def get_service_config(self, service_name: str) -> Dict[str, Any]:
        """获取服务配置"""
        return ServiceRegistry.get_service_config(service_name).__dict__
    
    def is_development(self) -> bool:
        """是否为开发环境"""
        return self.app.environment == "development"
    
    def is_production(self) -> bool:
        """是否为生产环境"""
        return self.app.environment == "production"
    
    def is_testing(self) -> bool:
        """是否为测试环境"""
        return self.app.environment == "testing"


# 全局配置实例
config = Config()


def get_config() -> Config:
    """获取全局配置实例"""
    return config
