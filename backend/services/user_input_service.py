#!/usr/bin/env python3
"""
用户输入服务
提供用户交互界面API，处理用户输入数据，与应急服务对接
端口：8006
依赖：所有其他服务
"""

import asyncio
import logging
import sys
import json
import uuid
from typing import List, Dict, Any, Optional, Union
from datetime import datetime, timedelta
from pathlib import Path

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
    APIResponse, ErrorResponse, PaginationParams, PaginatedResponse, UserInput
)
from shared.service_registry import ServiceRegistry

# 配置日志
logger = logging.getLogger(__name__)

# 数据模型
class UserInputRequest(BaseModel):
    """用户输入请求模型"""
    items: List[Item] = Field(..., description="物品列表", min_length=1, max_length=50)
    environment: Environment = Field(..., description="环境信息")
    additional_info: Optional[str] = Field(None, description="附加信息", max_length=1000)
    urgency_level: str = Field(default="中", description="紧急程度")
    contact_info: Optional[Dict[str, Any]] = Field(None, description="联系信息")
    user_id: Optional[str] = Field(None, description="用户ID")
    
    @field_validator('items')
    @classmethod
    def validate_items(cls, v):
        if not v:
            raise ValueError('物品列表不能为空')
        return v

class InputSuggestion(BaseModel):
    """输入建议模型"""
    type: str = Field(..., description="建议类型")
    value: str = Field(..., description="建议值")
    confidence: float = Field(..., description="置信度", ge=0.0, le=1.0)
    description: Optional[str] = Field(None, description="描述")

class InputValidationResult(BaseModel):
    """输入验证结果模型"""
    is_valid: bool = Field(..., description="是否有效")
    errors: List[str] = Field(default_factory=list, description="错误信息")
    warnings: List[str] = Field(default_factory=list, description="警告信息")
    suggestions: List[InputSuggestion] = Field(default_factory=list, description="建议")

class UserInputHistory(BaseModel):
    """用户输入历史模型"""
    id: str = Field(..., description="记录ID")
    user_id: str = Field(..., description="用户ID")
    input_data: UserInputRequest = Field(..., description="输入数据")
    rescue_plan_id: Optional[str] = Field(None, description="救援方案ID")
    status: str = Field(..., description="状态")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")

class ServiceHealth(BaseModel):
    """服务健康状态模型"""
    service_name: str = Field(..., description="服务名称")
    status: str = Field(..., description="状态")
    response_time: float = Field(..., description="响应时间(毫秒)")
    last_check: datetime = Field(default_factory=datetime.now, description="最后检查时间")
    error_message: Optional[str] = Field(None, description="错误信息")

class UserInputServiceHealth(BaseModel):
    """用户输入服务健康状态"""
    overall_status: str = Field(..., description="整体状态")
    services: List[ServiceHealth] = Field(..., description="各服务状态")
    total_services: int = Field(..., description="总服务数")
    healthy_services: int = Field(..., description="健康服务数")
    last_check: datetime = Field(default_factory=datetime.now, description="最后检查时间")

