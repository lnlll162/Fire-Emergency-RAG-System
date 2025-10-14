#!/usr/bin/env python3
"""
快速启动脚本 - 开发环境使用
只启动核心服务，跳过可选服务
"""

import os
import sys
import time
import subprocess
import requests
from pathlib import Path

def check_service_health(url: str, timeout: int = 5) -> bool:
    """检查服务健康状态"""
    try:
        response = requests.get(url, timeout=timeout)
        return response.status_code == 200
    except:
        return False

def start_service(service_name: str, script_name: str, health_url: str = None) -> bool:
    """启动单个服务"""
    project_root = Path(__file__).parent.parent
    script_path = project_root / "scripts" / script_name
    
    if not script_path.exists():
        print(f"[ERROR] 启动脚本不存在: {script_name}")
        return False
    
    print(f"[START] 启动 {service_name}...")
    
    try:
        process = subprocess.Popen(
            [sys.executable, str(script_path)],
            cwd=str(project_root),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            encoding='utf-8',
            errors='ignore'
        )
        
        # 等待服务启动
        if health_url:
            for i in range(15):  # 等待15秒
                time.sleep(1)
                if check_service_health(health_url):
                    print(f"[OK] {service_name} 启动成功")
                    return True
            print(f"[WARNING] {service_name} 启动可能有问题，但继续...")
        else:
            time.sleep(3)
            print(f"[OK] {service_name} 启动完成")
        
        return True
        
    except Exception as e:
        print(f"[ERROR] 启动 {service_name} 失败: {e}")
        return False

def main():
    """快速启动核心服务"""
    print("火灾应急救援RAG系统 - 快速启动")
    print("=" * 40)
    sys.stdout.flush()
    
    # 检查Docker是否运行
    print("检查Docker状态...")
    sys.stdout.flush()
    try:
        result = subprocess.run(['docker', 'ps'], capture_output=True, text=True, encoding='utf-8', errors='ignore')
        if result.returncode != 0:
            print("[ERROR] Docker未运行，请先启动Docker Desktop")
            return False
        print("[OK] Docker运行正常")
    except Exception as e:
        print(f"[ERROR] 未找到Docker: {e}")
        return False
    
    # 启动数据库服务
    print("\n启动数据库服务...")
    sys.stdout.flush()
    docker_cmd = [
        "docker-compose", "-f", "infrastructure/docker/docker-compose.yml",
        "up", "-d", "postgres", "redis", "neo4j", "chromadb", "ollama"
    ]
    
    try:
        result = subprocess.run(docker_cmd, cwd=Path(__file__).parent.parent, encoding='utf-8', errors='ignore')
        if result.returncode == 0:
            print("[OK] 数据库服务启动成功")
        else:
            print("[WARNING] 数据库服务启动可能有问题")
    except Exception as e:
        print(f"[ERROR] 数据库服务启动失败: {e}")
        return False
    
    # 等待数据库服务启动
    print("等待数据库服务启动...")
    sys.stdout.flush()
    time.sleep(10)
    
    # 启动核心应用服务
    services = [
        ("知识图谱服务", "start_knowledge_graph_service.py", "http://localhost:8001/health"),
        ("Ollama服务", "start_ollama_service.py", "http://localhost:8003/health"),
        ("缓存服务", "start_cache_service.py", "http://localhost:8004/health"),
        ("RAG服务", "start_rag_service.py", "http://localhost:3000/health"),
        ("应急服务", "start_emergency_service.py", "http://localhost:8000/health")
    ]
    
    print("\n启动应用服务...")
    sys.stdout.flush()
    success_count = 0
    
    for service_name, script_name, health_url in services:
        if start_service(service_name, script_name, health_url):
            success_count += 1
        time.sleep(2)  # 服务间启动间隔
    
    print(f"\n启动完成: {success_count}/{len(services)} 个服务成功启动")
    sys.stdout.flush()
    
    # 检查系统状态
    print("\n检查系统状态...")
    sys.stdout.flush()
    emergency_healthy = check_service_health("http://localhost:8000/health")
    
    if emergency_healthy:
        print("[SUCCESS] 系统启动成功！")
        print("应急服务: http://localhost:8000")
        print("API文档: http://localhost:8000/docs")
        print("\n按 Ctrl+C 退出")
        
        try:
            while True:
                time.sleep(10)
        except KeyboardInterrupt:
            print("\n正在退出...")
    else:
        print("[ERROR] 系统启动失败，请检查日志")
        return False
    
    return True

if __name__ == "__main__":
    main()
