#!/usr/bin/env python3
"""
Ollama服务
提供基于Ollama的AI生成功能，包括救援方案生成、模型状态管理等
"""

import asyncio
import logging
import sys
import json
import hashlib
import os
from typing import List, Dict, Any, Optional, Union
from datetime import datetime, timedelta
from pathlib import Path

# 设置代理跳过localhost（解决Windows代理导致的502错误）
os.environ['NO_PROXY'] = 'localhost,127.0.0.1,::1'
os.environ['no_proxy'] = 'localhost,127.0.0.1,::1'

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from pydantic import BaseModel, Field
import httpx
import redis
from redis.exceptions import RedisError

from shared.config import get_config
from shared.exceptions import ExternalServiceError, TimeoutError, ServiceError
from shared.models import RescuePlan, RescuePlanRequest, Item, Environment, RescueStep, PriorityLevel

# 配置日志
logger = logging.getLogger(__name__)

# 数据模型
class ModelInfo(BaseModel):
    """模型信息"""
    name: str = Field(..., description="模型名称")
    size: Optional[int] = Field(None, description="模型大小(字节)")
    digest: Optional[str] = Field(None, description="模型摘要")
    modified_at: Optional[datetime] = Field(None, description="修改时间")
    family: Optional[str] = Field(None, description="模型系列")
    format: Optional[str] = Field(None, description="模型格式")
    families: Optional[List[str]] = Field(None, description="模型系列列表")
    parameter_size: Optional[str] = Field(None, description="参数量")
    quantization_level: Optional[str] = Field(None, description="量化级别")

class ModelStatus(BaseModel):
    """模型状态"""
    name: str = Field(..., description="模型名称")
    loaded: bool = Field(..., description="是否已加载")
    loading: bool = Field(default=False, description="是否正在加载")
    error: Optional[str] = Field(None, description="错误信息")
    last_used: Optional[datetime] = Field(None, description="最后使用时间")
    memory_usage: Optional[int] = Field(None, description="内存使用量(字节)")

class GenerationRequest(BaseModel):
    """生成请求"""
    prompt: str = Field(..., description="提示词", min_length=1, max_length=10000)
    model: Optional[str] = Field(None, description="指定模型名称")
    temperature: float = Field(default=0.7, ge=0.0, le=2.0, description="温度参数")
    top_p: float = Field(default=0.9, ge=0.0, le=1.0, description="Top-p参数")
    max_tokens: int = Field(default=2048, ge=1, le=8192, description="最大生成token数")
    stream: bool = Field(default=False, description="是否流式输出")
    context: Optional[Dict[str, Any]] = Field(None, description="上下文信息")

class GenerationResponse(BaseModel):
    """生成响应"""
    response: str = Field(..., description="生成的文本")
    model: str = Field(..., description="使用的模型")
    created_at: datetime = Field(default_factory=datetime.now, description="创建时间")
    tokens_used: Optional[int] = Field(None, description="使用的token数")
    generation_time: float = Field(..., description="生成耗时(秒)")
    cached: bool = Field(default=False, description="是否来自缓存")

class RescuePlanGenerationRequest(BaseModel):
    """救援方案生成请求"""
    items: List[Item] = Field(..., description="物品列表", min_items=1, max_items=50)
    environment: Environment = Field(..., description="环境信息")
    additional_info: Optional[str] = Field(None, description="附加信息", max_length=1000)
    urgency_level: str = Field(default="中", description="紧急程度")
    model: Optional[str] = Field(None, description="指定模型名称")
    temperature: float = Field(default=0.7, ge=0.0, le=2.0, description="温度参数")

class QueryResponse(BaseModel):
    """查询响应"""
    success: bool = Field(..., description="查询是否成功")
    data: Any = Field(..., description="查询结果数据")
    message: str = Field(default="", description="响应消息")
    timestamp: datetime = Field(default_factory=datetime.now, description="响应时间")

