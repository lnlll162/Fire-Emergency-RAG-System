#!/usr/bin/env python3
"""
应急服务
系统核心协调服务，集成知识图谱、RAG、Ollama、缓存等服务
提供完整的火灾应急救援方案生成功能
"""

import asyncio
import logging
import sys
import json
import hashlib
import time
from typing import List, Dict, Any, Optional, Union, Tuple
from datetime import datetime, timedelta
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks, Query
from pydantic import BaseModel, Field, field_validator
import httpx
from httpx import AsyncClient, TimeoutException, HTTPError

from shared.config import get_config
from shared.exceptions import ExternalServiceError, TimeoutError, ServiceError, ValidationError
from shared.models import (
    RescuePlan, RescuePlanRequest, Item, Environment, RescueStep, PriorityLevel,
    APIResponse, ErrorResponse, PaginationParams, PaginatedResponse
)

# 配置日志
logger = logging.getLogger(__name__)

# 数据模型
class ServiceStatus(BaseModel):
    """服务状态模型"""
    service_name: str = Field(..., description="服务名称")
    status: str = Field(..., description="状态")
    response_time: float = Field(..., description="响应时间(毫秒)")
    last_check: datetime = Field(default_factory=datetime.now, description="最后检查时间")
    error_message: Optional[str] = Field(None, description="错误信息")

class EmergencyServiceHealth(BaseModel):
    """应急服务健康状态"""
    overall_status: str = Field(..., description="整体状态")
    services: List[ServiceStatus] = Field(..., description="各服务状态")
    total_services: int = Field(..., description="总服务数")
    healthy_services: int = Field(..., description="健康服务数")
    last_check: datetime = Field(default_factory=datetime.now, description="最后检查时间")

class KnowledgeContext(BaseModel):
    """知识上下文模型"""
    material_knowledge: Dict[str, Any] = Field(default_factory=dict, description="材质知识")
    environment_knowledge: Dict[str, Any] = Field(default_factory=dict, description="环境知识")
    rescue_procedures: List[Dict[str, Any]] = Field(default_factory=list, description="救援程序")
    rag_context: List[Dict[str, Any]] = Field(default_factory=list, description="RAG上下文")
    total_context_size: int = Field(default=0, description="总上下文大小")

