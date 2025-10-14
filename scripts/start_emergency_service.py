#!/usr/bin/env python3
"""
启动应急服务
"""

import asyncio
import logging
import sys
import os
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

import uvicorn
from backend.services.emergency_service import app, emergency_service

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def check_dependencies():
    """检查依赖服务"""
    logger.info("检查依赖服务...")
    
    try:
        health = await emergency_service.check_health()
        logger.info(f"依赖服务检查完成: {health.overall_status}")
        logger.info(f"健康服务: {health.healthy_services}/{health.total_services}")
        
        for service in health.services:
            status = "[OK]" if service.status == "healthy" else "[ERROR]"
            logger.info(f"  {status} {service.service_name}: {service.status} ({service.response_time:.1f}ms)")
        
        if health.overall_status == "unhealthy":
            logger.warning("部分必需服务不可用，系统将使用降级模式")
        elif health.overall_status == "degraded":
            logger.warning("部分可选服务不可用，但核心功能正常")
        else:
            logger.info("所有服务正常")
            
    except Exception as e:
        logger.error(f"依赖服务检查失败: {str(e)}")
        logger.warning("系统将使用降级模式运行")

def main():
    """主函数"""
    logger.info("启动应急服务...")
    
    # 设置正确的环境变量
    os.environ.setdefault("OLLAMA_HOST", "localhost")
    os.environ.setdefault("OLLAMA_PORT", "11434")
    
    # 检查依赖服务
    asyncio.run(check_dependencies())
    
    # 启动服务
    host = os.getenv("EMERGENCY_SERVICE_HOST", "0.0.0.0")
    port = int(os.getenv("EMERGENCY_SERVICE_PORT", "8000"))
    
    logger.info(f"应急服务启动在 http://{host}:{port}")
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
        logger.info("应急服务已停止")
    except Exception as e:
        logger.error(f"应急服务启动失败: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
