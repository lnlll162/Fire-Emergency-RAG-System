#!/usr/bin/env python3
"""
启动管理服务
"""

import sys
import os
import asyncio
import logging
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from backend.services.admin_service import app
import uvicorn

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    """启动管理服务"""
    try:
        logger.info("正在启动管理服务...")
        
        # 启动服务
        uvicorn.run(
            app,
            host="0.0.0.0",
            port=8005,
            log_level="info",
            access_log=True
        )
    except KeyboardInterrupt:
        logger.info("管理服务已停止")
    except Exception as e:
        logger.error(f"启动管理服务失败: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