class UserInputService:
    """用户输入服务类"""
    
    def __init__(self):
        self.config = get_config()
        self.http_client = None
        self.service_registry = ServiceRegistry()
        self.input_history: Dict[str, UserInputHistory] = {}
        self.suggestions_cache: Dict[str, List[InputSuggestion]] = {}
        self._initialize_http_client()
    
    def _initialize_http_client(self):
        """初始化HTTP客户端"""
        try:
            timeout = httpx.Timeout(30.0, connect=10.0)
            self.http_client = AsyncClient(timeout=timeout)
            logger.info("HTTP客户端初始化成功")
        except Exception as e:
            logger.error(f"HTTP客户端初始化失败: {str(e)}")
            self.http_client = None
    
    async def check_service_health(self, service_name: str) -> ServiceHealth:
        """检查单个服务健康状态"""
        start_time = datetime.now()
        try:
            health_url = self.service_registry.get_health_check_url(service_name)
            response = await self.http_client.get(health_url)
            response_time = (datetime.now() - start_time).total_seconds() * 1000
            
            if response.status_code == 200:
                return ServiceHealth(
                    service_name=service_name,
                    status="healthy",
                    response_time=response_time,
                    last_check=datetime.now()
                )
            else:
                return ServiceHealth(
                    service_name=service_name,
                    status="unhealthy",
                    response_time=response_time,
                    last_check=datetime.now(),
                    error_message=f"HTTP {response.status_code}"
                )
        except TimeoutException:
            response_time = (datetime.now() - start_time).total_seconds() * 1000
            return ServiceHealth(
                service_name=service_name,
                status="timeout",
                response_time=response_time,
                last_check=datetime.now(),
                error_message="连接超时"
            )
        except Exception as e:
            response_time = (datetime.now() - start_time).total_seconds() * 1000
            return ServiceHealth(
                service_name=service_name,
                status="error",
                response_time=response_time,
                last_check=datetime.now(),
                error_message=str(e)
            )
    
    async def check_all_services_health(self) -> UserInputServiceHealth:
        """检查所有服务健康状态"""
        try:
            # 需要检查的服务列表
            services_to_check = [
                "emergency_service",
                "knowledge_graph", 
                "rag_service",
                "ollama_service",
                "cache_service",
                "user_service"
            ]
            
            # 并行检查所有服务
            health_tasks = [
                self.check_service_health(service_name) 
                for service_name in services_to_check
            ]
            service_healths = await asyncio.gather(*health_tasks, return_exceptions=True)
            
            # 处理结果
            services = []
            healthy_count = 0
            
            for i, health in enumerate(service_healths):
                if isinstance(health, Exception):
                    service_name = services_to_check[i]
                    health = ServiceHealth(
                        service_name=service_name,
                        status="error",
                        response_time=0.0,
                        last_check=datetime.now(),
                        error_message=str(health)
                    )
                
                services.append(health)
                if health.status == "healthy":
                    healthy_count += 1
            
            # 确定整体状态
            if healthy_count == len(services):
                overall_status = "healthy"
            elif healthy_count > len(services) // 2:
                overall_status = "degraded"
            else:
                overall_status = "unhealthy"
            
            return UserInputServiceHealth(
                overall_status=overall_status,
                services=services,
                total_services=len(services),
                healthy_services=healthy_count,
                last_check=datetime.now()
            )
            
        except Exception as e:
            logger.error(f"检查服务健康状态失败: {str(e)}")
            return UserInputServiceHealth(
                overall_status="error",
                services=[],
                total_services=0,
                healthy_services=0,
                last_check=datetime.now()
            )
    
    async def validate_input(self, input_data: UserInputRequest) -> InputValidationResult:
        """验证用户输入数据"""
        errors = []
        warnings = []
        suggestions = []
        
        try:
            # 验证物品列表
            if not input_data.items:
                errors.append("物品列表不能为空")
            elif len(input_data.items) > 50:
                errors.append("物品数量不能超过50个")
            
            # 验证环境信息
            if not input_data.environment:
                errors.append("环境信息不能为空")
            else:
                if input_data.environment.occupancy and input_data.environment.occupancy > 10000:
                    warnings.append("人员数量过多，请确认数据准确性")
                
                if input_data.environment.exits < 1:
                    errors.append("出口数量至少为1")
                elif input_data.environment.exits > 20:
                    warnings.append("出口数量过多，请确认数据准确性")
            
            # 验证紧急程度
            valid_urgency_levels = ["低", "中", "高", "紧急"]
            if input_data.urgency_level not in valid_urgency_levels:
                errors.append(f"紧急程度必须是以下之一: {', '.join(valid_urgency_levels)}")
            
            # 验证附加信息长度
            if input_data.additional_info and len(input_data.additional_info) > 1000:
                errors.append("附加信息长度不能超过1000字符")
            
            # 生成建议
            suggestions = await self._generate_input_suggestions(input_data)
            
            return InputValidationResult(
                is_valid=len(errors) == 0,
                errors=errors,
                warnings=warnings,
                suggestions=suggestions
            )
            
        except Exception as e:
            logger.error(f"输入验证失败: {str(e)}")
            return InputValidationResult(
                is_valid=False,
                errors=[f"验证过程出错: {str(e)}"],
                warnings=[],
                suggestions=[]
            )
    
    async def _generate_input_suggestions(self, input_data: UserInputRequest) -> List[InputSuggestion]:
        """生成输入建议"""
        suggestions = []
        
        try:
            # 基于物品材质生成建议
            materials = [item.material.value for item in input_data.items]
            material_counts = {}
            for material in materials:
                material_counts[material] = material_counts.get(material, 0) + 1
            
            # 建议添加常见材质
            common_materials = ["木质", "金属", "塑料", "玻璃", "布料"]
            for material in common_materials:
                if material not in material_counts:
                    suggestions.append(InputSuggestion(
                        type="material",
                        value=material,
                        confidence=0.7,
                        description=f"考虑添加{material}物品"
                    ))
            
            # 基于环境类型生成建议
            if input_data.environment.type.value == "室内":
                if not input_data.environment.ventilation or input_data.environment.ventilation.value == "很差":
                    suggestions.append(InputSuggestion(
                        type="environment",
                        value="改善通风",
                        confidence=0.9,
                        description="室内环境通风较差，建议改善通风条件"
                    ))
            
            # 基于紧急程度生成建议
            if input_data.urgency_level == "低":
                suggestions.append(InputSuggestion(
                    type="urgency",
                    value="提高紧急程度",
                    confidence=0.6,
                    description="当前紧急程度较低，请确认是否需要提高"
                ))
            
            return suggestions
            
        except Exception as e:
            logger.error(f"生成输入建议失败: {str(e)}")
            return []
    
    async def submit_rescue_request(self, input_data: UserInputRequest) -> RescuePlan:
        """提交救援请求"""
        try:
            # 验证输入
            validation_result = await self.validate_input(input_data)
            if not validation_result.is_valid:
                raise ValidationError(f"输入验证失败: {', '.join(validation_result.errors)}")
            
            # 创建救援方案请求
            rescue_request = RescuePlanRequest(
                items=input_data.items,
                environment=input_data.environment,
                additional_info=input_data.additional_info,
                urgency_level=input_data.urgency_level,
                contact_info=input_data.contact_info,
                user_id=input_data.user_id
            )
            
            # 调用应急服务
            emergency_service_url = self.service_registry.get_service_url("emergency_service")
            response = await self.http_client.post(
                f"{emergency_service_url}/rescue-plan",
                json=rescue_request.model_dump()
            )
            
            if response.status_code != 200:
                raise ExternalServiceError("emergency_service", f"应急服务返回错误: {response.status_code}")
            
            response_data = response.json()
            if not response_data.get("success", False):
                raise ExternalServiceError("emergency_service", f"应急服务处理失败: {response_data.get('message', '未知错误')}")
            
            # 解析救援方案
            plan_data = response_data.get("data", {})
            rescue_plan = RescuePlan(**plan_data)
            
            # 保存输入历史
            if input_data.user_id:
                history_id = str(uuid.uuid4())
                history_record = UserInputHistory(
                    id=history_id,
                    user_id=input_data.user_id,
                    input_data=input_data,
                    rescue_plan_id=rescue_plan.id,
                    status="completed",
                    created_at=datetime.now(),
                    updated_at=datetime.now()
                )
                self.input_history[history_id] = history_record
            
            return rescue_plan
            
        except ValidationError:
            raise
        except ExternalServiceError:
            raise
        except Exception as e:
            logger.error(f"提交救援请求失败: {str(e)}")
            raise ServiceError("user_input_service", f"提交救援请求失败: {str(e)}")
    
    async def get_input_suggestions(self, partial_input: str, input_type: str) -> List[InputSuggestion]:
        """获取输入建议"""
        try:
            cache_key = f"{input_type}:{partial_input}"
            
            # 检查缓存
            if cache_key in self.suggestions_cache:
                return self.suggestions_cache[cache_key]
            
            suggestions = []
            
            if input_type == "material":
                # 材质建议
                material_suggestions = [
                    "木质", "金属", "塑料", "玻璃", "陶瓷", "布料", "皮革", "电子", "化学", "其他"
                ]
                for material in material_suggestions:
                    if partial_input.lower() in material.lower():
                        suggestions.append(InputSuggestion(
                            type="material",
                            value=material,
                            confidence=0.8,
                            description=f"材质: {material}"
                        ))
            
            elif input_type == "environment_type":
                # 环境类型建议
                env_types = ["室内", "室外", "半室外"]
                for env_type in env_types:
                    if partial_input.lower() in env_type.lower():
                        suggestions.append(InputSuggestion(
                            type="environment_type",
                            value=env_type,
                            confidence=0.9,
                            description=f"环境类型: {env_type}"
                        ))
            
            elif input_type == "area_type":
                # 区域类型建议
                area_types = ["住宅", "商业", "工业", "公共建筑", "交通工具", "仓库", "实验室", "其他"]
                for area_type in area_types:
                    if partial_input.lower() in area_type.lower():
                        suggestions.append(InputSuggestion(
                            type="area_type",
                            value=area_type,
                            confidence=0.9,
                            description=f"区域类型: {area_type}"
                        ))
            
            # 缓存建议
            self.suggestions_cache[cache_key] = suggestions
            
            return suggestions
            
        except Exception as e:
            logger.error(f"获取输入建议失败: {str(e)}")
            return []
    
    async def get_user_input_history(self, user_id: str, page: int = 1, size: int = 10) -> PaginatedResponse:
        """获取用户输入历史"""
        try:
            # 过滤用户历史记录
            user_histories = [
                history for history in self.input_history.values()
                if history.user_id == user_id
            ]
            
            # 按创建时间倒序排序
            user_histories.sort(key=lambda x: x.created_at, reverse=True)
            
            # 分页
            total = len(user_histories)
            start = (page - 1) * size
            end = start + size
            items = user_histories[start:end]
            
            return PaginatedResponse(
                items=[history.model_dump() for history in items],
                total=total,
                page=page,
                size=size,
                pages=(total + size - 1) // size if total > 0 else 0
            )
            
        except Exception as e:
            logger.error(f"获取用户输入历史失败: {str(e)}")
            raise ServiceError("user_input_service", f"获取用户输入历史失败: {str(e)}")
    
    async def get_input_history_by_id(self, history_id: str) -> Optional[UserInputHistory]:
        """根据ID获取输入历史"""
        return self.input_history.get(history_id)
    
    async def test_connection(self) -> bool:
        """测试服务连接"""
        try:
            # 检查HTTP客户端
            if not self.http_client:
                return False
            
            # 检查应急服务连接
            emergency_service_url = self.service_registry.get_service_url("emergency_service")
            response = await self.http_client.get(f"{emergency_service_url}/health")
            return response.status_code == 200
            
        except Exception as e:
            logger.error(f"服务连接测试失败: {str(e)}")
            return False

