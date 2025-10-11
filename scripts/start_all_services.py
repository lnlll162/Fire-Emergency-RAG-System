#!/usr/bin/env python3
"""
启动所有服务脚本
按正确顺序启动整个火灾应急RAG系统的所有服务
"""

import subprocess
import time
import sys
import os
import signal
from pathlib import Path
from typing import List, Dict
import psutil

class ServiceManager:
    """服务管理器"""
    
    def __init__(self):
        self.services = {
            "redis": {
                "name": "Redis",
                "port": 6379,
                "command": ["docker", "run", "-d", "--name", "fire_emergency_redis", 
                           "-p", "6379:6379", "redis:7-alpine"],
                "health_check": "redis-cli ping",
                "startup_time": 5
            },
            "postgres": {
                "name": "PostgreSQL", 
                "port": 5432,
                "command": ["docker", "run", "-d", "--name", "fire_emergency_postgres",
                           "-e", "POSTGRES_DB=fire_emergency",
                           "-e", "POSTGRES_USER=postgres", 
                           "-e", "POSTGRES_PASSWORD=password",
                           "-p", "5432:5432", "postgres:15-alpine"],
                "health_check": "pg_isready -h localhost -p 5432",
                "startup_time": 10
            },
            "neo4j": {
                "name": "Neo4j",
                "port": 7474,
                "command": ["docker", "run", "-d", "--name", "fire_emergency_neo4j",
                           "-e", "NEO4J_AUTH=neo4j/password",
                           "-p", "7474:7474", "-p", "7687:7687", "neo4j:5-community"],
                "health_check": "curl -f http://localhost:7474",
                "startup_time": 15
            },
            "chromadb": {
                "name": "ChromaDB",
                "port": 8001,
                "command": ["docker", "run", "-d", "--name", "fire_emergency_chromadb",
                           "-p", "8001:8000", "chromadb/chroma:latest"],
                "health_check": "curl -f http://localhost:8001/api/v1/heartbeat",
                "startup_time": 10
            },
            "ollama": {
                "name": "Ollama",
                "port": 11434,
                "command": ["docker", "run", "-d", "--name", "fire_emergency_ollama",
                           "-p", "11434:11434", "-v", "ollama_data:/root/.ollama",
                           "ollama/ollama:latest"],
                "health_check": "curl -f http://localhost:11434/api/tags",
                "startup_time": 20
            },
            "cache_service": {
                "name": "缓存服务",
                "port": 8004,
                "command": ["python", "scripts/start_cache_service.py"],
                "health_check": "curl -f http://localhost:8004/health",
                "startup_time": 5,
                "depends_on": ["redis"]
            },
            "ollama_service": {
                "name": "Ollama服务",
                "port": 8003,
                "command": ["python", "scripts/start_ollama_service.py"],
                "health_check": "curl -f http://localhost:8003/health",
                "startup_time": 5,
                "depends_on": ["ollama", "redis"]
            },
            "rag_service": {
                "name": "RAG服务",
                "port": 8005,
                "command": ["python", "scripts/start_rag_service.py"],
                "health_check": "curl -f http://localhost:8005/health",
                "startup_time": 10,
                "depends_on": ["chromadb", "redis"]
            },
            "knowledge_graph_service": {
                "name": "知识图谱服务",
                "port": 8006,
                "command": ["python", "scripts/start_knowledge_graph_service.py"],
                "health_check": "curl -f http://localhost:8006/health",
                "startup_time": 5,
                "depends_on": ["neo4j", "redis"]
            },
            "emergency_service": {
                "name": "应急服务",
                "port": 8000,
                "command": ["python", "scripts/start_emergency_service.py"],
                "health_check": "curl -f http://localhost:8000/health",
                "startup_time": 5,
                "depends_on": ["cache_service", "ollama_service", "rag_service", "knowledge_graph_service"]
            },
            "user_service": {
                "name": "用户服务",
                "port": 8001,
                "command": ["python", "scripts/start_user_service.py"],
                "health_check": "curl -f http://localhost:8001/health",
                "startup_time": 5,
                "depends_on": ["postgres", "redis"]
            },
            "admin_service": {
                "name": "管理服务",
                "port": 8002,
                "command": ["python", "scripts/start_admin_service.py"],
                "health_check": "curl -f http://localhost:8002/health",
                "startup_time": 5,
                "depends_on": ["postgres", "redis"]
            }
        }
        
        self.running_processes = {}
        self.startup_order = [
            "redis", "postgres", "neo4j", "chromadb", "ollama",
            "cache_service", "ollama_service", "rag_service", "knowledge_graph_service",
            "emergency_service", "user_service", "admin_service"
        ]
    
    def check_port_available(self, port: int) -> bool:
        """检查端口是否可用"""
        for conn in psutil.net_connections():
            if conn.laddr.port == port:
                return False
        return True
    
    def wait_for_service(self, service_name: str, max_wait: int = 60) -> bool:
        """等待服务启动"""
        service = self.services[service_name]
        print(f"  等待 {service['name']} 启动...")
        
        start_time = time.time()
        while time.time() - start_time < max_wait:
            try:
                if service_name in ["redis", "postgres", "neo4j", "chromadb", "ollama"]:
                    # Docker服务健康检查
                    result = subprocess.run(
                        service["health_check"].split(),
                        capture_output=True,
                        text=True,
                        timeout=5
                    )
                    if result.returncode == 0:
                        print(f"  ✅ {service['name']} 启动成功")
                        return True
                else:
                    # Python服务健康检查
                    result = subprocess.run(
                        ["curl", "-f", "-s", f"http://localhost:{service['port']}/health"],
                        capture_output=True,
                        text=True,
                        timeout=5
                    )
                    if result.returncode == 0:
                        print(f"  ✅ {service['name']} 启动成功")
                        return True
            except Exception as e:
                pass
            
            time.sleep(2)
        
        print(f"  ❌ {service['name']} 启动超时")
        return False
    
    def start_service(self, service_name: str) -> bool:
        """启动单个服务"""
        service = self.services[service_name]
        
        print(f"🚀 启动 {service['name']}...")
        
        # 检查端口是否被占用
        if not self.check_port_available(service["port"]):
            print(f"  ⚠️  端口 {service['port']} 已被占用，跳过启动")
            return True
        
        try:
            if service_name in ["redis", "postgres", "neo4j", "chromadb", "ollama"]:
                # 启动Docker服务
                result = subprocess.run(
                    service["command"],
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                if result.returncode == 0:
                    print(f"  ✅ {service['name']} Docker容器启动成功")
                    return self.wait_for_service(service_name)
                else:
                    print(f"  ❌ {service['name']} Docker容器启动失败: {result.stderr}")
                    return False
            else:
                # 启动Python服务
                process = subprocess.Popen(
                    service["command"],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
                self.running_processes[service_name] = process
                print(f"  ✅ {service['name']} 进程启动成功 (PID: {process.pid})")
                return self.wait_for_service(service_name)
        
        except Exception as e:
            print(f"  ❌ {service['name']} 启动失败: {str(e)}")
            return False
    
    def start_all_services(self) -> bool:
        """启动所有服务"""
        print("开始启动火灾应急RAG系统...")
        print("=" * 60)
        
        success_count = 0
        total_services = len(self.startup_order)
        
        for service_name in self.startup_order:
            # 检查依赖
            service = self.services[service_name]
            if "depends_on" in service:
                for dep in service["depends_on"]:
                    if dep not in self.running_processes and dep not in ["redis", "postgres", "neo4j", "chromadb", "ollama"]:
                        print(f"  ⚠️  {service['name']} 的依赖 {dep} 未启动，跳过")
                        continue
            
            if self.start_service(service_name):
                success_count += 1
            else:
                print(f"  ❌ {service['name']} 启动失败，停止后续服务启动")
                break
        
        print("\n" + "=" * 60)
        print(f"📊 启动结果: {success_count}/{total_services} 个服务启动成功")
        
        if success_count == total_services:
            print("✅ 所有服务启动成功！")
            print("\n🌐 服务访问地址:")
            for service_name, service in self.services.items():
                if service_name in self.running_processes or service_name in ["redis", "postgres", "neo4j", "chromadb", "ollama"]:
                    print(f"  {service['name']}: http://localhost:{service['port']}")
            return True
        else:
            print("❌ 部分服务启动失败！")
            return False
    
    def stop_all_services(self):
        """停止所有服务"""
        print("\n停止所有服务...")
        
        # 停止Python服务
        for service_name, process in self.running_processes.items():
            try:
                print(f"  停止 {service_name}...")
                process.terminate()
                process.wait(timeout=10)
                print(f"  ✅ {service_name} 已停止")
            except Exception as e:
                print(f"  ❌ 停止 {service_name} 失败: {str(e)}")
        
        # 停止Docker服务
        docker_services = ["fire_emergency_redis", "fire_emergency_postgres", 
                          "fire_emergency_neo4j", "fire_emergency_chromadb", 
                          "fire_emergency_ollama"]
        
        for container_name in docker_services:
            try:
                print(f"  停止Docker容器 {container_name}...")
                subprocess.run(["docker", "stop", container_name], 
                             capture_output=True, timeout=10)
                subprocess.run(["docker", "rm", container_name], 
                             capture_output=True, timeout=10)
                print(f"  ✅ {container_name} 已停止")
            except Exception as e:
                print(f"  ❌ 停止 {container_name} 失败: {str(e)}")
    
    def run_health_check(self):
        """运行健康检查"""
        print("\n🔍 运行系统健康检查...")
        
        import asyncio
        from tests.test_system_integration import SystemIntegrationTest
        
        async def check_health():
            tester = SystemIntegrationTest()
            health_results = await tester.test_all_services_health()
            
            healthy_count = sum(1 for result in health_results.values() if result["status"] == "healthy")
            total_count = len(health_results)
            
            print(f"📊 健康检查结果: {healthy_count}/{total_count} 个服务健康")
            
            if healthy_count == total_count:
                print("✅ 所有服务健康！")
                return True
            else:
                print("❌ 部分服务不健康！")
                return False
        
        return asyncio.run(check_health())

def signal_handler(signum, frame):
    """信号处理器"""
    print("\n\n🛑 接收到停止信号，正在关闭所有服务...")
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
            print("\n🎉 系统启动完成！")
            
            # 运行健康检查
            if manager.run_health_check():
                print("\n✅ 系统健康检查通过！")
                print("\n📝 使用说明:")
                print("  - 按 Ctrl+C 停止所有服务")
                print("  - 访问 http://localhost:8000 查看应急服务")
                print("  - 访问 http://localhost:8001 查看用户服务")
                print("  - 访问 http://localhost:8002 查看管理服务")
                print("  - 访问 http://localhost:8003 查看Ollama服务")
                print("  - 访问 http://localhost:8004 查看缓存服务")
                print("  - 访问 http://localhost:8005 查看RAG服务")
                print("  - 访问 http://localhost:8006 查看知识图谱服务")
                
                # 保持运行
                try:
                    while True:
                        time.sleep(1)
                except KeyboardInterrupt:
                    pass
            else:
                print("\n❌ 系统健康检查失败！")
        else:
            print("\n❌ 系统启动失败！")
    
    except KeyboardInterrupt:
        pass
    finally:
        manager.stop_all_services()

if __name__ == "__main__":
    main()
