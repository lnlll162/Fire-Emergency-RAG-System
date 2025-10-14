#!/usr/bin/env python3
"""
火灾应急救援RAG系统 - 一键启动脚本
智能启动所有服务，处理依赖关系和错误恢复
"""

import os
import sys
import time
import signal
import subprocess
import threading
import requests
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import json
import logging

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('system_startup.log', encoding='utf-8')
    ]
)
logger = logging.getLogger(__name__)

class SystemStarter:
    """系统启动管理器"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.running_processes: Dict[str, subprocess.Popen] = {}
        self.service_configs = {
            "postgres": {"port": 5432, "health_url": None, "required": True},
            "redis": {"port": 6379, "health_url": None, "required": True},
            "neo4j": {"port": 7687, "health_url": "http://localhost:7474", "required": True},
            "chromadb": {"port": 8007, "health_url": "http://localhost:8007/api/v1/heartbeat", "required": True},
            "ollama": {"port": 11434, "health_url": "http://localhost:11434/api/tags", "required": True},
            "knowledge_graph": {"port": 8001, "health_url": "http://localhost:8001/health", "required": False},
            "ollama_service": {"port": 8003, "health_url": "http://localhost:8003/health", "required": True},
            "cache": {"port": 8004, "health_url": "http://localhost:8004/health", "required": True},
            "rag": {"port": 3000, "health_url": "http://localhost:3000/health", "required": False},
            "emergency": {"port": 8000, "health_url": "http://localhost:8000/health", "required": True}
        }
        self.startup_order = [
            "postgres", "redis", "neo4j", "chromadb", "ollama",
            "knowledge_graph", "ollama_service", "cache", "rag", "emergency"
        ]
        
        # 服务名称到脚本名称的映射
        self.service_script_mapping = {
            "knowledge_graph": "knowledge_graph",
            "ollama_service": "ollama",
            "cache": "cache",
            "rag": "rag",
            "emergency": "emergency"
        }
        
    def check_port_available(self, port: int) -> bool:
        """检查端口是否可用"""
        try:
            import socket
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(1)
                result = s.connect_ex(('localhost', port))
                return result != 0
        except Exception:
            return False
    
    def kill_process_on_port(self, port: int) -> bool:
        """终止占用指定端口的进程"""
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
                                logger.info(f"已终止端口 {port} 上的进程 {pid}")
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
                        logger.info(f"已终止端口 {port} 上的进程 {pid}")
                    return True
        except Exception as e:
            logger.warning(f"终止端口 {port} 上的进程时出错: {e}")
        return False
    
    def start_docker_services(self) -> bool:
        """启动Docker服务"""
        logger.info("启动Docker数据库服务...")
        try:
            docker_compose_path = self.project_root / "infrastructure" / "docker" / "docker-compose.yml"
            if not docker_compose_path.exists():
                logger.error(f"Docker Compose文件不存在: {docker_compose_path}")
                return False
            
            # 启动数据库服务
            cmd = [
                "docker-compose", "-f", str(docker_compose_path),
                "up", "-d", "postgres", "redis", "neo4j", "chromadb", "ollama"
            ]
            
            result = subprocess.run(cmd, cwd=docker_compose_path.parent, 
                                  capture_output=True, text=True, timeout=120)
            
            if result.returncode == 0:
                logger.info("Docker数据库服务启动成功")
                return True
            else:
                logger.error(f"Docker服务启动失败: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            logger.error("Docker服务启动超时")
            return False
        except Exception as e:
            logger.error(f"启动Docker服务时出错: {e}")
            return False
    
    def wait_for_service(self, service_name: str, max_wait: int = 30) -> bool:
        """等待服务启动完成"""
        config = self.service_configs[service_name]
        if not config["health_url"]:
            return True
            
        logger.info(f"等待 {service_name} 服务启动...")
        start_time = time.time()
        
        while time.time() - start_time < max_wait:
            try:
                response = requests.get(config["health_url"], timeout=5)
                if response.status_code == 200:
                    logger.info(f"{service_name} 服务启动成功")
                    return True
            except requests.exceptions.RequestException:
                pass
            
            time.sleep(2)
        
        logger.warning(f"{service_name} 服务启动超时")
        return False
    
    def start_python_service(self, service_name: str) -> bool:
        """启动Python服务"""
        # 使用映射获取正确的脚本名称
        script_name = self.service_script_mapping.get(service_name, service_name)
        script_path = self.project_root / "scripts" / f"start_{script_name}_service.py"
        if not script_path.exists():
            logger.error(f"启动脚本不存在: {script_path}")
            return False
        
        try:
            # 检查端口是否被占用
            port = self.service_configs[service_name]["port"]
            if not self.check_port_available(port):
                logger.warning(f"端口 {port} 被占用，尝试释放...")
                self.kill_process_on_port(port)
                time.sleep(2)
            
            # 启动服务
            logger.info(f"启动 {service_name} 服务...")
            process = subprocess.Popen(
                [sys.executable, str(script_path)],
                cwd=str(self.project_root),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            self.running_processes[service_name] = process
            
            # 等待服务启动
            if self.wait_for_service(service_name):
                logger.info(f"{service_name} 服务启动成功")
                return True
            else:
                logger.error(f"{service_name} 服务启动失败")
                return False
                
        except Exception as e:
            logger.error(f"启动 {service_name} 服务时出错: {e}")
            return False
    
    def start_all_services(self) -> bool:
        """启动所有服务"""
        logger.info("开始启动火灾应急救援RAG系统...")
        
        # 1. 启动Docker服务
        if not self.start_docker_services():
            logger.error("Docker服务启动失败，无法继续")
            return False
        
        # 2. 等待数据库服务启动
        db_services = ["postgres", "redis", "neo4j", "chromadb", "ollama"]
        for service in db_services:
            if not self.wait_for_service(service, max_wait=60):
                logger.warning(f"数据库服务 {service} 启动可能有问题，但继续启动应用服务")
        
        # 3. 启动Python应用服务
        success_count = 0
        total_required = sum(1 for s in self.startup_order[5:] if self.service_configs[s]["required"])
        
        for service in self.startup_order[5:]:  # 跳过数据库服务
            if self.start_python_service(service):
                success_count += 1
            else:
                if self.service_configs[service]["required"]:
                    logger.error(f"必需服务 {service} 启动失败")
                    return False
                else:
                    logger.warning(f"可选服务 {service} 启动失败，系统将在降级模式下运行")
        
        logger.info(f"服务启动完成: {success_count}/{len(self.startup_order[5:])} 个服务成功启动")
        return True
    
    def check_system_health(self) -> Dict[str, bool]:
        """检查系统健康状态"""
        health_status = {}
        
        for service_name, config in self.service_configs.items():
            if not config["health_url"]:
                health_status[service_name] = True
                continue
                
            try:
                response = requests.get(config["health_url"], timeout=5)
                health_status[service_name] = response.status_code == 200
            except requests.exceptions.RequestException:
                health_status[service_name] = False
        
        return health_status
    
    def print_system_status(self):
        """打印系统状态"""
        logger.info("检查系统状态...")
        health_status = self.check_system_health()
        
        print("\n" + "="*60)
        print("系统状态报告")
        print("="*60)
        
        for service_name, is_healthy in health_status.items():
            status = "[OK] 健康" if is_healthy else "[ERROR] 异常"
            port = self.service_configs[service_name]["port"]
            print(f"{service_name:20} | {status:10} | 端口: {port}")
        
        healthy_count = sum(health_status.values())
        total_count = len(health_status)
        print(f"\n总体状态: {healthy_count}/{total_count} 个服务正常")
        
        if healthy_count == total_count:
            print("[SUCCESS] 系统完全正常！")
        elif healthy_count >= total_count * 0.8:
            print("[WARNING] 系统基本正常，部分服务异常")
        else:
            print("[ERROR] 系统异常，需要检查")
        
        print("="*60)
    
    def cleanup(self):
        """清理资源"""
        logger.info("清理资源...")
        
        # 终止Python进程
        for service_name, process in self.running_processes.items():
            try:
                process.terminate()
                process.wait(timeout=5)
                logger.info(f"已终止 {service_name} 服务")
            except subprocess.TimeoutExpired:
                process.kill()
                logger.warning(f"强制终止 {service_name} 服务")
            except Exception as e:
                logger.error(f"终止 {service_name} 服务时出错: {e}")
        
        self.running_processes.clear()
    
    def run(self):
        """运行启动流程"""
        try:
            # 设置信号处理
            def signal_handler(signum, frame):
                logger.info("收到退出信号，正在清理...")
                self.cleanup()
                sys.exit(0)
            
            signal.signal(signal.SIGINT, signal_handler)
            signal.signal(signal.SIGTERM, signal_handler)
            
            # 启动系统
            if self.start_all_services():
                self.print_system_status()
                
                # 保持运行
                logger.info("系统启动完成！按 Ctrl+C 退出")
                try:
                    while True:
                        time.sleep(10)
                        # 定期检查系统状态
                        health_status = self.check_system_health()
                        unhealthy_services = [k for k, v in health_status.items() if not v]
                        if unhealthy_services:
                            logger.warning(f"检测到异常服务: {unhealthy_services}")
                except KeyboardInterrupt:
                    logger.info("收到退出信号")
            else:
                logger.error("系统启动失败")
                return False
                
        except Exception as e:
            logger.error(f"启动过程中出错: {e}")
            return False
        finally:
            self.cleanup()
        
        return True

def main():
    """主函数"""
    print("火灾应急救援RAG系统 - 一键启动")
    print("="*50)
    
    starter = SystemStarter()
    success = starter.run()
    
    if success:
        print("系统启动成功！")
        sys.exit(0)
    else:
        print("系统启动失败！")
        sys.exit(1)

if __name__ == "__main__":
    main()
