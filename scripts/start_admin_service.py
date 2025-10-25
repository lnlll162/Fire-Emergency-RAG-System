#!/usr/bin/env python3
"""
启动管理服务
"""

import sys
import os
import asyncio
import logging
from pathlib import Path

# 设置代理跳过localhost（解决Windows代理导致的502错误）
os.environ['NO_PROXY'] = 'localhost,127.0.0.1,::1'
os.environ['no_proxy'] = 'localhost,127.0.0.1,::1'

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

# 在导入 app 之前设置数据库与编码环境变量
os.environ.setdefault("POSTGRES_HOST", os.environ.get("POSTGRES_HOST", "127.0.0.1"))
os.environ.setdefault("POSTGRES_PORT", os.environ.get("POSTGRES_PORT", "5432"))
os.environ.setdefault("POSTGRES_DB", os.environ.get("POSTGRES_DB", "fire_emergency"))
os.environ.setdefault("POSTGRES_USER", os.environ.get("POSTGRES_USER", "postgres"))
os.environ.setdefault("POSTGRES_PASSWORD", os.environ.get("POSTGRES_PASSWORD", "password"))
os.environ.setdefault("PGCLIENTENCODING", os.environ.get("PGCLIENTENCODING", "UTF8"))
os.environ.setdefault("PGOPTIONS", os.environ.get("PGOPTIONS", "-c lc_messages=C"))

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
