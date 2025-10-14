#!/usr/bin/env python3
"""
系统状态监控脚本
实时监控所有服务的健康状态
"""

import time
import requests
import json
from datetime import datetime
from typing import Dict, List
import argparse

class SystemMonitor:
    """系统监控器"""
    
    def __init__(self):
        self.services = {
            "postgres": {"port": 5432, "health_url": None, "name": "PostgreSQL数据库"},
            "redis": {"port": 6379, "health_url": None, "name": "Redis缓存"},
            "neo4j": {"port": 7687, "health_url": "http://localhost:7474", "name": "Neo4j数据库"},
            "chromadb": {"port": 8007, "health_url": "http://localhost:8007/api/v1/heartbeat", "name": "ChromaDB向量数据库"},
            "ollama": {"port": 11434, "health_url": "http://localhost:11434/api/tags", "name": "Ollama AI服务"},
            "knowledge_graph": {"port": 8001, "health_url": "http://localhost:8001/health", "name": "知识图谱服务"},
            "ollama_service": {"port": 8003, "health_url": "http://localhost:8003/health", "name": "Ollama服务"},
            "cache": {"port": 8004, "health_url": "http://localhost:8004/health", "name": "缓存服务"},
            "rag": {"port": 3000, "health_url": "http://localhost:3000/health", "name": "RAG服务"},
            "emergency": {"port": 8000, "health_url": "http://localhost:8000/health", "name": "应急服务"}
        }
    
    def check_service_health(self, service_name: str) -> Dict:
        """检查单个服务健康状态"""
        service = self.services[service_name]
        
        if not service["health_url"]:
            return {
                "name": service["name"],
                "status": "unknown",
                "response_time": 0,
                "message": "无健康检查URL"
            }
        
        start_time = time.time()
        try:
            response = requests.get(service["health_url"], timeout=5)
            response_time = (time.time() - start_time) * 1000
            
            if response.status_code == 200:
                return {
                    "name": service["name"],
                    "status": "healthy",
                    "response_time": round(response_time, 2),
                    "message": "服务正常"
                }
            else:
                return {
                    "name": service["name"],
                    "status": "unhealthy",
                    "response_time": round(response_time, 2),
                    "message": f"HTTP {response.status_code}"
                }
        except requests.exceptions.Timeout:
            return {
                "name": service["name"],
                "status": "timeout",
                "response_time": 5000,
                "message": "连接超时"
            }
        except requests.exceptions.ConnectionError:
            return {
                "name": service["name"],
                "status": "unreachable",
                "response_time": 0,
                "message": "无法连接"
            }
        except Exception as e:
            return {
                "name": service["name"],
                "status": "error",
                "response_time": 0,
                "message": str(e)
            }
    
    def check_all_services(self) -> Dict:
        """检查所有服务状态"""
        results = {}
        for service_name in self.services:
            results[service_name] = self.check_service_health(service_name)
        return results
    
    def print_status_report(self, results: Dict):
        """打印状态报告"""
        print(f"\n{'='*80}")
        print(f"系统状态报告 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*80}")
        
        healthy_count = 0
        total_count = len(results)
        
        for service_name, result in results.items():
            status_icon = {
                "healthy": "[OK]",
                "unhealthy": "[ERROR]", 
                "timeout": "[TIMEOUT]",
                "unreachable": "[UNREACHABLE]",
                "error": "[WARNING]",
                "unknown": "[?]"
            }.get(result["status"], "[?]")
            
            print(f"{status_icon} {result['name']:20} | "
                  f"{result['status']:12} | "
                  f"{result['response_time']:8.2f}ms | "
                  f"{result['message']}")
            
            if result["status"] == "healthy":
                healthy_count += 1
        
        print(f"{'='*80}")
        print(f"总体状态: {healthy_count}/{total_count} 个服务正常")
        
        if healthy_count == total_count:
            print("[SUCCESS] 系统完全正常！")
        elif healthy_count >= total_count * 0.8:
            print("[WARNING] 系统基本正常，部分服务异常")
        else:
            print("[ERROR] 系统异常，需要检查")
        
        print(f"{'='*80}")
    
    def save_status_log(self, results: Dict, filename: str = "system_status.log"):
        """保存状态日志"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "services": results,
            "summary": {
                "total": len(results),
                "healthy": sum(1 for r in results.values() if r["status"] == "healthy"),
                "unhealthy": sum(1 for r in results.values() if r["status"] != "healthy")
            }
        }
        
        try:
            with open(filename, "a", encoding="utf-8") as f:
                f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")
        except Exception as e:
            print(f"保存日志失败: {e}")
    
    def monitor_continuous(self, interval: int = 30, save_log: bool = False):
        """持续监控"""
        print("开始持续监控系统状态...")
        print(f"监控间隔: {interval} 秒")
        print("按 Ctrl+C 停止监控")
        
        try:
            while True:
                results = self.check_all_services()
                self.print_status_report(results)
                
                if save_log:
                    self.save_status_log(results)
                
                print(f"\n下次检查时间: {interval} 秒后...")
                time.sleep(interval)
                
        except KeyboardInterrupt:
            print("\n监控已停止")
    
    def monitor_once(self, save_log: bool = False):
        """单次监控"""
        results = self.check_all_services()
        self.print_status_report(results)
        
        if save_log:
            self.save_status_log(results)
    
    def test_rescue_plan(self) -> bool:
        """测试救援方案生成功能"""
        print("\n测试救援方案生成功能...")
        
        test_data = {
            "items": [
                {
                    "name": "测试物品",
                    "material": "木质",
                    "quantity": 1,
                    "location": "客厅"
                }
            ],
            "environment": {
                "type": "室内",
                "location": "客厅",
                "area": "住宅",
                "weather": "晴天",
                "wind_speed": "微风",
                "ventilation": "良好",
                "exits": 2
            }
        }
        
        try:
            response = requests.post(
                "http://localhost:8000/rescue-plan",
                json=test_data,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get("success"):
                    print("[OK] 救援方案生成测试成功")
                    print(f"   生成了 {len(result.get('data', {}).get('steps', []))} 个步骤")
                    return True
                else:
                    print(f"[ERROR] 救援方案生成失败: {result.get('message', '未知错误')}")
                    return False
            else:
                print(f"[ERROR] 救援方案生成测试失败: HTTP {response.status_code}")
                return False
                
        except Exception as e:
            print(f"[ERROR] 救援方案生成测试出错: {e}")
            return False

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="系统状态监控脚本")
    parser.add_argument("--mode", choices=["once", "continuous"], default="once",
                       help="监控模式: once=单次检查, continuous=持续监控")
    parser.add_argument("--interval", type=int, default=30,
                       help="持续监控间隔时间(秒)")
    parser.add_argument("--log", action="store_true",
                       help="保存状态日志")
    parser.add_argument("--test", action="store_true",
                       help="测试救援方案生成功能")
    
    args = parser.parse_args()
    
    monitor = SystemMonitor()
    
    if args.mode == "once":
        monitor.monitor_once(save_log=args.log)
    else:
        monitor.monitor_continuous(interval=args.interval, save_log=args.log)
    
    if args.test:
        monitor.test_rescue_plan()

if __name__ == "__main__":
    main()
