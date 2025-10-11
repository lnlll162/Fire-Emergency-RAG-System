#!/usr/bin/env python3
"""
端口冲突检测和解决脚本
"""

import socket
import subprocess
import sys
import os
from typing import List, Dict, Any

def check_port_availability(port: int) -> bool:
    """检查端口是否可用"""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(1)
            result = s.connect_ex(('localhost', port))
            return result != 0  # 端口可用返回True
    except Exception:
        return False

def get_process_using_port(port: int) -> Dict[str, Any]:
    """获取占用端口的进程信息"""
    try:
        # Windows系统使用netstat命令
        result = subprocess.run(
            ['netstat', '-ano'], 
            capture_output=True, 
            text=True, 
            shell=True
        )
        
        lines = result.stdout.split('\n')
        for line in lines:
            if f':{port}' in line and 'LISTENING' in line:
                parts = line.split()
                if len(parts) >= 5:
                    pid = parts[-1]
                    return {
                        'port': port,
                        'pid': pid,
                        'status': 'LISTENING',
                        'process': get_process_name(pid)
                    }
    except Exception as e:
        print(f"获取进程信息失败: {e}")
    
    return {'port': port, 'pid': 'unknown', 'status': 'unknown', 'process': 'unknown'}

def get_process_name(pid: str) -> str:
    """根据PID获取进程名称"""
    try:
        result = subprocess.run(
            ['tasklist', '/FI', f'PID eq {pid}'],
            capture_output=True,
            text=True,
            shell=True
        )
        lines = result.stdout.split('\n')
        for line in lines:
            if pid in line:
                parts = line.split()
                if len(parts) >= 1:
                    return parts[0]
    except Exception:
        pass
    return 'unknown'

def check_docker_containers() -> List[Dict[str, Any]]:
    """检查Docker容器状态"""
    try:
        result = subprocess.run(
            ['docker', 'ps', '--format', 'table {{.Names}}\t{{.Ports}}\t{{.Status}}'],
            capture_output=True,
            text=True,
            shell=True
        )
        
        containers = []
        lines = result.stdout.split('\n')[1:]  # 跳过表头
        for line in lines:
            if line.strip():
                parts = line.split('\t')
                if len(parts) >= 3:
                    containers.append({
                        'name': parts[0],
                        'ports': parts[1],
                        'status': parts[2]
                    })
        return containers
    except Exception as e:
        print(f"检查Docker容器失败: {e}")
        return []

def main():
    """主函数"""
    print("端口冲突检测开始...")
    print("=" * 50)
    
    # 需要检查的端口
    required_ports = {
        8000: "应急服务",
        8001: "知识图谱服务", 
        8003: "Ollama服务",
        8004: "缓存服务",
        8006: "知识图谱服务(备用)",
        8007: "ChromaDB",
        8008: "RAG服务",
        11434: "Ollama后端"
    }
    
    conflicts = []
    available_ports = []
    
    print("端口状态检查:")
    for port, service in required_ports.items():
        is_available = check_port_availability(port)
        if is_available:
            print(f"  [OK] 端口 {port} ({service}) - 可用")
            available_ports.append(port)
        else:
            print(f"  [X] 端口 {port} ({service}) - 被占用")
            process_info = get_process_using_port(port)
            conflicts.append({
                'port': port,
                'service': service,
                'process_info': process_info
            })
            print(f"     占用进程: PID {process_info['pid']} - {process_info['process']}")
    
    print(f"\n端口状态统计:")
    print(f"  可用端口: {len(available_ports)}/{len(required_ports)}")
    print(f"  冲突端口: {len(conflicts)}")
    
    # 检查Docker容器
    print(f"\nDocker容器状态:")
    containers = check_docker_containers()
    if containers:
        for container in containers:
            print(f"  {container['name']}: {container['status']}")
            if container['ports']:
                print(f"    端口: {container['ports']}")
    else:
        print("  没有运行中的Docker容器")
    
    # 提供解决方案
    if conflicts:
        print(f"\n解决方案建议:")
        for conflict in conflicts:
            port = conflict['port']
            service = conflict['service']
            pid = conflict['process_info']['pid']
            
            if port == 8007:
                print(f"  端口 {port} ({service}):")
                print(f"    - 这是ChromaDB端口，可能被Docker容器占用")
                print(f"    - 建议: 停止Docker容器或使用其他端口")
                print(f"    - 命令: docker stop fire_emergency_chromadb")
            elif port == 11434:
                print(f"  端口 {port} ({service}):")
                print(f"    - 这是Ollama后端端口，可能被Docker容器占用")
                print(f"    - 建议: 停止Docker容器或使用其他端口")
                print(f"    - 命令: docker stop fire_emergency_ollama")
            else:
                print(f"  端口 {port} ({service}):")
                print(f"    - 被进程 {pid} 占用")
                print(f"    - 建议: 终止进程或使用其他端口")
                print(f"    - 命令: taskkill /PID {pid} /F")
    
    print(f"\n检测完成！")
    return len(conflicts) == 0

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
