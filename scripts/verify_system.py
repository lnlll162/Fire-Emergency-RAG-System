#!/usr/bin/env python3
"""
系统一键验证脚本
自动运行所有验证步骤并生成报告
"""

import asyncio
import sys
import json
import time
from datetime import datetime
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

# 导入系统集成测试
try:
    from tests.test_system_integration import SystemIntegrationTest
except ImportError:
    # 如果无法导入，创建一个简化的测试类
    class SystemIntegrationTest:
        def __init__(self):
            self.base_urls = {
                "cache_service": "http://localhost:8004",
                "ollama_service": "http://localhost:8003",
                "rag_service": "http://localhost:8005",
                "knowledge_graph_service": "http://localhost:8006",
                "emergency_service": "http://localhost:8000",
                "user_service": "http://localhost:8001",
                "admin_service": "http://localhost:8002"
            }
        
        async def test_all_services_health(self):
            import httpx
            health_results = {}
            for service_name, url in self.base_urls.items():
                try:
                    async with httpx.AsyncClient(timeout=10.0) as client:
                        response = await client.get(f"{url}/health")
                        if response.status_code == 200:
                            data = response.json()
                            health_results[service_name] = {
                                "status": "healthy",
                                "connected": data.get("data", {}).get("connected", False),
                                "response_time": response.elapsed.total_seconds(),
                                "details": data.get("data", {})
                            }
                        else:
                            health_results[service_name] = {
                                "status": "unhealthy",
                                "connected": False,
                                "response_time": response.elapsed.total_seconds(),
                                "error": f"HTTP {response.status_code}"
                            }
                except Exception as e:
                    health_results[service_name] = {
                        "status": "unreachable",
                        "connected": False,
                        "response_time": None,
                        "error": str(e)
                    }
            return health_results
        
        async def test_cache_service_functionality(self):
            import httpx
            url = self.base_urls["cache_service"]
            test_results = {}
            try:
                async with httpx.AsyncClient(timeout=30.0) as client:
                    # 测试设置缓存
                    response = await client.post(
                        f"{url}/set",
                        params={
                            "key": "integration_test",
                            "value": "test_value",
                            "ttl": 3600,
                            "namespace": "integration"
                        }
                    )
                    test_results["set_cache"] = response.status_code == 200
                    
                    # 测试获取缓存
                    response = await client.get(
                        f"{url}/get/integration_test",
                        params={"namespace": "integration"}
                    )
                    test_results["get_cache"] = response.status_code == 200
                    
                    # 清理测试数据
                    await client.delete(
                        f"{url}/delete/integration_test",
                        params={"namespace": "integration"}
                    )
            except Exception as e:
                test_results["error"] = str(e)
            return test_results
        
        async def test_ollama_service_functionality(self):
            import httpx
            url = self.base_urls["ollama_service"]
            test_results = {}
            try:
                async with httpx.AsyncClient(timeout=30.0) as client:
                    response = await client.get(f"{url}/models")
                    test_results["list_models"] = response.status_code == 200
                    
                    response = await client.get(f"{url}/model-status")
                    test_results["model_status"] = response.status_code == 200
            except Exception as e:
                test_results["error"] = str(e)
            return test_results
        
        async def test_rag_service_functionality(self):
            import httpx
            url = self.base_urls["rag_service"]
            test_results = {}
            try:
                async with httpx.AsyncClient(timeout=30.0) as client:
                    response = await client.post(
                        f"{url}/search",
                        json={"query": "火灾应急", "top_k": 5}
                    )
                    test_results["document_search"] = response.status_code == 200
            except Exception as e:
                test_results["error"] = str(e)
            return test_results
        
        async def test_knowledge_graph_functionality(self):
            import httpx
            url = self.base_urls["knowledge_graph_service"]
            test_results = {}
            try:
                async with httpx.AsyncClient(timeout=30.0) as client:
                    response = await client.get(f"{url}/materials")
                    test_results["materials_query"] = response.status_code == 200
            except Exception as e:
                test_results["error"] = str(e)
            return test_results
        
        async def test_emergency_service_functionality(self):
            import httpx
            url = self.base_urls["emergency_service"]
            test_results = {}
            try:
                async with httpx.AsyncClient(timeout=30.0) as client:
                    response = await client.post(
                        f"{url}/generate-rescue-plan",
                        json={
                            "items": [{"name": "木质家具", "material": "wood", "flammability": "high", "toxicity": "low"}],
                            "environment": {"area": "indoor", "ventilation": "poor", "temperature": 25, "humidity": 60},
                            "urgency_level": "high"
                        }
                    )
                    test_results["rescue_plan_generation"] = response.status_code == 200
            except Exception as e:
                test_results["error"] = str(e)
            return test_results
        
        async def test_user_service_functionality(self):
            import httpx
            url = self.base_urls["user_service"]
            test_results = {}
            try:
                async with httpx.AsyncClient(timeout=30.0) as client:
                    response = await client.post(
                        f"{url}/login",
                        json={"username": "test_user", "password": "test_password"}
                    )
                    test_results["user_login"] = response.status_code in [200, 401]
            except Exception as e:
                test_results["error"] = str(e)
            return test_results
        
        async def test_admin_service_functionality(self):
            import httpx
            url = self.base_urls["admin_service"]
            test_results = {}
            try:
                async with httpx.AsyncClient(timeout=30.0) as client:
                    response = await client.get(f"{url}/system-status")
                    test_results["system_status"] = response.status_code == 200
            except Exception as e:
                test_results["error"] = str(e)
            return test_results
        
        async def test_end_to_end_workflow(self):
            import httpx
            workflow_results = {}
            try:
                async with httpx.AsyncClient(timeout=60.0) as client:
                    # 测试救援方案生成
                    response = await client.post(
                        f"{self.base_urls['emergency_service']}/generate-rescue-plan",
                        json={
                            "items": [{"name": "办公桌", "material": "wood", "flammability": "high", "toxicity": "low"}],
                            "environment": {"area": "indoor", "ventilation": "poor", "temperature": 30, "humidity": 70},
                            "urgency_level": "high"
                        }
                    )
                    workflow_results["rescue_plan"] = response.status_code == 200
                    
                    # 测试缓存
                    if workflow_results["rescue_plan"]:
                        cache_response = await client.post(
                            f"{self.base_urls['cache_service']}/set",
                            params={
                                "key": "rescue_plan_001",
                                "value": "test_plan",
                                "ttl": 3600,
                                "namespace": "rescue_plans"
                            }
                        )
                        workflow_results["cache_plan"] = cache_response.status_code == 200
            except Exception as e:
                workflow_results["error"] = str(e)
            return workflow_results

