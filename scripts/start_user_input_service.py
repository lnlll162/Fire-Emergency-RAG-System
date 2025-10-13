#!/usr/bin/env python3
"""
启动用户输入服务
"""

import sys
import os
import subprocess
import time
import signal
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

def start_user_input_service():
    """启动用户输入服务"""
    print("启动用户输入服务...")
    
    # 设置环境变量
    env = os.environ.copy()
    env.update({
        "USER_INPUT_SERVICE_HOST": "localhost",
        "USER_INPUT_SERVICE_PORT": "8006",
        "EMERGENCY_SERVICE_HOST": "localhost",
        "EMERGENCY_SERVICE_PORT": "8000",
        "KNOWLEDGE_GRAPH_HOST": "localhost",
        "KNOWLEDGE_GRAPH_PORT": "8001",
        "RAG_SERVICE_HOST": "localhost",
        "RAG_SERVICE_PORT": "3000",
        "OLLAMA_SERVICE_HOST": "localhost",
        "OLLAMA_SERVICE_PORT": "8003",
        "CACHE_SERVICE_HOST": "localhost",
        "CACHE_SERVICE_PORT": "8004",
        "USER_SERVICE_HOST": "localhost",
        "USER_SERVICE_PORT": "8002",
        "ADMIN_SERVICE_HOST": "localhost",
        "ADMIN_SERVICE_PORT": "8005"
    })
    
    # 启动服务
    service_path = project_root / "backend" / "services" / "user_input_service.py"
    
    try:
        process = subprocess.Popen(
            [sys.executable, str(service_path)],
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        print(f"用户输入服务已启动 (PID: {process.pid})")
        print(f"服务地址: http://localhost:8006")
        print(f"API文档: http://localhost:8006/docs")
        print("按 Ctrl+C 停止服务")
        
        # 等待进程结束
        try:
            process.wait()
        except KeyboardInterrupt:
            print("\n正在停止用户输入服务...")
            process.terminate()
            process.wait()
            print("用户输入服务已停止")
            
    except Exception as e:
        print(f"启动用户输入服务失败: {str(e)}")
        return False
    
    return True

if __name__ == "__main__":
    start_user_input_service()
