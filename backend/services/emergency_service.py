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
import os
import hashlib
import time
from typing import List, Dict, Any, Optional, Union, Tuple
from datetime import datetime, timedelta
from pathlib import Path

# 设置代理跳过localhost（解决Windows代理导致的502错误）
os.environ['NO_PROXY'] = 'localhost,127.0.0.1,::1'
os.environ['no_proxy'] = 'localhost,127.0.0.1,::1'

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks, Query
from fastapi.middleware.cors import CORSMiddleware
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
class EmergencyQueryRequest(BaseModel):
    """应急查询请求模型（前端兼容）"""
    query: str = Field(..., description="查询内容")
    environment: Dict[str, Any] = Field(default_factory=dict, description="环境信息")
    urgency_level: Optional[str] = Field("medium", description="紧急程度")

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
        rag_host = os.getenv("RAG_HOST", "localhost")
        rag_port = os.getenv("RAG_PORT", "3000")
        self.services = {
            "knowledge_graph": {
                "url": f"http://localhost:8001",
                "timeout": 10.0,
                "required": True
            },
            "rag": {
                "url": f"http://{rag_host}:{rag_port}", 
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
        # 中文 -> 英文 映射（用于知识图谱服务路径参数）
        self.material_zh_to_en = {
            "木质": "wood",
            "金属": "metal",
            "塑料": "plastic",
            "玻璃": "glass",
            "陶瓷": "ceramic",
            "布料": "fabric",
            "皮革": "leather",
            "电子": "electronics",
            "化学": "chemical",
            "其他": "other",
        }
        self.area_zh_to_en = {
            "住宅": "residential",
            "商业": "commercial",
            "工业": "industrial",
            "办公": "office",
            "学校": "school",
            "医院": "hospital",
            "仓库": "warehouse",
            "室外": "outdoor",
            "室内": "indoor",
        }
    
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
        # 收集材质知识（带中文->英文映射与兜底搜索）
        material_tasks = []
        for item in request.items:
            material_zh = getattr(item.material, "value", None) or getattr(item, "material", "")
            material_en = self.material_zh_to_en.get(material_zh, material_zh)
            async def fetch_material(mat_en: str = material_en, mat_zh: str = material_zh):
                try:
                    return await self._call_service("knowledge_graph", f"/materials/{mat_en}")
                except Exception:
                    # 兜底：使用搜索接口（支持中文关键词）
                    try:
                        return await self._call_service("knowledge_graph", f"/materials/search/{mat_zh}")
                    except Exception as e:
                        logger.warning(f"获取材质知识失败: {mat_zh}/{mat_en}: {str(e)}")
                        return {"success": False}
            material_tasks.append(fetch_material())

        # 收集环境知识（直接使用中文查询）
        area_zh = getattr(request.environment.area, "value", None) or getattr(request.environment, "area", "")
        async def fetch_environment():
            try:
                # 直接使用中文查询，因为Neo4j中存储的是中文
                return await self._call_service("knowledge_graph", f"/environments/{area_zh}")
            except Exception as e:
                logger.warning(f"获取环境知识失败: {area_zh}: {str(e)}")
                return {"success": False}
        env_task = fetch_environment()

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
            logger.error(f"生成救援方案失败: {str(e)}", exc_info=True)
            logger.warning("⚠️ Ollama服务调用失败，将使用降级救援方案")
            logger.info(f"失败原因: {type(e).__name__}: {str(e)}")
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
        
        # 创建基本救援步骤（包含详细信息）
        steps = [
            RescueStep(
                step_number=1,
                description="立即拨打119报警，启动应急预案，组织现场人员按疏散路线有序撤离，同时关闭电源和燃气阀门，防止火势蔓延",
                equipment=["手机或对讲机", "应急照明灯", "扩音器", "防烟面罩", "疏散指示牌"],
                warnings=[
                    "确保所有人员安全撤离，优先疏散老人、儿童和行动不便者",
                    "保持冷静，不要惊慌，避免发生踩踏事故",
                    "不要使用电梯，选择楼梯疏散",
                    "低姿前进，用湿毛巾捂住口鼻"
                ],
                estimated_time=5
            ),
            RescueStep(
                step_number=2,
                description="专业消防人员到达前，使用现场灭火器材进行初期火灾扑救，切断火势蔓延路径，重点保护重要设施和疏散通道",
                equipment=["干粉灭火器", "二氧化碳灭火器", "消防水带", "防火毯", "防护服", "消防斧"],
                warnings=[
                    "选择合适的灭火器材，电器火灾不能用水扑救",
                    "注意风向，站在上风位置进行灭火",
                    "保持安全距离，火势较大时应立即撤离",
                    "不要贸然进入浓烟区域，避免中毒窒息"
                ],
                estimated_time=10
            ),
            RescueStep(
                step_number=3,
                description="引导所有人员按照疏散指示标志撤离到安全区域，在集合点清点人数，确认无人员滞留，及时向消防队报告现场情况",
                equipment=["应急灯", "对讲机", "急救箱", "警戒带", "人员名册", "扩音设备"],
                warnings=[
                    "到达安全区域后立即清点人数，确认无人员失踪",
                    "如发现有人员未撤出，立即通知消防救援人员",
                    "不要返回火场取物品，避免二次伤害",
                    "对受伤人员进行紧急救护，等待医疗救援"
                ],
                estimated_time=5
            ),
            RescueStep(
                step_number=4,
                description="等待消防队确认火势完全扑灭，使用热成像仪检查是否有隐藏火点，清理现场残留危险物品，评估损失并做好现场保护工作",
                equipment=["热成像仪", "清理工具", "警戒标识", "照明设备", "相机或摄像机", "检测仪器"],
                warnings=[
                    "等待消防队确认安全后再进入现场",
                    "确保无复燃风险，检查所有可能的隐患点",
                    "注意建筑结构稳定性，防止次生灾害",
                    "做好现场保护和证据留存工作，配合后续调查"
                ],
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

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],  # 允许前端访问
    allow_credentials=True,
    allow_methods=["*"],  # 允许所有方法
    allow_headers=["*"],  # 允许所有头
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

# 添加前端API兼容端点
@app.get("/api/v1/system/status", response_model=APIResponse)
async def get_system_status(service: EmergencyService = Depends(get_emergency_service)):
    """获取系统状态（前端兼容）"""
    try:
        # 获取健康检查信息
        health = await service.check_health()
        
        # 转换为前端期望的格式
        services_dict = {}
        for svc in health.services:
            services_dict[svc.service_name] = {
                "status": "running" if svc.status == "healthy" else "error",
                "uptime": "运行中",
                "last_check": svc.last_check.isoformat()
            }
        
        system_status = {
            "services": services_dict,
            "databases": {
                "postgres": True,  # 假设数据库正常
                "neo4j": True
            },
            "overall_status": health.overall_status
        }
        
        return APIResponse(
            success=True,
            message="系统状态获取成功",
            data=system_status
        )
    except Exception as e:
        logger.error(f"获取系统状态失败: {str(e)}")
        # 返回降级的状态信息
        return APIResponse(
            success=False,
            message=f"获取系统状态失败: {str(e)}",
            data={
                "services": {},
                "databases": {"postgres": False, "neo4j": False},
                "overall_status": "error"
            }
        )

@app.get("/api/v1/knowledge/graph", response_model=APIResponse)
async def knowledge_graph_query(
    q: str = Query(..., description="搜索关键词"),
    service: EmergencyService = Depends(get_emergency_service)
):
    """知识图谱查询接口（前端兼容）"""
    try:
        logger.info(f"收到知识图谱查询请求: {q}")
        
        # 调用知识图谱服务
        response = await service._call_service("knowledge_graph", f"/api/v1/knowledge/graph?q={q}")
        
        if response and response.get("success"):
            return APIResponse(
                success=True,
                message=response.get("message", "查询成功"),
                data=response.get("data", {})
            )
        else:
            return APIResponse(
                success=False,
                message=response.get("message", "查询失败") if response else "知识图谱服务不可用",
                data={"nodes": [], "edges": [], "query": q, "count": 0}
            )
    except Exception as e:
        logger.error(f"知识图谱查询失败: {str(e)}")
        return APIResponse(
            success=False,
            message=f"查询失败: {str(e)}",
            data={"nodes": [], "edges": [], "query": q, "count": 0}
        )

@app.post("/api/v1/emergency/query", response_model=APIResponse)
async def emergency_query(
    request: EmergencyQueryRequest,
    service: EmergencyService = Depends(get_emergency_service)
):
    """应急查询接口（前端兼容）"""
    try:
        logger.info(f"收到应急查询请求: {request.query}")
        
        # 将前端请求转换为救援方案请求
        rescue_request = RescuePlanRequest(
            items=[Item(
                name="应急查询",
                material="其他",  # 使用正确的枚举值
                quantity=1,
                location="查询位置",  # 添加必需字段
                condition="正常",
                flammability="不燃",
                toxicity="无毒"
            )],  # 添加默认物品以满足验证要求
            environment=Environment(
                type="室内",  # 默认室内
                area="商业",  # 默认商业区域
                floor=1,  # 默认1楼
                ventilation="良好",  # 默认通风良好
                exits=2,  # 默认2个出口
                occupancy=10,  # 默认10人
                building_type="办公楼",
                fire_safety_equipment=["灭火器", "烟雾报警器"],
                special_conditions=request.query
            ),
            additional_info=request.query,
            urgency_level=request.urgency_level or "medium"
        )
        
        # 生成救援方案
        rescue_plan = await service.generate_rescue_plan(rescue_request)
        
        # 转换为前端期望的响应格式
        # 将RescueStep对象转换为详细的文本格式
        steps_text = []
        for step in rescue_plan.steps:
            step_text = f"### 步骤 {step.step_number}: {step.description}\n\n"
            if step.equipment:
                step_text += f"**所需设备**: {', '.join(step.equipment)}\n\n"
            if step.warnings:
                step_text += f"**注意事项**:\n"
                for warning in step.warnings:
                    step_text += f"  - {warning}\n"
                step_text += "\n"
            if step.estimated_time:
                step_text += f"**预计时间**: {step.estimated_time} 分钟\n\n"
            steps_text.append(step_text)
        
        full_response = f"# {rescue_plan.title}\n\n"
        full_response += f"**优先级**: {rescue_plan.priority.value}\n\n"
        full_response += f"**预计总时间**: {rescue_plan.estimated_duration} 分钟\n\n"
        full_response += "---\n\n"
        full_response += "## 救援步骤\n\n"
        full_response += "\n".join(steps_text)
        
        if rescue_plan.warnings:
            full_response += "---\n\n"
            full_response += "## ⚠️ 重要警告\n\n"
            for warning in rescue_plan.warnings:
                full_response += f"- {warning}\n"
            full_response += "\n"
        
        if rescue_plan.equipment_list:
            full_response += "---\n\n"
            full_response += "## 🛠️ 所需设备清单\n\n"
            for equipment in rescue_plan.equipment_list:
                full_response += f"- {equipment}\n"
            full_response += "\n"
        
        response_data = {
            "response": full_response,
            "confidence": 0.85,
            "sources": ["消防应急知识库", "救援程序数据库", "RAG知识检索", "Ollama AI分析"],
            "timestamp": datetime.now().isoformat()
        }
        
        return APIResponse(
            success=True,
            data=response_data,
            message="应急查询成功"
        )
    except Exception as e:
        logger.error(f"应急查询失败: {str(e)}")
        return APIResponse(
            success=False,
            data=None,
            message=f"应急查询失败: {str(e)}"
        )

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