class OllamaService:
    """Ollama服务类"""
    
    def __init__(self):
        self.config = get_config()
        self.ollama_url = self.config.database.ollama_url
        self.redis_client = None
        self.current_model = self.config.database.ollama_model  # 使用配置中的模型
        self.model_cache = {}
        self._initialize_redis()
        self._initialize_ollama_connection()
    
    def _initialize_redis(self):
        """初始化Redis连接"""
        try:
            self.redis_client = redis.Redis(
                host=self.config.database.redis_host,
                port=self.config.database.redis_port,
                password=self.config.database.redis_password,
                db=self.config.database.redis_db,
                decode_responses=True
            )
            # 测试连接
            self.redis_client.ping()
            logger.info("Redis连接初始化成功")
        except Exception as e:
            logger.warning(f"Redis连接初始化失败: {str(e)}")
            self.redis_client = None
    
    def _initialize_ollama_connection(self):
        """初始化Ollama连接"""
        try:
            # 测试Ollama连接
            asyncio.run(self._test_ollama_connection())
            logger.info("Ollama连接初始化成功")
        except Exception as e:
            logger.error(f"Ollama连接初始化失败: {str(e)}")
            raise ExternalServiceError(f"无法连接到Ollama服务: {str(e)}", "ollama")
    
    async def _test_ollama_connection(self) -> bool:
        """测试Ollama连接"""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(f"{self.ollama_url}/api/tags")
                return response.status_code == 200
        except Exception as e:
            logger.error(f"Ollama连接测试失败: {str(e)}")
            return False
    
    async def test_connection(self) -> bool:
        """测试服务连接"""
        try:
            # 测试Ollama连接
            ollama_ok = await self._test_ollama_connection()
            
            # 测试Redis连接
            redis_ok = False
            if self.redis_client:
                try:
                    self.redis_client.ping()
                    redis_ok = True
                except:
                    pass
            
            return ollama_ok and redis_ok
        except Exception as e:
            logger.error(f"服务连接测试失败: {str(e)}")
            return False
    
    async def list_models(self) -> List[ModelInfo]:
        """获取可用模型列表"""
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(f"{self.ollama_url}/api/tags")
                response.raise_for_status()
                
                data = response.json()
                models = []
                
                for model_data in data.get("models", []):
                    model_info = ModelInfo(
                        name=model_data.get("name", ""),
                        size=model_data.get("size"),
                        digest=model_data.get("digest"),
                        modified_at=datetime.fromisoformat(model_data.get("modified_at", "").replace("Z", "+00:00")) if model_data.get("modified_at") else None,
                        family=model_data.get("family"),
                        format=model_data.get("format"),
                        families=model_data.get("families"),
                        parameter_size=model_data.get("parameter_size"),
                        quantization_level=model_data.get("quantization_level")
                    )
                    models.append(model_info)
                
                return models
        except Exception as e:
            logger.error(f"获取模型列表失败: {str(e)}")
            raise ExternalServiceError(f"获取模型列表失败: {str(e)}", "ollama")
    
    async def get_model_status(self, model_name: str) -> ModelStatus:
        """获取模型状态"""
        try:
            # 检查模型是否在运行
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(
                    f"{self.ollama_url}/api/show",
                    json={"name": model_name}
                )
                
                if response.status_code == 200:
                    data = response.json()
                    return ModelStatus(
                        name=model_name,
                        loaded=True,
                        loading=False,
                        memory_usage=data.get("size"),
                        last_used=datetime.now()
                    )
                else:
                    return ModelStatus(
                        name=model_name,
                        loaded=False,
                        loading=False,
                        error=f"模型状态检查失败: {response.status_code}"
                    )
        except Exception as e:
            logger.error(f"获取模型状态失败: {str(e)}")
            return ModelStatus(
                name=model_name,
                loaded=False,
                loading=False,
                error=str(e)
            )
    
    async def load_model(self, model_name: str) -> bool:
        """加载模型"""
        try:
            async with httpx.AsyncClient(timeout=120.0) as client:
                response = await client.post(
                    f"{self.ollama_url}/api/generate",
                    json={
                        "model": model_name,
                        "prompt": "测试",
                        "stream": False
                    }
                )
                
                if response.status_code == 200:
                    self.current_model = model_name
                    logger.info(f"模型 {model_name} 加载成功")
                    return True
                else:
                    logger.error(f"模型 {model_name} 加载失败: {response.status_code}")
                    return False
        except Exception as e:
            logger.error(f"加载模型失败: {str(e)}")
            return False
    
    def _generate_cache_key(self, request: GenerationRequest) -> str:
        """生成缓存键"""
        # 创建请求的哈希值作为缓存键
        request_data = {
            "prompt": request.prompt,
            "model": request.model or self.current_model,
            "temperature": request.temperature,
            "top_p": request.top_p,
            "max_tokens": request.max_tokens
        }
        request_str = json.dumps(request_data, sort_keys=True)
        return f"ollama:generation:{hashlib.md5(request_str.encode()).hexdigest()}"
    
    async def generate_text(self, request: GenerationRequest) -> GenerationResponse:
        """生成文本"""
        try:
            # 检查缓存
            if self.redis_client:
                cache_key = self._generate_cache_key(request)
                cached_result = self.redis_client.get(cache_key)
                if cached_result:
                    data = json.loads(cached_result)
                    logger.info(f"从缓存返回生成结果: {cache_key}")
                    # 移除cached字段避免重复
                    data.pop('cached', None)
                    return GenerationResponse(**data, cached=True)
            
            # 使用指定模型或当前模型
            model_name = request.model or self.current_model
            if not model_name:
                raise ValueError("未指定模型且当前无可用模型")
            
            start_time = datetime.now()
            
            async with httpx.AsyncClient(timeout=120.0) as client:
                response = await client.post(
                    f"{self.ollama_url}/api/generate",
                    json={
                        "model": model_name,
                        "prompt": request.prompt,
                        "stream": request.stream,
                        "options": {
                            "temperature": request.temperature,
                            "top_p": request.top_p,
                            "num_predict": request.max_tokens
                        }
                    }
                )
                
                response.raise_for_status()
                data = response.json()
                
                end_time = datetime.now()
                generation_time = (end_time - start_time).total_seconds()
                
                result = GenerationResponse(
                    response=data.get("response", ""),
                    model=model_name,
                    tokens_used=data.get("eval_count"),
                    generation_time=generation_time
                )
                
                # 缓存结果（缓存1小时）
                if self.redis_client:
                    cache_key = self._generate_cache_key(request)
                    cache_data = result.model_dump()
                    cache_data["cached"] = False
                    self.redis_client.setex(
                        cache_key,
                        3600,  # 1小时
                        json.dumps(cache_data, default=str)
                    )
                
                return result
                
        except httpx.TimeoutException as e:
            raise TimeoutError(f"生成请求超时: {str(e)}", "ollama", 120.0)
        except httpx.HTTPError as e:
            raise ExternalServiceError(f"生成请求失败: {str(e)}", "ollama")
        except Exception as e:
            logger.error(f"生成文本失败: {str(e)}")
            raise ServiceError(f"生成文本失败: {str(e)}", "ollama_service")
    
    def _build_rescue_plan_prompt(self, request: RescuePlanGenerationRequest) -> str:
        """构建救援方案生成提示词"""
        # 构建物品信息
        items_info = []
        for item in request.items:
            item_desc = f"- {item.name} ({item.material.value})"
            if item.quantity > 1:
                item_desc += f" x{item.quantity}"
            if item.location:
                item_desc += f" 位置: {item.location}"
            if item.condition:
                item_desc += f" 状态: {item.condition}"
            items_info.append(item_desc)
        
        # 构建环境信息
        env_info = f"""
环境类型: {request.environment.type.value}
区域类型: {request.environment.area.value}
通风情况: {request.environment.ventilation.value}
出口数量: {request.environment.exits}
"""
        if request.environment.floor is not None:
            env_info += f"楼层: {request.environment.floor}\n"
        if request.environment.occupancy is not None:
            env_info += f"人员数量: {request.environment.occupancy}\n"
        if request.environment.building_type:
            env_info += f"建筑类型: {request.environment.building_type}\n"
        if request.environment.special_conditions:
            env_info += f"特殊条件: {request.environment.special_conditions}\n"
        
        # 构建完整提示词
        prompt = f"""
你是一个专业的火灾应急救援专家。请根据以下信息生成详细的救援方案。

## 场景信息

### 物品信息
{chr(10).join(items_info)}

### 环境信息
{env_info}

### 紧急程度
{request.urgency_level}

### 附加信息
{request.additional_info or "无"}

## 输出要求

请严格按照以下格式生成救援方案，必须包含每个步骤的完整详细信息：

### 第一步：立即响应
- 描述：迅速拨打119报警，组织现场人员有序撤离，关闭电源和燃气阀门，避免火势蔓延
- 所需设备：手机，应急照明灯，扩音器，防烟面罩
- 注意事项：确保自身安全，保持冷静，优先疏散老人和儿童，不要使用电梯
- 预计时间：3分钟

### 第二步：火势控制
- 描述：使用适当的灭火器材对火源进行初期扑救，切断火势蔓延路径，重点保护重要设施
- 所需设备：干粉灭火器，消防水带，防火毯，防护服，呼吸器
- 注意事项：注意风向，站在上风位置，保持安全距离，不要贸然进入浓烟区域
- 预计时间：10分钟

### 第三步：人员疏散
- 描述：引导所有人员按照疏散指示标志撤离，清点人数，确认无人员滞留
- 所需设备：应急灯，对讲机，急救箱，警戒带
- 注意事项：低姿前进，用湿毛巾捂住口鼻，不要返回火场，到达安全区域后立即清点人数
- 预计时间：5分钟

### 第四步：现场清理
- 描述：确认火势完全扑灭，检查是否有复燃风险，清理现场残留危险物品，评估损失
- 所需设备：热成像仪，清理工具，警戒标识，相机
- 注意事项：等待消防队确认安全，注意建筑结构稳定性，做好现场保护工作
- 预计时间：15分钟

重要：你必须严格按照上述格式生成4个完整步骤，每个步骤必须包含：
1. 描述：具体、可操作的行动说明（至少15个字）
2. 所需设备：详细的设备清单（至少列出3-5项）
3. 注意事项：安全要点和注意事项（至少列出2-3条）
4. 预计时间：合理的时间估计（3-20分钟）

现在请生成救援方案：
"""
        return prompt
    
    def _parse_rescue_plan_response(self, response: str, urgency_level: str = "中") -> RescuePlan:
        """解析救援方案响应"""
        try:
            # 清理响应文本
            response = response.strip()
            lines = [line.strip() for line in response.split('\n') if line.strip()]
            
            # 提取标题（查找"#"或"标题"关键词）
            title = "火灾应急救援方案"
            for line in lines:
                if line.startswith("#") and ("方案" in line or "标题" in line):
                    title = line.replace("#", "").strip()
                    break
                elif "标题" in line and ":" in line:
                    title = line.split(":", 1)[1].strip()
                    break
            
            # 提取步骤 - 使用更智能的方法
            steps = []
            current_step = None
            step_number = 1
            current_section = None
            
            import re
            
            for i, line in enumerate(lines):
                # 检测新步骤（匹配 "### 第X步：" 格式）
                step_match = re.match(r'^#{1,3}\s*第([一二三四五六七八九十\d]+)步[：:](.+)', line)
                
                if step_match:
                    # 保存前一个步骤
                    if current_step:
                        steps.append(current_step)
                    
                    # 提取步骤标题作为描述
                    step_title = step_match.group(2).strip()
                    
                    current_step = RescueStep(
                        step_number=step_number,
                        description=step_title,
                        equipment=[],
                        warnings=[],
                        estimated_time=5
                    )
                    step_number += 1
                    current_section = None
                
                # 如果在步骤内，解析各个字段（支持Markdown加粗语法 **）
                elif current_step:
                    # 检测描述（支持 **描述** 或 描述）
                    desc_match = re.match(r'^-?\s*\**(描述|说明)\**[：:](.+)', line)
                    if desc_match:
                        desc_text = desc_match.group(2).strip()
                        if desc_text and desc_text != "[具体操作描述]":
                            current_step.description = desc_text
                        current_section = 'description'
                    
                    # 检测设备（支持 **所需设备** 或 所需设备）
                    elif re.match(r'^-?\s*\**所需设备\**[：:]', line):
                        current_section = 'equipment'
                        equipment_text = re.sub(r'^-?\s*\**所需设备\**[：:]', '', line).strip()
                        # 移除可能的句号
                        equipment_text = equipment_text.rstrip('。.')
                        if equipment_text and equipment_text != "[设备列表]":
                            equipment_items = [eq.strip() for eq in re.split(r'[,，、]', equipment_text) if eq.strip()]
                            current_step.equipment.extend(equipment_items)
                    
                    # 检测注意事项（支持 **注意事项** 或 注意事项）
                    elif re.match(r'^-?\s*\**注意事项\**[：:]', line):
                        current_section = 'warnings'
                        warning_text = re.sub(r'^-?\s*\**注意事项\**[：:]', '', line).strip()
                        # 移除可能的句号
                        warning_text = warning_text.rstrip('。.')
                        if warning_text and warning_text != "[安全提醒]":
                            current_step.warnings.append(warning_text)
                    
                    # 检测预计时间（支持 **预计时间** 或 预计时间）
                    elif re.match(r'^-?\s*\**预计时间\**[：:]', line):
                        current_section = 'time'
                        time_text = re.sub(r'^-?\s*\**预计时间\**[：:]', '', line).strip()
                        # 移除可能的句号
                        time_text = time_text.rstrip('。.')
                        time_match = re.search(r'(\d+)\s*分钟', time_text)
                        if time_match:
                            current_step.estimated_time = int(time_match.group(1))
                        else:
                            # 尝试匹配纯数字
                            num_match = re.search(r'(\d+)', time_text)
                            if num_match:
                                current_step.estimated_time = int(num_match.group(1))
                    
                    # 继续收集列表项
                    elif line.startswith("-") or line.startswith("•"):
                        item_text = line.lstrip("-•").strip()
                        if current_section == 'equipment' and item_text:
                            current_step.equipment.append(item_text)
                        elif current_section == 'warnings' and item_text:
                            current_step.warnings.append(item_text)
            
            # 添加最后一个步骤
            if current_step:
                steps.append(current_step)
            
            # 如果没有解析到步骤，创建默认步骤
            if not steps:
                steps = [
                    RescueStep(
                        step_number=1,
                        description="评估现场情况，确保救援人员安全",
                        equipment=["防护装备", "通信设备"],
                        warnings=["注意现场安全", "保持通信畅通"],
                        estimated_time=5
                    ),
                    RescueStep(
                        step_number=2,
                        description="制定具体救援方案并执行",
                        equipment=["救援工具", "安全设备"],
                        warnings=["严格按照安全程序操作"],
                        estimated_time=30
                    )
                ]
            
            # 提取设备清单
            equipment_list = []
            for step in steps:
                equipment_list.extend(step.equipment)
            equipment_list = list(set(equipment_list))  # 去重
            
            # 提取警告
            warnings = []
            for step in steps:
                warnings.extend(step.warnings)
            warnings = list(set(warnings))  # 去重
            
            # 计算总时长
            total_duration = sum(step.estimated_time or 0 for step in steps)
            if total_duration == 0:
                total_duration = 60  # 默认1小时
            
            # 确定优先级
            priority = PriorityLevel.HIGH
            if urgency_level in ["低", "一般"]:
                priority = PriorityLevel.MEDIUM
            elif urgency_level in ["紧急", "非常紧急"]:
                priority = PriorityLevel.URGENT
            
            return RescuePlan(
                title=title,
                priority=priority,
                steps=steps,
                equipment_list=equipment_list,
                warnings=warnings,
                estimated_duration=total_duration
            )
            
        except Exception as e:
            logger.error(f"解析救援方案失败: {str(e)}")
            # 返回默认方案
            return RescuePlan(
                title="火灾应急救援方案",
                priority=PriorityLevel.HIGH,
                steps=[
                    RescueStep(
                        step_number=1,
                        description="评估现场情况，确保救援人员安全",
                        equipment=["防护装备", "通信设备"],
                        warnings=["注意现场安全", "保持通信畅通"],
                        estimated_time=5
                    ),
                    RescueStep(
                        step_number=2,
                        description="制定具体救援方案并执行",
                        equipment=["救援工具", "安全设备"],
                        warnings=["严格按照安全程序操作"],
                        estimated_time=30
                    )
                ],
                equipment_list=["防护装备", "通信设备", "救援工具", "安全设备"],
                warnings=["注意现场安全", "保持通信畅通", "严格按照安全程序操作"],
                estimated_duration=60
            )
    
    async def generate_rescue_plan(self, request: RescuePlanGenerationRequest) -> RescuePlan:
        """生成救援方案"""
        try:
            # 构建提示词
            prompt = self._build_rescue_plan_prompt(request)
            
            # 生成文本
            generation_request = GenerationRequest(
                prompt=prompt,
                model=request.model,
                temperature=request.temperature,
                max_tokens=2048
            )
            
            response = await self.generate_text(generation_request)
            
            # 打印原始响应用于调试
            logger.info(f"🔍 Ollama原始响应（前500字符）: {response.response[:500]}")
            
            # 解析救援方案
            rescue_plan = self._parse_rescue_plan_response(response.response, request.urgency_level)
            
            # 打印解析结果
            logger.info(f"✅ 救援方案生成成功，包含 {len(rescue_plan.steps)} 个步骤")
            for i, step in enumerate(rescue_plan.steps, 1):
                logger.info(f"   步骤{i}: {step.description[:50]}... | 设备数: {len(step.equipment)} | 注意事项数: {len(step.warnings)}")
            return rescue_plan
            
        except Exception as e:
            logger.error(f"生成救援方案失败: {str(e)}")
            raise ServiceError(f"生成救援方案失败: {str(e)}", "ollama_service")
    
    async def clear_cache(self) -> bool:
        """清空缓存"""
        try:
            if self.redis_client:
                # 删除所有ollama相关的缓存
                keys = self.redis_client.keys("ollama:*")
                if keys:
                    self.redis_client.delete(*keys)
                logger.info(f"清空了 {len(keys)} 个缓存项")
                return True
            return False
        except Exception as e:
            logger.error(f"清空缓存失败: {str(e)}")
            return False
    
    async def get_cache_stats(self) -> Dict[str, Any]:
        """获取缓存统计信息"""
        try:
            if not self.redis_client:
                return {"enabled": False, "message": "Redis未连接"}
            
            # 获取ollama相关的缓存键
            keys = self.redis_client.keys("ollama:*")
            total_keys = len(keys)
            
            # 计算总内存使用
            total_memory = 0
            for key in keys:
                try:
                    memory = self.redis_client.memory_usage(key)
                    total_memory += memory or 0
                except:
                    pass
            
            return {
                "enabled": True,
                "total_keys": total_keys,
                "total_memory_bytes": total_memory,
                "total_memory_mb": round(total_memory / 1024 / 1024, 2)
            }
        except Exception as e:
            logger.error(f"获取缓存统计失败: {str(e)}")
            return {"enabled": False, "error": str(e)}

