#!/usr/bin/env python3
"""
启动缓存服务脚本
"""

import asyncio
import logging
import sys
import os
from pathlib import Path

# 设置代理跳过localhost（解决Windows代理导致的502错误）
os.environ['NO_PROXY'] = 'localhost,127.0.0.1,::1'
os.environ['no_proxy'] = 'localhost,127.0.0.1,::1'

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

import uvicorn
from backend.services.cache_service import app, get_cache_service_instance

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def check_dependencies():
    """检查依赖服务"""
    logger.info("检查缓存服务依赖...")
    
    try:
        cache_service = get_cache_service_instance()
        is_healthy = await cache_service.test_connection()
        if is_healthy:
            logger.info("Redis连接正常")
        else:
            logger.warning("Redis连接异常，但服务将继续启动")
    except Exception as e:
        logger.error(f"依赖检查失败: {str(e)}")
        logger.warning("服务将在降级模式下启动")

def main():
    """主函数"""
    logger.info("启动缓存服务...")
    
    # 设置正确的环境变量
    os.environ.setdefault("OLLAMA_HOST", "localhost")
    os.environ.setdefault("OLLAMA_PORT", "11434")
    
    # 检查依赖服务
    asyncio.run(check_dependencies())
    
    # 启动服务
    host = os.getenv("CACHE_SERVICE_HOST", "0.0.0.0")
    port = int(os.getenv("CACHE_SERVICE_PORT", "8004"))
    
    logger.info(f"缓存服务启动在 http://{host}:{port}")
    logger.info(f"API文档: http://{host}:{port}/docs")
    logger.info(f"健康检查: http://{host}:{port}/health")
    
    try:
        uvicorn.run(
            app,
            host=host,
            port=port,
            log_level="info",
            access_log=True
        )
    except KeyboardInterrupt:
        logger.info("缓存服务已停止")
    except Exception as e:
        logger.error(f"缓存服务启动失败: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