# 创建服务实例
user_input_service = UserInputService()

# FastAPI应用
app = FastAPI(
    title="用户输入服务",
    description="用户交互界面API，处理用户输入数据，与应急服务对接",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应该限制具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 依赖注入
def get_user_input_service() -> UserInputService:
    return user_input_service

# API路由
@app.get("/", response_model=APIResponse)
async def root():
    """根路径 - 服务信息"""
    return APIResponse(
        success=True,
        message="用户输入服务运行正常",
        data={
            "service": "用户输入服务",
            "version": "1.0.0",
            "description": "用户交互界面API，处理用户输入数据，与应急服务对接",
            "endpoints": {
                "health": "/health",
                "validate": "/validate",
                "submit": "/submit",
                "suggestions": "/suggestions",
                "history": "/history",
                "docs": "/docs"
            }
        }
    )

@app.get("/health", response_model=APIResponse)
async def health_check(service: UserInputService = Depends(get_user_input_service)):
    """健康检查"""
    try:
        health_status = await service.check_all_services_health()
        return APIResponse(
            success=health_status.overall_status in ["healthy", "degraded"],
            message="健康检查完成",
            data=health_status.model_dump()
        )
    except Exception as e:
        return APIResponse(
            success=False,
            message=f"健康检查失败: {str(e)}",
            data={"status": "unhealthy"}
        )

@app.post("/validate", response_model=APIResponse)
async def validate_input(
    input_data: UserInputRequest,
    service: UserInputService = Depends(get_user_input_service)
):
    """验证用户输入"""
    try:
        validation_result = await service.validate_input(input_data)
        return APIResponse(
            success=True,
            message="输入验证完成",
            data=validation_result.model_dump()
        )
    except Exception as e:
        return APIResponse(
            success=False,
            message=f"输入验证失败: {str(e)}",
            data={"is_valid": False, "errors": [str(e)]}
        )

@app.post("/submit", response_model=APIResponse)
async def submit_rescue_request(
    input_data: UserInputRequest,
    service: UserInputService = Depends(get_user_input_service)
):
    """提交救援请求"""
    try:
        rescue_plan = await service.submit_rescue_request(input_data)
        return APIResponse(
            success=True,
            message="救援请求提交成功",
            data=rescue_plan.model_dump()
        )
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except ExternalServiceError as e:
        raise HTTPException(status_code=502, detail=str(e))
    except ServiceError as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/suggestions", response_model=APIResponse)
async def get_input_suggestions(
    partial_input: str = Query(..., description="部分输入"),
    input_type: str = Query(..., description="输入类型"),
    service: UserInputService = Depends(get_user_input_service)
):
    """获取输入建议"""
    try:
        suggestions = await service.get_input_suggestions(partial_input, input_type)
        return APIResponse(
            success=True,
            message="获取建议成功",
            data=[suggestion.model_dump() for suggestion in suggestions]
        )
    except Exception as e:
        return APIResponse(
            success=False,
            message=f"获取建议失败: {str(e)}",
            data=[]
        )

@app.get("/history/{user_id}", response_model=APIResponse)
async def get_user_input_history(
    user_id: str,
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(10, ge=1, le=100, description="每页大小"),
    service: UserInputService = Depends(get_user_input_service)
):
    """获取用户输入历史"""
    try:
        history = await service.get_user_input_history(user_id, page, size)
        return APIResponse(
            success=True,
            message="获取历史记录成功",
            data=history.model_dump()
        )
    except ServiceError as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/history/detail/{history_id}", response_model=APIResponse)
async def get_input_history_detail(
    history_id: str,
    service: UserInputService = Depends(get_user_input_service)
):
    """获取输入历史详情"""
    try:
        history = await service.get_input_history_by_id(history_id)
        if not history:
            raise HTTPException(status_code=404, detail="历史记录不存在")
        
        return APIResponse(
            success=True,
            message="获取历史记录详情成功",
            data=history.model_dump()
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取历史记录详情失败: {str(e)}")

# 启动和关闭事件
@app.on_event("startup")
async def startup_event():
    """应用启动事件"""
    logger.info("用户输入服务启动中...")
    try:
        # 测试连接
        is_healthy = await user_input_service.test_connection()
        if is_healthy:
            logger.info("用户输入服务启动成功")
        else:
            logger.warning("用户输入服务启动，但部分连接异常")
    except Exception as e:
        logger.error(f"用户输入服务启动失败: {str(e)}")

@app.on_event("shutdown")
async def shutdown_event():
    """应用关闭事件"""
    logger.info("用户输入服务关闭中...")
    try:
        # 关闭HTTP客户端
        if user_input_service.http_client:
            await user_input_service.http_client.aclose()
        logger.info("HTTP客户端已关闭")
    except Exception as e:
        logger.error(f"关闭HTTP客户端失败: {str(e)}")
    logger.info("用户输入服务已关闭")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8006)