class SystemVerifier:
    """系统验证器"""
    
    def __init__(self):
        self.test_results = {}
        self.start_time = None
        self.end_time = None
    
    async def run_complete_verification(self) -> dict:
        """运行完整系统验证"""
        print("[START] 开始系统完整验证...")
        print("=" * 60)
        
        self.start_time = time.time()
        
        # 1. 健康检查
        print("1️⃣ 运行健康检查...")
        health_results = await self._run_health_check()
        
        # 2. 功能测试
        print("\n2️⃣ 运行功能测试...")
        functionality_results = await self._run_functionality_tests()
        
        # 3. 端到端测试
        print("\n3️⃣ 运行端到端测试...")
        workflow_results = await self._run_workflow_tests()
        
        # 4. 性能测试
        print("\n4️⃣ 运行性能测试...")
        performance_results = await self._run_performance_tests()
        
        # 5. 生成验证报告
        self.end_time = time.time()
        verification_report = self._generate_verification_report(
            health_results, functionality_results, workflow_results, performance_results
        )
        
        # 6. 保存报告
        self._save_report(verification_report)
        
        # 7. 打印结果
        self._print_verification_results(verification_report)
        
        return verification_report
    
    async def _run_health_check(self) -> dict:
        """运行健康检查"""
        tester = SystemIntegrationTest()
        health_results = await tester.test_all_services_health()
        
        healthy_count = sum(1 for result in health_results.values() if result["status"] == "healthy")
        total_count = len(health_results)
        
        print(f"  健康服务: {healthy_count}/{total_count}")
        
        return {
            "results": health_results,
            "healthy_count": healthy_count,
            "total_count": total_count,
            "success_rate": healthy_count / total_count if total_count > 0 else 0
        }
    
    async def _run_functionality_tests(self) -> dict:
        """运行功能测试"""
        tester = SystemIntegrationTest()
        
        functionality_results = {
            "cache_service": await tester.test_cache_service_functionality(),
            "ollama_service": await tester.test_ollama_service_functionality(),
            "rag_service": await tester.test_rag_service_functionality(),
            "knowledge_graph_service": await tester.test_knowledge_graph_functionality(),
            "emergency_service": await tester.test_emergency_service_functionality(),
            "user_service": await tester.test_user_service_functionality(),
            "admin_service": await tester.test_admin_service_functionality()
        }
        
        # 计算成功率
        total_tests = 0
        passed_tests = 0
        
        for service_name, tests in functionality_results.items():
            for test_name, result in tests.items():
                if test_name != "error":
                    total_tests += 1
                    if result:
                        passed_tests += 1
        
        print(f"  功能测试: {passed_tests}/{total_tests}")
        
        return {
            "results": functionality_results,
            "passed_tests": passed_tests,
            "total_tests": total_tests,
            "success_rate": passed_tests / total_tests if total_tests > 0 else 0
        }
    
    async def _run_workflow_tests(self) -> dict:
        """运行端到端工作流程测试"""
        tester = SystemIntegrationTest()
        workflow_results = await tester.test_end_to_end_workflow()
        
        passed_workflows = sum(1 for result in workflow_results.values() if result is True)
        total_workflows = len(workflow_results)
        
        print(f"  工作流程: {passed_workflows}/{total_workflows}")
        
        return {
            "results": workflow_results,
            "passed_workflows": passed_workflows,
            "total_workflows": total_workflows,
            "success_rate": passed_workflows / total_workflows if total_workflows > 0 else 0
        }
    
    async def _run_performance_tests(self) -> dict:
        """运行性能测试"""
        import httpx
        
        performance_results = {}
        base_urls = {
            "cache_service": "http://localhost:8004",
            "ollama_service": "http://localhost:8003",
            "rag_service": "http://localhost:8005",
            "knowledge_graph_service": "http://localhost:8006",
            "emergency_service": "http://localhost:8000",
            "user_service": "http://localhost:8001",
            "admin_service": "http://localhost:8002"
        }
        
        response_times = []
        
        async with httpx.AsyncClient(timeout=10.0) as client:
            for service_name, url in base_urls.items():
                try:
                    start_time = time.time()
                    response = await client.get(f"{url}/health")
                    end_time = time.time()
                    
                    response_time = (end_time - start_time) * 1000  # 转换为毫秒
                    response_times.append(response_time)
                    
                    performance_results[service_name] = {
                        "response_time_ms": response_time,
                        "status_code": response.status_code,
                        "success": response.status_code == 200
                    }
                except Exception as e:
                    performance_results[service_name] = {
                        "response_time_ms": None,
                        "status_code": None,
                        "success": False,
                        "error": str(e)
                    }
        
        avg_response_time = sum(response_times) / len(response_times) if response_times else 0
        max_response_time = max(response_times) if response_times else 0
        
        print(f"  平均响应时间: {avg_response_time:.2f}ms")
        print(f"  最大响应时间: {max_response_time:.2f}ms")
        
        return {
            "results": performance_results,
            "average_response_time": avg_response_time,
            "max_response_time": max_response_time,
            "success_count": sum(1 for result in performance_results.values() if result["success"])
        }
    
    def _generate_verification_report(self, health_results, functionality_results, workflow_results, performance_results) -> dict:
        """生成验证报告"""
        total_duration = self.end_time - self.start_time
        
        # 计算总体成功率
        health_success = health_results["success_rate"]
        functionality_success = functionality_results["success_rate"]
        workflow_success = workflow_results["success_rate"]
        
        overall_success = (health_success + functionality_success + workflow_success) / 3
        
        # 判断系统状态
        if overall_success >= 0.9:
            system_status = "EXCELLENT"
        elif overall_success >= 0.8:
            system_status = "GOOD"
        elif overall_success >= 0.6:
            system_status = "FAIR"
        else:
            system_status = "POOR"
        
        return {
            "verification_time": datetime.now().isoformat(),
            "total_duration_seconds": total_duration,
            "system_status": system_status,
            "overall_success_rate": overall_success,
            "health_check": health_results,
            "functionality_tests": functionality_results,
            "workflow_tests": workflow_results,
            "performance_tests": performance_results,
            "recommendations": self._generate_recommendations(health_results, functionality_results, workflow_results, performance_results)
        }
    
    def _generate_recommendations(self, health_results, functionality_results, workflow_results, performance_results) -> list:
        """生成改进建议"""
        recommendations = []
        
        # 健康检查建议
        if health_results["success_rate"] < 1.0:
            recommendations.append("检查不健康的服务，确保所有服务正常运行")
        
        # 功能测试建议
        if functionality_results["success_rate"] < 0.9:
            recommendations.append("修复功能测试失败的服务，确保核心功能正常")
        
        # 工作流程建议
        if workflow_results["success_rate"] < 0.8:
            recommendations.append("优化端到端工作流程，确保业务流程完整")
        
        # 性能建议
        if performance_results["average_response_time"] > 5000:  # 5秒
            recommendations.append("优化服务性能，减少响应时间")
        
        if performance_results["success_count"] < len(performance_results["results"]):
            recommendations.append("检查服务可用性，确保所有服务可访问")
        
        if not recommendations:
            recommendations.append("系统运行良好，无需特别优化")
        
        return recommendations
    
    def _save_report(self, report: dict):
        """保存验证报告"""
        report_dir = Path("reports")
        report_dir.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = report_dir / f"verification_report_{timestamp}.json"
        
        with open(report_file, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"\n📄 验证报告已保存: {report_file}")
    
    def _print_verification_results(self, report: dict):
        """打印验证结果"""
        print("\n" + "=" * 60)
        print("[INFO] 系统验证报告")
        print("=" * 60)
        
        print(f"⏱️  验证时间: {report['verification_time']}")
        print(f"⏱️  总耗时: {report['total_duration_seconds']:.2f} 秒")
        print(f"[STATUS] 系统状态: {report['system_status']}")
        print(f"[RATE] 总体成功率: {report['overall_success_rate']:.1%}")
        
        print(f"\n🏥 健康检查: {report['health_check']['healthy_count']}/{report['health_check']['total_count']} ({report['health_check']['success_rate']:.1%})")
        print(f"🧪 功能测试: {report['functionality_tests']['passed_tests']}/{report['functionality_tests']['total_tests']} ({report['functionality_tests']['success_rate']:.1%})")
        print(f"🔄 工作流程: {report['workflow_tests']['passed_workflows']}/{report['workflow_tests']['total_workflows']} ({report['workflow_tests']['success_rate']:.1%})")
        print(f"[PERF] 平均响应时间: {report['performance_tests']['average_response_time']:.2f}ms")
        
        print(f"\n[SUGGEST] 改进建议:")
        for i, recommendation in enumerate(report['recommendations'], 1):
            print(f"  {i}. {recommendation}")
        
        if report['system_status'] in ['EXCELLENT', 'GOOD']:
            print(f"\n[SUCCESS] 系统验证通过！系统可以正常运行。")
        else:
            print(f"\n[ERROR] 系统验证失败！需要修复问题后重新验证。")

async def main():
    """主函数"""
    verifier = SystemVerifier()
    report = await verifier.run_complete_verification()
    
    # 返回适当的退出码
    if report['system_status'] in ['EXCELLENT', 'GOOD']:
        sys.exit(0)
    else:
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