class EmergencyService:
    """应急服务类"""
    
    def __init__(self):
        self.config = get_config()
        self.services = {
            "knowledge_graph": {
                "url": f"http://localhost:8001",
                "timeout": 10.0,
                "required": True
            },
            "rag": {
                "url": f"http://localhost:8008", 
                "timeout": 15.0,
                "required": True
            },
            "ollama": {
                "url": f"http://localhost:8003",
                "timeout": 120.0,
                "required": True
            },
            "cache": {
                "url": f"http://localhost:8004",
                "timeout": 5.0,
                "required": False
            }
        }
        self.cache_enabled = True
        self._initialize_services()
    
    def _initialize_services(self):
        """初始化服务连接"""
        logger.info("初始化应急服务...")
        # 服务将在第一次调用时进行健康检查
        logger.info("应急服务初始化完成")
    
    async def _check_service_health(self, service_name: str, service_config: Dict[str, Any]) -> ServiceStatus:
        """检查单个服务健康状态"""
        start_time = time.time()
        try:
            async with AsyncClient(timeout=service_config["timeout"]) as client:
                response = await client.get(f"{service_config['url']}/health")
                response_time = (time.time() - start_time) * 1000
                
                if response.status_code == 200:
                    data = response.json()
                    is_healthy = data.get("success", False)
                    return ServiceStatus(
                        service_name=service_name,
                        status="healthy" if is_healthy else "unhealthy",
                        response_time=response_time,
                        error_message=None if is_healthy else "服务返回不健康状态"
                    )
                else:
                    return ServiceStatus(
                        service_name=service_name,
                        status="unhealthy",
                        response_time=response_time,
                        error_message=f"HTTP {response.status_code}"
                    )
        except TimeoutException:
            return ServiceStatus(
                service_name=service_name,
                status="unhealthy",
                response_time=(time.time() - start_time) * 1000,
                error_message="连接超时"
            )
        except Exception as e:
            return ServiceStatus(
                service_name=service_name,
                status="unhealthy",
                response_time=(time.time() - start_time) * 1000,
                error_message=str(e)
            )
    
    async def check_health(self) -> EmergencyServiceHealth:
        """检查所有服务健康状态"""
        logger.info("开始健康检查...")
        
        # 并行检查所有服务
        tasks = []
        for service_name, service_config in self.services.items():
            task = self._check_service_health(service_name, service_config)
            tasks.append(task)
        
        service_statuses = await asyncio.gather(*tasks, return_exceptions=True)
        
        # 处理异常结果
        processed_statuses = []
        for i, status in enumerate(service_statuses):
            if isinstance(status, Exception):
                service_name = list(self.services.keys())[i]
                processed_statuses.append(ServiceStatus(
                    service_name=service_name,
                    status="unhealthy",
                    response_time=0.0,
                    error_message=str(status)
                ))
            else:
                processed_statuses.append(status)
        
        # 计算健康状态
        healthy_count = sum(1 for status in processed_statuses if status.status == "healthy")
        total_count = len(processed_statuses)
        
        # 检查必需服务是否健康
        required_services_healthy = all(
            status.status == "healthy" 
            for status in processed_statuses 
            if self.services[status.service_name]["required"]
        )
        
        overall_status = "healthy" if required_services_healthy else "degraded"
        
        return EmergencyServiceHealth(
            overall_status=overall_status,
            services=processed_statuses,
            total_services=total_count,
            healthy_services=healthy_count
        )
    
    async def _call_service(self, service_name: str, endpoint: str, method: str = "GET", 
                           data: Optional[Dict[str, Any]] = None, timeout: Optional[float] = None) -> Dict[str, Any]:
        """调用外部服务"""
        service_config = self.services[service_name]
        url = f"{service_config['url']}{endpoint}"
        request_timeout = timeout or service_config["timeout"]
        
        try:
            async with AsyncClient(timeout=request_timeout) as client:
                if method.upper() == "GET":
                    response = await client.get(url, params=data)
                elif method.upper() == "POST":
                    response = await client.post(url, json=data)
                else:
                    raise ValueError(f"不支持的HTTP方法: {method}")
                
                response.raise_for_status()
                return response.json()
        except TimeoutException:
            raise TimeoutError(f"服务 {service_name} 调用超时", service_name, request_timeout)
        except HTTPError as e:
            raise ExternalServiceError(f"服务 {service_name} 调用失败: {str(e)}", service_name)
        except Exception as e:
            raise ServiceError(f"服务 {service_name} 调用异常: {str(e)}", "emergency_service")
    
    def _generate_cache_key(self, request: RescuePlanRequest) -> str:
        """生成缓存键"""
        # 创建请求的哈希值作为缓存键
        request_data = {
            "items": [item.model_dump() for item in request.items],
            "environment": request.environment.model_dump(),
            "additional_info": request.additional_info,
            "urgency_level": request.urgency_level
        }
        request_str = json.dumps(request_data, sort_keys=True, ensure_ascii=False)
        return f"emergency:rescue_plan:{hashlib.md5(request_str.encode()).hexdigest()}"
    
    async def _get_cached_result(self, cache_key: str) -> Optional[RescuePlan]:
        """从缓存获取结果"""
        if not self.cache_enabled:
            return None
        
        try:
            result = await self._call_service("cache", f"/get/{cache_key}")
            if result.get("success") and result.get("data"):
                return RescuePlan(**result["data"])
        except Exception as e:
            logger.warning(f"获取缓存失败: {str(e)}")
            self.cache_enabled = False
        return None
    
    async def _set_cached_result(self, cache_key: str, rescue_plan: RescuePlan, ttl: int = 3600):
        """设置缓存结果"""
        if not self.cache_enabled:
            return
        
        try:
            await self._call_service("cache", "/set", "POST", {
                "key": cache_key,
                "value": rescue_plan.model_dump(mode='json'),
                "ttl": ttl
            })
        except Exception as e:
            logger.warning(f"设置缓存失败: {str(e)}")
            self.cache_enabled = False
    
    async def _gather_knowledge_context(self, request: RescuePlanRequest) -> KnowledgeContext:
        """收集知识上下文"""
        logger.info("开始收集知识上下文...")
        
        # 并行收集各种知识
        tasks = []
        
        # 收集材质知识
        material_tasks = []
        for item in request.items:
            task = self._call_service("knowledge_graph", f"/materials/{item.material.value}")
            material_tasks.append(task)
        
        # 收集环境知识
        env_task = self._call_service("knowledge_graph", f"/environments/{request.environment.area.value}")
        
        # 收集救援程序
        procedures_task = self._call_service("knowledge_graph", "/procedures")
        
        # 收集RAG上下文
        rag_contexts = []
        for item in request.items:
            rag_task = self._call_service("rag", "/search", "POST", {
                "query": f"{item.name} {item.material.value} 火灾 救援",
                "limit": 3
            })
            rag_contexts.append(rag_task)
        
        # 等待所有任务完成
        try:
            material_results = await asyncio.gather(*material_tasks, return_exceptions=True)
            env_result = await env_task
            procedures_result = await procedures_task
            rag_results = await asyncio.gather(*rag_contexts, return_exceptions=True)
            
            # 处理材质知识结果
            material_knowledge = {}
            for i, result in enumerate(material_results):
                if not isinstance(result, Exception) and result.get("success"):
                    material_knowledge[request.items[i].material.value] = result["data"]
            
            # 处理环境知识结果
            environment_knowledge = {}
            if not isinstance(env_result, Exception) and env_result.get("success"):
                environment_knowledge = env_result["data"]
            
            # 处理救援程序结果
            rescue_procedures = []
            if not isinstance(procedures_result, Exception) and procedures_result.get("success"):
                rescue_procedures = procedures_result["data"]
            
            # 处理RAG上下文结果
            rag_context = []
            for result in rag_results:
                if not isinstance(result, Exception) and result.get("success"):
                    rag_context.extend(result["data"])
            
            # 计算总上下文大小
            total_size = len(json.dumps(material_knowledge, ensure_ascii=False)) + \
                        len(json.dumps(environment_knowledge, ensure_ascii=False)) + \
                        len(json.dumps(rescue_procedures, ensure_ascii=False)) + \
                        len(json.dumps(rag_context, ensure_ascii=False))
            
            return KnowledgeContext(
                material_knowledge=material_knowledge,
                environment_knowledge=environment_knowledge,
                rescue_procedures=rescue_procedures,
                rag_context=rag_context,
                total_context_size=total_size
            )
            
        except Exception as e:
            logger.error(f"收集知识上下文失败: {str(e)}")
            # 返回空上下文，让系统继续运行
            return KnowledgeContext()
    
    def _validate_request(self, request: RescuePlanRequest) -> None:
        """验证请求数据"""
        if not request.items:
            raise ValidationError("物品列表不能为空")
        
        if len(request.items) > 50:
            raise ValidationError("物品数量不能超过50个")
        
        for item in request.items:
            if not item.name.strip():
                raise ValidationError("物品名称不能为空")
            
            if item.quantity <= 0:
                raise ValidationError("物品数量必须大于0")
            
            if not item.location.strip():
                raise ValidationError("物品位置不能为空")
        
        if request.environment.exits <= 0:
            raise ValidationError("出口数量必须大于0")
        
        if request.environment.occupancy is not None and request.environment.occupancy < 0:
            raise ValidationError("人员数量不能为负数")
    
    async def generate_rescue_plan(self, request: RescuePlanRequest) -> RescuePlan:
        """生成救援方案"""
        logger.info("开始生成救援方案...")
        
        # 验证请求
        self._validate_request(request)
        
        # 检查缓存
        cache_key = self._generate_cache_key(request)
        cached_result = await self._get_cached_result(cache_key)
        if cached_result:
            logger.info("从缓存返回救援方案")
            return cached_result
        
        try:
            # 收集知识上下文
            knowledge_context = await self._gather_knowledge_context(request)
            logger.info(f"收集到知识上下文，大小: {knowledge_context.total_context_size} 字符")
            
            # 构建增强的救援方案请求
            enhanced_request = {
                "items": [item.model_dump() for item in request.items],
                "environment": request.environment.model_dump(),
                "additional_info": request.additional_info or "",
                "urgency_level": request.urgency_level,
                "knowledge_context": knowledge_context.model_dump()
            }
            
            # 调用Ollama服务生成救援方案
            ollama_response = await self._call_service("ollama", "/rescue-plan", "POST", enhanced_request)
            
            if not ollama_response.get("success"):
                raise ServiceError("Ollama服务生成救援方案失败", "emergency_service")
            
            # 解析救援方案
            rescue_plan_data = ollama_response["data"]
            rescue_plan = RescuePlan(**rescue_plan_data)
            
            # 缓存结果
            await self._set_cached_result(cache_key, rescue_plan)
            
            logger.info(f"救援方案生成成功，包含 {len(rescue_plan.steps)} 个步骤")
            return rescue_plan
            
        except Exception as e:
            logger.error(f"生成救援方案失败: {str(e)}")
            # 返回默认救援方案
            return self._create_fallback_rescue_plan(request)
    
    def _create_fallback_rescue_plan(self, request: RescuePlanRequest) -> RescuePlan:
        """创建降级救援方案"""
        logger.warning("使用降级救援方案")
        
        # 根据紧急程度确定优先级
        priority = PriorityLevel.MEDIUM
        if request.urgency_level in ["紧急", "非常紧急"]:
            priority = PriorityLevel.URGENT
        elif request.urgency_level in ["低", "一般"]:
            priority = PriorityLevel.LOW
        
        # 创建基本救援步骤
        steps = [
            RescueStep(
                step_number=1,
                description="立即报警并疏散人员",
                equipment=["通信设备", "疏散指示牌"],
                warnings=["确保所有人员安全撤离", "保持冷静"],
                estimated_time=5
            ),
            RescueStep(
                step_number=2,
                description="评估火势和现场情况",
                equipment=["防护装备", "检测设备"],
                warnings=["注意自身安全", "避免进入危险区域"],
                estimated_time=10
            ),
            RescueStep(
                step_number=3,
                description="使用适当的灭火器材进行灭火",
                equipment=["灭火器", "消防水带"],
                warnings=["选择合适的灭火器材", "注意风向"],
                estimated_time=20
            ),
            RescueStep(
                step_number=4,
                description="确保火势完全扑灭并检查现场",
                equipment=["检测设备", "照明设备"],
                warnings=["确保无复燃风险", "检查是否有人员受伤"],
                estimated_time=15
            )
        ]
        
        # 收集设备清单
        equipment_list = []
        for step in steps:
            equipment_list.extend(step.equipment)
        equipment_list = list(set(equipment_list))
        
        # 收集警告信息
        warnings = []
        for step in steps:
            warnings.extend(step.warnings)
        warnings = list(set(warnings))
        
        return RescuePlan(
            title=f"火灾应急救援方案 - {request.environment.area.value}",
            priority=priority,
            steps=steps,
            equipment_list=equipment_list,
            warnings=warnings,
            estimated_duration=sum(step.estimated_time or 0 for step in steps)
        )
    
    async def get_service_status(self) -> Dict[str, Any]:
        """获取服务状态信息"""
        health = await self.check_health()
        return {
            "overall_status": health.overall_status,
            "services": {s.service_name: s.model_dump() for s in health.services},
            "cache_enabled": self.cache_enabled,
            "last_check": health.last_check
        }

