"""
火灾应急救援RAG系统 - 服务注册中心
统一管理所有服务的配置和发现
"""

import os
from typing import Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class ServiceConfig:
    """服务配置类"""
    host: str
    port: int
    base_url: str
    health_check_url: str


class ServiceRegistry:
    """服务注册中心"""
    
    # 服务端口配置
    SERVICES = {
        "emergency_service": {
            "host": os.getenv("EMERGENCY_SERVICE_HOST", "localhost"),
            "port": int(os.getenv("EMERGENCY_SERVICE_PORT", "8000")),
            "base_url": f"http://{os.getenv('EMERGENCY_SERVICE_HOST', 'localhost')}:{os.getenv('EMERGENCY_SERVICE_PORT', '8000')}",
            "health_check_url": f"http://{os.getenv('EMERGENCY_SERVICE_HOST', 'localhost')}:{os.getenv('EMERGENCY_SERVICE_PORT', '8000')}/health"
        },
        "knowledge_graph": {
            "host": os.getenv("KNOWLEDGE_GRAPH_HOST", "localhost"),
            "port": int(os.getenv("KNOWLEDGE_GRAPH_PORT", "8001")),
            "base_url": f"http://{os.getenv('KNOWLEDGE_GRAPH_HOST', 'localhost')}:{os.getenv('KNOWLEDGE_GRAPH_PORT', '8001')}",
            "health_check_url": f"http://{os.getenv('KNOWLEDGE_GRAPH_HOST', 'localhost')}:{os.getenv('KNOWLEDGE_GRAPH_PORT', '8001')}/health"
        },
        "rag_service": {
            "host": os.getenv("RAG_SERVICE_HOST", "localhost"),
            "port": int(os.getenv("RAG_SERVICE_PORT", "3000")),
            "base_url": f"http://{os.getenv('RAG_SERVICE_HOST', 'localhost')}:{os.getenv('RAG_SERVICE_PORT', '3000')}",
            "health_check_url": f"http://{os.getenv('RAG_SERVICE_HOST', 'localhost')}:{os.getenv('RAG_SERVICE_PORT', '3000')}/health"
        },
        "ollama_service": {
            "host": os.getenv("OLLAMA_SERVICE_HOST", "localhost"),
            "port": int(os.getenv("OLLAMA_SERVICE_PORT", "8003")),
            "base_url": f"http://{os.getenv('OLLAMA_SERVICE_HOST', 'localhost')}:{os.getenv('OLLAMA_SERVICE_PORT', '8003')}",
            "health_check_url": f"http://{os.getenv('OLLAMA_SERVICE_HOST', 'localhost')}:{os.getenv('OLLAMA_SERVICE_PORT', '8003')}/health"
        },
        "cache_service": {
            "host": os.getenv("CACHE_SERVICE_HOST", "localhost"),
            "port": int(os.getenv("CACHE_SERVICE_PORT", "8004")),
            "base_url": f"http://{os.getenv('CACHE_SERVICE_HOST', 'localhost')}:{os.getenv('CACHE_SERVICE_PORT', '8004')}",
            "health_check_url": f"http://{os.getenv('CACHE_SERVICE_HOST', 'localhost')}:{os.getenv('CACHE_SERVICE_PORT', '8004')}/health"
        },
        "admin_service": {
            "host": os.getenv("ADMIN_SERVICE_HOST", "localhost"),
            "port": int(os.getenv("ADMIN_SERVICE_PORT", "8005")),
            "base_url": f"http://{os.getenv('ADMIN_SERVICE_HOST', 'localhost')}:{os.getenv('ADMIN_SERVICE_PORT', '8005')}",
            "health_check_url": f"http://{os.getenv('ADMIN_SERVICE_HOST', 'localhost')}:{os.getenv('ADMIN_SERVICE_PORT', '8005')}/health"
        },
        "user_service": {
            "host": os.getenv("USER_SERVICE_HOST", "localhost"),
            "port": int(os.getenv("USER_SERVICE_PORT", "8002")),
            "base_url": f"http://{os.getenv('USER_SERVICE_HOST', 'localhost')}:{os.getenv('USER_SERVICE_PORT', '8002')}",
            "health_check_url": f"http://{os.getenv('USER_SERVICE_HOST', 'localhost')}:{os.getenv('USER_SERVICE_PORT', '8002')}/health"
        },
        "admin_service": {
            "host": os.getenv("ADMIN_SERVICE_HOST", "localhost"),
            "port": int(os.getenv("ADMIN_SERVICE_PORT", "8005")),
            "base_url": f"http://{os.getenv('ADMIN_SERVICE_HOST', 'localhost')}:{os.getenv('ADMIN_SERVICE_PORT', '8005')}",
            "health_check_url": f"http://{os.getenv('ADMIN_SERVICE_HOST', 'localhost')}:{os.getenv('ADMIN_SERVICE_PORT', '8005')}/health"
        },
        "user_input_service": {
            "host": os.getenv("USER_INPUT_SERVICE_HOST", "localhost"),
            "port": int(os.getenv("USER_INPUT_SERVICE_PORT", "8006")),
            "base_url": f"http://{os.getenv('USER_INPUT_SERVICE_HOST', 'localhost')}:{os.getenv('USER_INPUT_SERVICE_PORT', '8006')}",
            "health_check_url": f"http://{os.getenv('USER_INPUT_SERVICE_HOST', 'localhost')}:{os.getenv('USER_INPUT_SERVICE_PORT', '8006')}/health"
        }
    }
    
    # 数据库配置
    DATABASES = {
        "postgresql": {
            "host": os.getenv("POSTGRES_HOST", "localhost"),
            "port": int(os.getenv("POSTGRES_PORT", "5432")),
            "database": os.getenv("POSTGRES_DB", "fire_emergency"),
            "username": os.getenv("POSTGRES_USER", "postgres"),
            "password": os.getenv("POSTGRES_PASSWORD", "password"),
            "url": f"postgresql://{os.getenv('POSTGRES_USER', 'postgres')}:{os.getenv('POSTGRES_PASSWORD', 'password')}@{os.getenv('POSTGRES_HOST', 'localhost')}:{os.getenv('POSTGRES_PORT', '5432')}/{os.getenv('POSTGRES_DB', 'fire_emergency')}"
        },
        "redis": {
            "host": os.getenv("REDIS_HOST", "localhost"),
            "port": int(os.getenv("REDIS_PORT", "6379")),
            "password": os.getenv("REDIS_PASSWORD"),
            "db": int(os.getenv("REDIS_DB", "0")),
            "url": f"redis://{os.getenv('REDIS_HOST', 'localhost')}:{os.getenv('REDIS_PORT', '6379')}/{os.getenv('REDIS_DB', '0')}"
        },
        "neo4j": {
            "host": os.getenv("NEO4J_HOST", "localhost"),
            "port": int(os.getenv("NEO4J_PORT", "7687")),
            "username": os.getenv("NEO4J_USER", "neo4j"),
            "password": os.getenv("NEO4J_PASSWORD", "password"),
            "uri": f"bolt://{os.getenv('NEO4J_HOST', 'localhost')}:{os.getenv('NEO4J_PORT', '7687')}"
        },
        "chromadb": {
            "host": os.getenv("CHROMA_HOST", "localhost"),
            "port": int(os.getenv("CHROMA_PORT", "8007")),
            "url": f"http://{os.getenv('CHROMA_HOST', 'localhost')}:{os.getenv('CHROMA_PORT', '8007')}"
        },
        "ollama": {
            "host": os.getenv("OLLAMA_HOST", "localhost"),
            "port": int(os.getenv("OLLAMA_PORT", "11434")),
            "url": f"http://{os.getenv('OLLAMA_HOST', 'localhost')}:{os.getenv('OLLAMA_PORT', '11434')}"
        }
    }
    
    @classmethod
    def get_service_config(cls, service_name: str) -> ServiceConfig:
        """获取服务配置"""
        if service_name not in cls.SERVICES:
            raise ValueError(f"服务 {service_name} 不存在")
        
        config = cls.SERVICES[service_name]
        return ServiceConfig(
            host=config["host"],
            port=config["port"],
            base_url=config["base_url"],
            health_check_url=config["health_check_url"]
        )
    
    @classmethod
    def get_service_url(cls, service_name: str) -> str:
        """获取服务URL"""
        config = cls.get_service_config(service_name)
        return config.base_url
    
    @classmethod
    def get_health_check_url(cls, service_name: str) -> str:
        """获取健康检查URL"""
        config = cls.get_service_config(service_name)
        return config.health_check_url
    
    @classmethod
    def get_database_config(cls, db_name: str) -> Dict[str, Any]:
        """获取数据库配置"""
        if db_name not in cls.DATABASES:
            raise ValueError(f"数据库 {db_name} 不存在")
        return cls.DATABASES[db_name]
    
    @classmethod
    def get_database_url(cls, db_name: str) -> str:
        """获取数据库连接URL"""
        config = cls.get_database_config(db_name)
        return config["url"]
    
    @classmethod
    def list_services(cls) -> list:
        """列出所有服务"""
        return list(cls.SERVICES.keys())
    
    @classmethod
    def list_databases(cls) -> list:
        """列出所有数据库"""
        return list(cls.DATABASES.keys())
    
    @classmethod
    def is_service_configured(cls, service_name: str) -> bool:
        """检查服务是否已配置"""
        return service_name in cls.SERVICES
    
    @classmethod
    def is_database_configured(cls, db_name: str) -> bool:
        """检查数据库是否已配置"""
        return db_name in cls.DATABASES
