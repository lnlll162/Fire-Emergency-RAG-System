#!/usr/bin/env python3
"""
服务管理脚本
用于启动、停止、重启单个服务
"""

import os
import sys
import time
import signal
import subprocess
import requests
import argparse
from pathlib import Path
from typing import Dict, Optional

class ServiceManager:
    """服务管理器"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.services = {
            "knowledge_graph": {
                "script": "start_knowledge_graph_service.py",
                "port": 8001,
                "health_url": "http://localhost:8001/health",
                "description": "知识图谱服务"
            },
            "ollama": {
                "script": "start_ollama_service.py", 
                "port": 8003,
                "health_url": "http://localhost:8003/health",
                "description": "Ollama服务"
            },
            "cache": {
                "script": "start_cache_service.py",
                "port": 8004,
                "health_url": "http://localhost:8004/health", 
                "description": "缓存服务"
            },
            "rag": {
                "script": "start_rag_service.py",
                "port": 3000,
                "health_url": "http://localhost:3000/health",
                "description": "RAG服务"
            },
            "emergency": {
                "script": "start_emergency_service.py",
                "port": 8000,
                "health_url": "http://localhost:8000/health",
                "description": "应急服务"
            }
        }
        self.running_processes: Dict[str, subprocess.Popen] = {}
    
    def check_port_available(self, port: int) -> bool:
        """检查端口是否可用"""
        try:
            import socket
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(1)
                result = s.connect_ex(('localhost', port))
                return result != 0
        except:
            return False
    
    def kill_process_on_port(self, port: int) -> bool:
        """终止占用端口的进程"""
        try:
            if os.name == 'nt':  # Windows
                result = subprocess.run(
                    f'netstat -ano | findstr :{port}',
                    shell=True, capture_output=True, text=True
                )
                if result.stdout:
                    lines = result.stdout.strip().split('\n')
                    for line in lines:
                        if f':{port}' in line and 'LISTENING' in line:
                            parts = line.split()
                            if len(parts) >= 5:
                                pid = parts[-1]
                                subprocess.run(f'taskkill /PID {pid} /F', shell=True)
                                print(f"已终止端口 {port} 上的进程 {pid}")
                                return True
            else:  # Linux/Mac
                result = subprocess.run(
                    f'lsof -ti:{port}',
                    shell=True, capture_output=True, text=True
                )
                if result.stdout.strip():
                    pids = result.stdout.strip().split('\n')
                    for pid in pids:
                        subprocess.run(f'kill -9 {pid}', shell=True)
                        print(f"已终止端口 {port} 上的进程 {pid}")
                    return True
        except Exception as e:
            print(f"终止端口 {port} 上的进程时出错: {e}")
        return False
    
    def start_service(self, service_name: str) -> bool:
        """启动服务"""
        if service_name not in self.services:
            print(f"[ERROR] 未知服务: {service_name}")
            return False
        
        service_config = self.services[service_name]
        script_path = self.project_root / "scripts" / service_config["script"]
        
        if not script_path.exists():
            print(f"[ERROR] 启动脚本不存在: {script_path}")
            return False
        
        # 检查端口
        port = service_config["port"]
        if not self.check_port_available(port):
            print(f"[WARNING] 端口 {port} 被占用，尝试释放...")
            self.kill_process_on_port(port)
            time.sleep(2)
        
        try:
            print(f"[START] 启动 {service_config['description']}...")
            process = subprocess.Popen(
                [sys.executable, str(script_path)],
                cwd=str(self.project_root),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            self.running_processes[service_name] = process
            
            # 等待服务启动
            print("等待服务启动...")
            for i in range(15):
                time.sleep(1)
                try:
                    response = requests.get(service_config["health_url"], timeout=2)
                    if response.status_code == 200:
                        print(f"[OK] {service_config['description']} 启动成功")
                        return True
                except:
                    pass
            
            print(f"[WARNING] {service_config['description']} 启动可能有问题")
            return False
            
        except Exception as e:
            print(f"[ERROR] 启动 {service_config['description']} 失败: {e}")
            return False
    
    def stop_service(self, service_name: str) -> bool:
        """停止服务"""
        if service_name not in self.running_processes:
            print(f"[WARNING] 服务 {service_name} 未在运行")
            return True
        
        try:
            process = self.running_processes[service_name]
            process.terminate()
            process.wait(timeout=5)
            del self.running_processes[service_name]
            print(f"[OK] 服务 {service_name} 已停止")
            return True
        except subprocess.TimeoutExpired:
            process.kill()
            del self.running_processes[service_name]
            print(f"[WARNING] 强制停止服务 {service_name}")
            return True
        except Exception as e:
            print(f"[ERROR] 停止服务 {service_name} 失败: {e}")
            return False
    
    def restart_service(self, service_name: str) -> bool:
        """重启服务"""
        print(f"🔄 重启服务 {service_name}...")
        self.stop_service(service_name)
        time.sleep(2)
        return self.start_service(service_name)
    
    def status_service(self, service_name: str) -> bool:
        """检查服务状态"""
        if service_name not in self.services:
            print(f"[ERROR] 未知服务: {service_name}")
            return False
        
        service_config = self.services[service_name]
        
        try:
            response = requests.get(service_config["health_url"], timeout=5)
            if response.status_code == 200:
                print(f"[OK] {service_config['description']} 运行正常")
                return True
            else:
                print(f"[ERROR] {service_config['description']} 状态异常")
                return False
        except:
            print(f"[ERROR] {service_config['description']} 无法连接")
            return False
    
    def list_services(self):
        """列出所有服务"""
        print("可用服务:")
        print("-" * 50)
        for name, config in self.services.items():
            status = "运行中" if name in self.running_processes else "未运行"
            print(f"{name:15} | {config['description']:15} | {status}")
    
    def cleanup(self):
        """清理所有服务"""
        print("清理所有服务...")
        for service_name in list(self.running_processes.keys()):
            self.stop_service(service_name)

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="服务管理脚本")
    parser.add_argument("action", choices=["start", "stop", "restart", "status", "list"], 
                       help="操作类型")
    parser.add_argument("service", nargs="?", help="服务名称")
    
    args = parser.parse_args()
    
    manager = ServiceManager()
    
    try:
        if args.action == "list":
            manager.list_services()
        elif args.action == "start":
            if not args.service:
                print("[ERROR] 请指定服务名称")
                sys.exit(1)
            success = manager.start_service(args.service)
            if success:
                print("按 Ctrl+C 停止服务")
                try:
                    while True:
                        time.sleep(1)
                except KeyboardInterrupt:
                    print("\n正在停止服务...")
                    manager.stop_service(args.service)
        elif args.action == "stop":
            if not args.service:
                print("[ERROR] 请指定服务名称")
                sys.exit(1)
            manager.stop_service(args.service)
        elif args.action == "restart":
            if not args.service:
                print("[ERROR] 请指定服务名称")
                sys.exit(1)
            manager.restart_service(args.service)
        elif args.action == "status":
            if not args.service:
                print("[ERROR] 请指定服务名称")
                sys.exit(1)
            manager.status_service(args.service)
    
    except KeyboardInterrupt:
        print("\n正在清理...")
        manager.cleanup()
    except Exception as e:
        print(f"[ERROR] 操作失败: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