# 创建服务实例
emergency_service = EmergencyService()

# FastAPI应用
app = FastAPI(
    title="应急服务",
    description="火灾应急救援系统核心协调服务，集成知识图谱、RAG、Ollama、缓存等服务",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# 依赖注入
def get_emergency_service() -> EmergencyService:
    return emergency_service

# API路由
@app.get("/", response_model=APIResponse)
async def root():
    """根路径 - 服务信息"""
    return APIResponse(
        success=True,
        message="应急服务运行正常",
        data={
            "service": "应急服务",
            "version": "1.0.0",
            "description": "火灾应急救援系统核心协调服务",
            "endpoints": {
                "health": "/health",
                "rescue-plan": "/rescue-plan",
                "status": "/status",
                "docs": "/docs"
            }
        }
    )

@app.get("/health", response_model=APIResponse)
async def health_check(service: EmergencyService = Depends(get_emergency_service)):
    """健康检查"""
    try:
        health = await service.check_health()
        return APIResponse(
            success=health.overall_status in ["healthy", "degraded"],
            message=f"健康检查完成，状态: {health.overall_status}",
            data=health.model_dump()
        )
    except Exception as e:
        return APIResponse(
            success=False,
            message=f"健康检查失败: {str(e)}",
            data={"overall_status": "unhealthy"}
        )

@app.get("/status", response_model=APIResponse)
async def get_status(service: EmergencyService = Depends(get_emergency_service)):
    """获取服务状态"""
    try:
        status = await service.get_service_status()
        return APIResponse(
            success=True,
            message="服务状态获取成功",
            data=status
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取服务状态失败: {str(e)}")

@app.post("/rescue-plan", response_model=APIResponse)
async def generate_rescue_plan(
    request: RescuePlanRequest,
    service: EmergencyService = Depends(get_emergency_service)
):
    """生成救援方案"""
    try:
        rescue_plan = await service.generate_rescue_plan(request)
        return APIResponse(
            success=True,
            message="救援方案生成成功",
            data=rescue_plan.model_dump()
        )
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except TimeoutError as e:
        raise HTTPException(status_code=408, detail=str(e))
    except ExternalServiceError as e:
        raise HTTPException(status_code=502, detail=str(e))
    except ServiceError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        logger.error(f"生成救援方案异常: {str(e)}")
        raise HTTPException(status_code=500, detail="生成救援方案失败")

# 启动和关闭事件
@app.on_event("startup")
async def startup_event():
    """应用启动事件"""
    logger.info("应急服务启动中...")
    try:
        health = await emergency_service.check_health()
        if health.overall_status in ["healthy", "degraded"]:
            logger.info("应急服务启动成功")
        else:
            logger.warning("应急服务启动，但部分依赖服务不可用")
    except Exception as e:
        logger.error(f"应急服务启动失败: {str(e)}")

@app.on_event("shutdown")
async def shutdown_event():
    """应用关闭事件"""
    logger.info("应急服务关闭中...")
    logger.info("应急服务已关闭")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
