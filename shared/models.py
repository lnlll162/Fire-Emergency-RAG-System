"""
火灾应急救援RAG系统 - 统一数据模型
定义系统中所有服务使用的统一数据模型
"""

from pydantic import BaseModel, Field, field_validator
from typing import List, Optional, Dict, Any, Union
from datetime import datetime
from enum import Enum
import uuid


class ItemMaterial(str, Enum):
    """材质枚举"""
    WOOD = "木质"
    METAL = "金属"
    PLASTIC = "塑料"
    GLASS = "玻璃"
    CERAMIC = "陶瓷"
    FABRIC = "布料"
    LEATHER = "皮革"
    ELECTRONIC = "电子"
    CHEMICAL = "化学"
    OTHER = "其他"


class FlammabilityLevel(str, Enum):
    """易燃性等级"""
    NON_FLAMMABLE = "不燃"
    DIFFICULT_FLAMMABLE = "难燃"
    FLAMMABLE = "易燃"
    HIGHLY_FLAMMABLE = "极易燃"


class ToxicityLevel(str, Enum):
    """毒性等级"""
    NON_TOXIC = "无毒"
    LOW_TOXIC = "低毒"
    MEDIUM_TOXIC = "中毒"
    HIGH_TOXIC = "高毒"
    EXTREMELY_TOXIC = "剧毒"


class EnvironmentType(str, Enum):
    """环境类型枚举"""
    INDOOR = "室内"
    OUTDOOR = "室外"
    SEMI_OUTDOOR = "半室外"


class AreaType(str, Enum):
    """区域类型枚举"""
    RESIDENTIAL = "住宅"
    COMMERCIAL = "商业"
    INDUSTRIAL = "工业"
    PUBLIC_BUILDING = "公共建筑"
    VEHICLE = "交通工具"
    WAREHOUSE = "仓库"
    LABORATORY = "实验室"
    OTHER = "其他"


class VentilationLevel(str, Enum):
    """通风等级枚举"""
    EXCELLENT = "良好"
    GOOD = "一般"
    POOR = "较差"
    VERY_POOR = "很差"


class PriorityLevel(str, Enum):
    """优先级枚举"""
    LOW = "低"
    MEDIUM = "中"
    HIGH = "高"
    URGENT = "紧急"


class Item(BaseModel):
    """统一物品模型"""
    name: str = Field(..., description="物品名称", min_length=1, max_length=100)
    material: ItemMaterial = Field(..., description="材质")
    quantity: int = Field(..., description="数量", ge=1, le=1000)
    location: str = Field(..., description="位置", min_length=1, max_length=100)
    condition: Optional[str] = Field(None, description="状态", max_length=50)
    flammability: Optional[FlammabilityLevel] = Field(None, description="易燃性")
    toxicity: Optional[ToxicityLevel] = Field(None, description="毒性")
    size: Optional[Dict[str, Any]] = Field(None, description="尺寸信息")
    weight: Optional[Dict[str, Any]] = Field(None, description="重量信息")
    
    @field_validator('name')
    @classmethod
    def validate_name(cls, v):
        if not v.strip():
            raise ValueError('物品名称不能为空')
        return v.strip()
    
    @field_validator('location')
    @classmethod
    def validate_location(cls, v):
        if not v.strip():
            raise ValueError('位置不能为空')
        return v.strip()


class Environment(BaseModel):
    """统一环境模型"""
    type: EnvironmentType = Field(..., description="环境类型")
    area: AreaType = Field(..., description="区域类型")
    floor: Optional[int] = Field(None, description="楼层", ge=-10, le=200)
    ventilation: VentilationLevel = Field(..., description="通风情况")
    exits: int = Field(..., description="出口数量", ge=1, le=20)
    occupancy: Optional[int] = Field(None, description="人员数量", ge=0, le=10000)
    building_type: Optional[str] = Field(None, description="建筑类型", max_length=100)
    fire_safety_equipment: Optional[List[str]] = Field(None, description="消防设备")
    special_conditions: Optional[str] = Field(None, description="特殊条件", max_length=500)


