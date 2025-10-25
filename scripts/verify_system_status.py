#!/usr/bin/env python3
"""
系统状态验证脚本
检查所有服务的健康状态和功能完整性
"""

import asyncio
import httpx
import json
import sys
from datetime import datetime
from typing import Dict, Any, List

class SystemVerifier:
    """系统验证器"""
    
    def __init__(self):
        self.services = {
            "emergency": {"url": "http://localhost:8000", "name": "应急服务"},
            "knowledge_graph": {"url": "http://localhost:8001", "name": "知识图谱服务"},
            "ollama": {"url": "http://localhost:8003", "name": "Ollama服务"},
            "cache": {"url": "http://localhost:8004", "name": "缓存服务"},
            "rag": {"url": "http://localhost:3000", "name": "RAG服务"}
        }
        self.results = {}
    
    async def check_service_health(self, service_name: str, service_config: Dict[str, Any]) -> Dict[str, Any]:
        """检查单个服务健康状态"""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(f"{service_config['url']}/health")
                if response.status_code == 200:
                    data = response.json()
                    return {
                        "status": "healthy",
                        "response_time": response.elapsed.total_seconds() * 1000,
                        "data": data
                    }
                else:
                    return {
                        "status": "unhealthy",
                        "response_time": response.elapsed.total_seconds() * 1000,
                        "error": f"HTTP {response.status_code}"
                    }
        except Exception as e:
            return {
                "status": "unreachable",
                "response_time": 0,
                "error": str(e)
            }
    
    async def verify_all_services(self) -> Dict[str, Any]:
        """验证所有服务"""
        print("系统状态验证开始...")
        print("=" * 50)
        
        # 并行检查所有服务
        tasks = []
        for service_name, service_config in self.services.items():
            task = self.check_service_health(service_name, service_config)
            tasks.append((service_name, task))
        
        # 等待所有检查完成
        for service_name, task in tasks:
            result = await task
            self.results[service_name] = result
            
            status_icon = "[OK]" if result["status"] == "healthy" else "[X]"
            print(f"{status_icon} {self.services[service_name]['name']}: {result['status']}")
            if result["status"] == "healthy":
                print(f"    响应时间: {result['response_time']:.1f}ms")
            else:
                print(f"    错误: {result.get('error', 'Unknown error')}")
        
        # 统计结果
        healthy_count = sum(1 for r in self.results.values() if r["status"] == "healthy")
        total_count = len(self.results)
        
        print(f"\n系统状态统计:")
        print(f"  健康服务: {healthy_count}/{total_count}")
        print(f"  系统可用性: {(healthy_count/total_count)*100:.1f}%")
        
        if healthy_count == total_count:
            print("  [SUCCESS] 所有服务运行正常！")
            return {"overall_status": "healthy", "healthy_services": healthy_count, "total_services": total_count}
        elif healthy_count >= total_count * 0.5:
            print("  [WARNING] 系统降级运行，部分功能可用")
            return {"overall_status": "degraded", "healthy_services": healthy_count, "total_services": total_count}
        else:
            print("  [ERROR] 系统不可用，需要检查服务状态")
            return {"overall_status": "unhealthy", "healthy_services": healthy_count, "total_services": total_count}
    
    async def test_emergency_workflow(self) -> bool:
        """测试应急工作流程"""
        print("\n测试应急工作流程...")
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                # 测试救援方案生成
                test_request = {
                    "items": [
                        {
                            "name": "沙发",
                            "material": "木质",
                            "quantity": 1,
                            "location": "客厅",
                            "condition": "正常",
                            "flammability": "易燃",
                            "toxicity": "无毒"
                        }
                    ],
                    "environment": {
                        "type": "室内",
                        "area": "住宅",
                        "floor": 1,
                        "ventilation": "良好",
                        "exits": 2,
                        "occupancy": 3,
                        "building_type": "住宅楼",
                        "fire_safety_equipment": ["灭火器"],
                        "special_conditions": "无"
                    },
                    "additional_info": "客厅发生火灾",
                    "urgency_level": "high"
                }

                response = await client.post(
                    "http://localhost:8000/rescue-plan",
                    json=test_request
                )
                
                if response.status_code == 200:
                    resp = response.json()
                    if isinstance(resp, dict) and resp.get("success") and isinstance(resp.get("data"), dict):
                        plan = resp["data"]
                        print("  [OK] 救援方案生成测试成功")
                        print(f"    方案标题: {plan.get('title', 'N/A')}")
                        print(f"    步骤数量: {len(plan.get('steps', []))}")
                        return True
                    else:
                        msg = resp.get("message", "响应格式不符合预期") if isinstance(resp, dict) else "响应不是JSON"
                        print(f"  [X] 救援方案生成测试失败: {msg}")
                        return False
                else:
                    print(f"  [X] 救援方案生成测试失败: HTTP {response.status_code}")
                    return False
                    
        except Exception as e:
            print(f"  [X] 工作流程测试失败: {repr(e)}")
            return False
    
    def generate_report(self) -> str:
        """生成验证报告"""
        report = []
        report.append("# 系统状态验证报告")
        report.append(f"验证时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("")
        
        # 服务状态
        report.append("## 服务状态")
        for service_name, result in self.results.items():
            service_config = self.services[service_name]
            status_icon = "[OK]" if result["status"] == "healthy" else "[X]"
            report.append(f"- {status_icon} {service_config['name']}: {result['status']}")
            if result["status"] == "healthy":
                report.append(f"  - 响应时间: {result['response_time']:.1f}ms")
            else:
                report.append(f"  - 错误: {result.get('error', 'Unknown error')}")
        
        # 系统统计
        healthy_count = sum(1 for r in self.results.values() if r["status"] == "healthy")
        total_count = len(self.results)
        availability = (healthy_count / total_count) * 100
        
        report.append("")
        report.append("## 系统统计")
        report.append(f"- 健康服务: {healthy_count}/{total_count}")
        report.append(f"- 系统可用性: {availability:.1f}%")
        
        if availability == 100:
            report.append("- 状态: [SUCCESS] 完全健康")
        elif availability >= 50:
            report.append("- 状态: [WARNING] 降级运行")
        else:
            report.append("- 状态: [ERROR] 不可用")
        
        return "\n".join(report)

async def main():
    """主函数"""
    verifier = SystemVerifier()
    
    # 验证服务状态
    system_status = await verifier.verify_all_services()
    
    # 如果应急服务健康，测试工作流程
    if system_status["overall_status"] in ["healthy", "degraded"]:
        workflow_success = await verifier.test_emergency_workflow()
        system_status["workflow_test"] = workflow_success
    
    # 生成报告
    report = verifier.generate_report()
    print("\n" + "=" * 50)
    print(report)
    
    # 保存报告
    with open("system_verification_report.md", "w", encoding="utf-8") as f:
        f.write(report)
    
    print(f"\n验证报告已保存到: system_verification_report.md")
    
    # 返回状态码
    if system_status["overall_status"] == "healthy":
        return 0
    elif system_status["overall_status"] == "degraded":
        return 1
    else:
        return 2

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
