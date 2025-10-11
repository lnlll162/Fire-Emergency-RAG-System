#!/usr/bin/env python3
"""
启动Ollama后端服务
确保模型存储到指定目录而不是C盘
"""

import os
import sys
import subprocess
import logging
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def setup_environment():
    """设置环境变量"""
    # 设置Ollama模型存储路径（避免C盘）
    models_dir = project_root / "models"
    models_dir.mkdir(exist_ok=True)
    
    os.environ["OLLAMA_MODELS"] = str(models_dir)
    os.environ["OLLAMA_HOST"] = "0.0.0.0"
    os.environ["OLLAMA_PORT"] = "11434"
    
    logger.info(f"设置Ollama模型存储路径: {models_dir}")
    logger.info(f"设置Ollama主机: 0.0.0.0:11434")

def start_ollama():
    """启动Ollama服务"""
    try:
        logger.info("启动Ollama后端服务...")
        
        # 设置环境变量
        setup_environment()
        
        # 启动Ollama服务
        cmd = ["ollama", "serve"]
        
        logger.info(f"执行命令: {' '.join(cmd)}")
        logger.info("Ollama服务启动中...")
        logger.info("按 Ctrl+C 停止服务")
        
        # 启动服务
        subprocess.run(cmd, check=True)
        
    except KeyboardInterrupt:
        logger.info("Ollama服务已停止")
    except subprocess.CalledProcessError as e:
        logger.error(f"启动Ollama服务失败: {e}")
        logger.error("请确保已安装Ollama: https://ollama.ai/download")
    except FileNotFoundError:
        logger.error("未找到ollama命令")
        logger.error("请安装Ollama: https://ollama.ai/download")
    except Exception as e:
        logger.error(f"启动Ollama服务时出错: {e}")

if __name__ == "__main__":
    start_ollama()