class RescueStep(BaseModel):
    """救援步骤模型"""
    step_number: int = Field(..., description="步骤编号", ge=1)
    description: str = Field(..., description="步骤描述", min_length=1, max_length=500)
    equipment: List[str] = Field(default_factory=list, description="所需设备")
    warnings: List[str] = Field(default_factory=list, description="注意事项")
    estimated_time: Optional[int] = Field(None, description="预计时间(分钟)", ge=1, le=1440)
    
    @field_validator('description')
    @classmethod
    def validate_description(cls, v):
        if not v.strip():
            raise ValueError('步骤描述不能为空')
        return v.strip()


class RescuePlan(BaseModel):
    """救援方案模型"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="方案ID")
    title: str = Field(..., description="方案标题", min_length=1, max_length=200)
    priority: PriorityLevel = Field(..., description="优先级")
    status: str = Field(default="active", description="状态")
    steps: List[RescueStep] = Field(..., description="救援步骤", min_length=1)
    equipment_list: List[str] = Field(..., description="设备清单")
    warnings: List[str] = Field(..., description="总体警告")
    estimated_duration: int = Field(..., description="预计总时长(分钟)", ge=1, le=1440)
    created_at: datetime = Field(default_factory=datetime.utcnow, description="创建时间")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="更新时间")
    
    @field_validator('title')
    @classmethod
    def validate_title(cls, v):
        if not v.strip():
            raise ValueError('方案标题不能为空')
        return v.strip()
    
    @field_validator('steps')
    @classmethod
    def validate_steps(cls, v):
        if not v:
            raise ValueError('救援步骤不能为空')
        # 验证步骤编号是否连续
        step_numbers = [step.step_number for step in v]
        if step_numbers != list(range(1, len(step_numbers) + 1)):
            raise ValueError('步骤编号必须从1开始连续递增')
        return v


class RescuePlanRequest(BaseModel):
    """统一救援方案请求模型"""
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


class User(BaseModel):
    """用户模型"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="用户ID")
    username: str = Field(..., description="用户名", min_length=3, max_length=50)
    email: str = Field(..., description="邮箱", pattern=r'^[^@]+@[^@]+\.[^@]+$')
    full_name: Optional[str] = Field(None, description="全名", max_length=100)
    role: str = Field(default="user", description="角色")
    is_active: bool = Field(default=True, description="是否激活")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="创建时间")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="更新时间")


class UserInput(BaseModel):
    """用户输入记录模型"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="记录ID")
    user_id: str = Field(..., description="用户ID")
    rescue_plan_id: Optional[str] = Field(None, description="救援方案ID")
    items: List[Item] = Field(..., description="物品列表")
    environment: Environment = Field(..., description="环境信息")
    additional_info: Optional[str] = Field(None, description="附加信息")
    urgency_level: str = Field(default="中", description="紧急程度")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="创建时间")


class SystemLog(BaseModel):
    """系统日志模型"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="日志ID")
    service_name: str = Field(..., description="服务名称", max_length=50)
    level: str = Field(..., description="日志级别", max_length=20)
    message: str = Field(..., description="日志消息", min_length=1)
    metadata: Optional[Dict[str, Any]] = Field(None, description="元数据")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="创建时间")


# API响应模型
class APIResponse(BaseModel):
    """统一API响应模型"""
    success: bool = Field(..., description="是否成功")
    message: str = Field(..., description="响应消息")
    data: Optional[Any] = Field(None, description="响应数据")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="时间戳")


class ErrorResponse(BaseModel):
    """错误响应模型"""
    error: str = Field(..., description="错误类型")
    message: str = Field(..., description="错误消息")
    details: Optional[Dict[str, Any]] = Field(None, description="错误详情")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="时间戳")


# 分页模型
class PaginationParams(BaseModel):
    """分页参数模型"""
    page: int = Field(default=1, description="页码", ge=1)
    size: int = Field(default=10, description="每页大小", ge=1, le=100)
    
    @property
    def offset(self) -> int:
        return (self.page - 1) * self.size


class PaginatedResponse(BaseModel):
    """分页响应模型"""
    items: List[Any] = Field(..., description="数据列表")
    total: int = Field(..., description="总数量")
    page: int = Field(..., description="当前页码")
    size: int = Field(..., description="每页大小")
    pages: int = Field(..., description="总页数")
    
    @field_validator('pages', mode='before')
    @classmethod
    def calculate_pages(cls, v, info):
        if v is not None:
            return v
        values = info.data
        total = values.get('total', 0)
        size = values.get('size', 10)
        return (total + size - 1) // size if total > 0 else 0
