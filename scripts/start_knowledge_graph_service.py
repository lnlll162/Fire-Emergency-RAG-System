#!/usr/bin/env python3
"""
启动知识图谱服务
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
from backend.services.knowledge_graph_service import app, kg_service

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def check_dependencies():
    """检查依赖服务"""
    logger.info("检查知识图谱服务依赖...")
    
    try:
        is_healthy = await kg_service.test_connection()
        if is_healthy:
            logger.info("Neo4j数据库连接正常")
        else:
            logger.warning("Neo4j数据库连接异常，但服务将继续启动")
    except Exception as e:
        logger.error(f"依赖检查失败: {str(e)}")
        logger.warning("服务将在降级模式下启动")

def main():
    """主函数"""
    logger.info("启动知识图谱服务...")
    
    # 设置正确的环境变量
    os.environ.setdefault("OLLAMA_HOST", "localhost")
    os.environ.setdefault("OLLAMA_PORT", "11434")
    
    # 检查依赖服务
    asyncio.run(check_dependencies())
    
    # 启动服务
    host = os.getenv("KNOWLEDGE_GRAPH_SERVICE_HOST", "0.0.0.0")
    port = int(os.getenv("KNOWLEDGE_GRAPH_SERVICE_PORT", "8001"))
    
    logger.info(f"知识图谱服务启动在 http://{host}:{port}")
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
        logger.info("知识图谱服务已停止")
    except Exception as e:
        logger.error(f"知识图谱服务启动失败: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