# 创建服务实例
ollama_service = OllamaService()

# FastAPI应用
app = FastAPI(
    title="Ollama服务",
    description="基于Ollama的AI生成服务，提供救援方案生成和模型管理功能",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# 依赖注入
def get_ollama_service() -> OllamaService:
    return ollama_service

# API路由
@app.get("/", response_model=QueryResponse)
async def root():
    """根路径 - 服务信息"""
    return QueryResponse(
        success=True,
        data={
            "service": "Ollama服务",
            "version": "1.0.0",
            "description": "基于Ollama的AI生成服务",
            "endpoints": {
                "health": "/health",
                "models": "/models",
                "generate": "/generate",
                "rescue-plan": "/rescue-plan",
                "cache": "/cache",
                "docs": "/docs"
            }
        },
        message="Ollama服务运行正常"
    )

@app.get("/health", response_model=QueryResponse)
async def health_check(service: OllamaService = Depends(get_ollama_service)):
    """健康检查"""
    try:
        is_healthy = await service.test_connection()
        return QueryResponse(
            success=is_healthy,
            data={"status": "healthy" if is_healthy else "unhealthy"},
            message="服务健康检查完成"
        )
    except Exception as e:
        return QueryResponse(
            success=False,
            data={"status": "unhealthy"},
            message=f"健康检查失败: {str(e)}"
        )

@app.get("/models", response_model=QueryResponse)
async def list_models(service: OllamaService = Depends(get_ollama_service)):
    """获取可用模型列表"""
    try:
        models = await service.list_models()
        return QueryResponse(
            success=True,
            data=[model.model_dump() for model in models],
            message=f"成功获取 {len(models)} 个模型"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取模型列表失败: {str(e)}")

@app.get("/models/{model_name}/status", response_model=QueryResponse)
async def get_model_status(
    model_name: str,
    service: OllamaService = Depends(get_ollama_service)
):
    """获取模型状态"""
    try:
        status = await service.get_model_status(model_name)
        return QueryResponse(
            success=True,
            data=status.model_dump(),
            message=f"成功获取模型 {model_name} 的状态"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取模型状态失败: {str(e)}")

@app.post("/models/{model_name}/load", response_model=QueryResponse)
async def load_model(
    model_name: str,
    service: OllamaService = Depends(get_ollama_service)
):
    """加载模型"""
    try:
        success = await service.load_model(model_name)
        return QueryResponse(
            success=success,
            data={"model_name": model_name, "loaded": success},
            message=f"模型 {model_name} {'加载成功' if success else '加载失败'}"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"加载模型失败: {str(e)}")

@app.post("/generate", response_model=GenerationResponse)
async def generate_text(
    request: GenerationRequest,
    service: OllamaService = Depends(get_ollama_service)
):
    """生成文本"""
    try:
        result = await service.generate_text(request)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"生成文本失败: {str(e)}")

@app.post("/rescue-plan", response_model=QueryResponse)
async def generate_rescue_plan(
    request: RescuePlanGenerationRequest,
    service: OllamaService = Depends(get_ollama_service)
):
    """生成救援方案"""
    try:
        rescue_plan = await service.generate_rescue_plan(request)
        return QueryResponse(
            success=True,
            data=rescue_plan.model_dump(),
            message="救援方案生成成功"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"生成救援方案失败: {str(e)}")

@app.get("/cache/stats", response_model=QueryResponse)
async def get_cache_stats(service: OllamaService = Depends(get_ollama_service)):
    """获取缓存统计信息"""
    try:
        stats = await service.get_cache_stats()
        return QueryResponse(
            success=True,
            data=stats,
            message="缓存统计信息获取成功"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取缓存统计失败: {str(e)}")

@app.delete("/cache", response_model=QueryResponse)
async def clear_cache(service: OllamaService = Depends(get_ollama_service)):
    """清空缓存"""
    try:
        success = await service.clear_cache()
        return QueryResponse(
            success=success,
            data={"cleared": success},
            message="缓存清空成功" if success else "缓存清空失败"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"清空缓存失败: {str(e)}")

# 启动和关闭事件
@app.on_event("startup")
async def startup_event():
    """应用启动事件"""
    logger.info("Ollama服务启动中...")
    try:
        is_healthy = await ollama_service.test_connection()
        if is_healthy:
            logger.info("Ollama服务启动成功")
        else:
            logger.warning("Ollama服务启动，但连接异常")
    except Exception as e:
        logger.error(f"Ollama服务启动失败: {str(e)}")

@app.on_event("shutdown")
async def shutdown_event():
    """应用关闭事件"""
    logger.info("Ollama服务关闭中...")
    logger.info("Ollama服务已关闭")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8003)
