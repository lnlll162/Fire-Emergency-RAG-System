#!/usr/bin/env python3
"""
启动用户服务
"""

import sys
import os
import subprocess
import time
import signal
from pathlib import Path

# 设置代理跳过localhost（解决Windows代理导致的502错误）
os.environ['NO_PROXY'] = 'localhost,127.0.0.1,::1'
os.environ['no_proxy'] = 'localhost,127.0.0.1,::1'

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

def start_user_service():
    """启动用户服务"""
    print("启动用户服务...")
    
    # 设置环境变量
    env = os.environ.copy()
    env.update({
        "USER_SERVICE_HOST": "localhost",
        "USER_SERVICE_PORT": "8002",
        "REDIS_HOST": "localhost",
        "REDIS_PORT": "6379",
        # 数据库连接（与 docker-compose 保持一致；本地直连则指向 127.0.0.1:5432）
        "POSTGRES_HOST": env.get("POSTGRES_HOST", "127.0.0.1"),
        "POSTGRES_PORT": env.get("POSTGRES_PORT", "5432"),
        "POSTGRES_DB": env.get("POSTGRES_DB", "fire_emergency"),
        "POSTGRES_USER": env.get("POSTGRES_USER", "postgres"),
        "POSTGRES_PASSWORD": env.get("POSTGRES_PASSWORD", "password"),
        # 编码/消息设置，规避 Windows 区域设置导致的解码问题
        "PGCLIENTENCODING": env.get("PGCLIENTENCODING", "UTF8"),
        "PGOPTIONS": env.get("PGOPTIONS", "-c lc_messages=C"),
        "JWT_SECRET_KEY": "your-secret-key-here-change-in-production",
        "JWT_ALGORITHM": "HS256",
        "JWT_ACCESS_TOKEN_EXPIRE_MINUTES": "30",
        "JWT_REFRESH_TOKEN_EXPIRE_DAYS": "7"
    })
    
    # 启动服务
    service_path = project_root / "backend" / "services" / "user_service.py"
    
    try:
        process = subprocess.Popen(
            [sys.executable, str(service_path)],
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        print(f"用户服务已启动 (PID: {process.pid})")
        print(f"服务地址: http://localhost:8002")
        print(f"API文档: http://localhost:8002/docs")
        print("按 Ctrl+C 停止服务")
        
        # 等待进程结束
        try:
            process.wait()
        except KeyboardInterrupt:
            print("\n正在停止用户服务...")
            process.terminate()
            process.wait()
            print("用户服务已停止")
            
    except Exception as e:
        print(f"启动用户服务失败: {str(e)}")
        return False
    
    return True

if __name__ == "__main__":
    start_user_service()
