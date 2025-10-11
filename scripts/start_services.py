#!/usr/bin/env python3
"""
启动已开发的服务
启动缓存服务和Ollama服务
"""

import subprocess
import time
import sys
import signal
import os
from pathlib import Path

class ServiceManager:
    """服务管理器"""
    
    def __init__(self):
        self.processes = {}
        self.services = {
            "cache_service": {
                "name": "缓存服务",
                "port": 8004,
                "script": "scripts/start_cache_service.py",
                "health_url": "http://localhost:8004/health"
            },
            "ollama_service": {
                "name": "Ollama服务", 
                "port": 8003,
                "script": "scripts/start_ollama_service.py",
                "health_url": "http://localhost:8003/health"
            }
        }
    
    def start_service(self, service_name: str) -> bool:
        """启动单个服务"""
        if service_name not in self.services:
            print(f"未知服务: {service_name}")
            return False
        
        service = self.services[service_name]
        print(f"启动 {service['name']} (端口 {service['port']})...")
        
        try:
            # 启动服务进程
            process = subprocess.Popen(
                [sys.executable, service['script']],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            self.processes[service_name] = process
            print(f"  {service['name']} 进程启动成功 (PID: {process.pid})")
            
            # 等待服务启动
            print(f"  等待 {service['name']} 启动...")
            time.sleep(5)
            
            # 检查服务是否健康
            if self.check_service_health(service_name):
                print(f"  [OK] {service['name']} 启动成功")
                return True
            else:
                print(f"  [FAIL] {service['name']} 启动失败")
                return False
                
        except Exception as e:
            print(f"  [ERROR] 启动 {service['name']} 失败: {str(e)}")
            return False
    
    def check_service_health(self, service_name: str) -> bool:
        """检查服务健康状态"""
        if service_name not in self.services:
            return False
        
        service = self.services[service_name]
        
        try:
            import requests
            response = requests.get(service['health_url'], timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def start_all_services(self) -> bool:
        """启动所有服务"""
        print("=" * 60)
        print("启动火灾应急RAG系统服务")
        print("=" * 60)
        
        success_count = 0
        total_services = len(self.services)
        
        for service_name in self.services:
            if self.start_service(service_name):
                success_count += 1
            else:
                print(f"服务 {service_name} 启动失败，停止后续服务启动")
                break
        
        print("\n" + "=" * 60)
        print(f"启动结果: {success_count}/{total_services} 个服务启动成功")
        
        if success_count == total_services:
            print("[OK] 所有服务启动成功！")
            print("\n服务访问地址:")
            for service_name, service in self.services.items():
                if service_name in self.processes:
                    print(f"  {service['name']}: http://localhost:{service['port']}")
            return True
        else:
            print("[FAIL] 部分服务启动失败！")
            return False
    
    def stop_all_services(self):
        """停止所有服务"""
        print("\n停止所有服务...")
        
        for service_name, process in self.processes.items():
            try:
                print(f"  停止 {service_name}...")
                process.terminate()
                process.wait(timeout=10)
                print(f"  [OK] {service_name} 已停止")
            except Exception as e:
                print(f"  [ERROR] 停止 {service_name} 失败: {str(e)}")
        
        self.processes.clear()
    
    def run_health_check(self):
        """运行健康检查"""
        print("\n运行健康检查...")
        
        for service_name, service in self.services.items():
            if service_name in self.processes:
                if self.check_service_health(service_name):
                    print(f"  [OK] {service['name']}: 健康")
                else:
                    print(f"  [FAIL] {service['name']}: 不健康")
            else:
                print(f"  [SKIP] {service['name']}: 未启动")

def signal_handler(signum, frame):
    """信号处理器"""
    print("\n\n接收到停止信号，正在关闭所有服务...")
    manager.stop_all_services()
    sys.exit(0)

def main():
    """主函数"""
    global manager
    manager = ServiceManager()
    
    # 注册信号处理器
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        # 启动所有服务
        if manager.start_all_services():
            print("\n[SUCCESS] 系统启动完成！")
            
            # 运行健康检查
            manager.run_health_check()
            
            print("\n使用说明:")
            print("  - 按 Ctrl+C 停止所有服务")
            print("  - 访问 http://localhost:8004 查看缓存服务")
            print("  - 访问 http://localhost:8003 查看Ollama服务")
            print("  - 访问 http://localhost:8004/docs 查看API文档")
            print("  - 访问 http://localhost:8003/docs 查看API文档")
            
            # 保持运行
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                pass
        else:
            print("\n[FAIL] 系统启动失败！")
    
    except KeyboardInterrupt:
        pass
    finally:
        manager.stop_all_services()

if __name__ == "__main__":
    main()
