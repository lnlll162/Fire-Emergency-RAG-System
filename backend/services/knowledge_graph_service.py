#!/usr/bin/env python3
"""
知识图谱服务
提供火灾应急救援相关的知识图谱查询功能
"""

import asyncio
import logging
import sys
import os
from typing import List, Dict, Any, Optional
from datetime import datetime
from pathlib import Path

# 设置代理跳过localhost（解决Windows代理导致的502错误）
os.environ['NO_PROXY'] = 'localhost,127.0.0.1,::1'
os.environ['no_proxy'] = 'localhost,127.0.0.1,::1'

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

from fastapi import FastAPI, HTTPException, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from neo4j import GraphDatabase
from neo4j.exceptions import ServiceUnavailable, AuthError

from shared.config import get_config
from shared.exceptions import DatabaseConnectionError, QueryExecutionError

# 配置日志
logger = logging.getLogger(__name__)

# 数据模型
class MaterialInfo(BaseModel):
    """材质信息"""
    name: str = Field(..., description="材质名称")
    properties: Dict[str, Any] = Field(default_factory=dict, description="材质属性")
    hazards: List[str] = Field(default_factory=list, description="危险特性")
    safety_measures: List[str] = Field(default_factory=list, description="安全措施")

class EnvironmentInfo(BaseModel):
    """环境信息"""
    location: str = Field(..., description="位置")
    conditions: Dict[str, Any] = Field(default_factory=dict, description="环境条件")
    risks: List[str] = Field(default_factory=list, description="风险因素")
    recommendations: List[str] = Field(default_factory=list, description="建议措施")

class RescueProcedure(BaseModel):
    """救援程序"""
    procedure_id: str = Field(..., description="程序ID")
    title: str = Field(..., description="程序标题")
    description: str = Field(..., description="程序描述")
    steps: List[str] = Field(default_factory=list, description="执行步骤")
    materials_needed: List[str] = Field(default_factory=list, description="所需材料")
    safety_notes: List[str] = Field(default_factory=list, description="安全注意事项")

class QueryResponse(BaseModel):
    """查询响应"""
    success: bool = Field(..., description="查询是否成功")
    data: Any = Field(..., description="查询结果数据")
    message: str = Field(default="", description="响应消息")
    timestamp: datetime = Field(default_factory=datetime.now, description="响应时间")

class KnowledgeGraphService:
    """知识图谱服务类"""
    
    def __init__(self):
        self.config = get_config()
        self.driver = None
        self._initialize_connection()
    
    def _initialize_connection(self):
        """初始化Neo4j连接"""
        try:
            self.driver = GraphDatabase.driver(
                self.config.database.neo4j_uri,
                auth=(self.config.database.neo4j_user, self.config.database.neo4j_password)
            )
            logger.info("Neo4j连接初始化成功")
        except Exception as e:
            logger.error(f"Neo4j连接初始化失败: {str(e)}")
            raise DatabaseConnectionError(f"无法连接到Neo4j数据库: {str(e)}")
    
    def close(self):
        """关闭数据库连接"""
        if self.driver:
            self.driver.close()
            logger.info("Neo4j连接已关闭")
    
    async def test_connection(self) -> bool:
        """测试数据库连接"""
        try:
            with self.driver.session() as session:
                result = session.run("RETURN 1 as test")
                record = result.single()
                return record["test"] == 1
        except Exception as e:
            logger.error(f"数据库连接测试失败: {str(e)}")
            return False
    
    async def get_material_info(self, material_name: str) -> Optional[MaterialInfo]:
        """获取材质信息"""
        query = """
        MATCH (m:Material {name: $material_name})
        OPTIONAL MATCH (m)-[:HAS_PROPERTY]->(p:Property)
        OPTIONAL MATCH (m)-[:HAS_HAZARD]->(h:Hazard)
        OPTIONAL MATCH (m)-[:HAS_SAFETY_MEASURE]->(s:SafetyMeasure)
        RETURN m.name as name,
               collect(DISTINCT {key: p.key, value: p.value}) as properties,
               collect(DISTINCT h.description) as hazards,
               collect(DISTINCT s.description) as safety_measures
        """
        
        try:
            with self.driver.session() as session:
                result = session.run(query, material_name=material_name)
                record = result.single()
                
                if not record:
                    return None
                
                # 处理属性字典
                properties = {}
                for prop in record["properties"]:
                    if prop["key"] and prop["value"]:
                        properties[prop["key"]] = prop["value"]
                
                return MaterialInfo(
                    name=record["name"],
                    properties=properties,
                    hazards=[h for h in record["hazards"] if h],
                    safety_measures=[s for s in record["safety_measures"] if s]
                )
        except Exception as e:
            logger.error(f"查询材质信息失败: {str(e)}")
            raise QueryExecutionError(f"查询材质信息失败: {str(e)}")
    
    async def get_environment_info(self, location: str) -> Optional[EnvironmentInfo]:
        """获取环境信息"""
        query = """
        MATCH (e:Environment {location: $location})
        OPTIONAL MATCH (e)-[:HAS_CONDITION]->(c:Condition)
        OPTIONAL MATCH (e)-[:HAS_RISK]->(r:Risk)
        OPTIONAL MATCH (e)-[:HAS_RECOMMENDATION]->(rec:Recommendation)
        RETURN e.location as location,
               collect(DISTINCT {key: c.key, value: c.value}) as conditions,
               collect(DISTINCT r.description) as risks,
               collect(DISTINCT rec.description) as recommendations
        """
        
        try:
            with self.driver.session() as session:
                result = session.run(query, location=location)
                record = result.single()
                
                if not record:
                    return None
                
                # 处理条件字典
                conditions = {}
                for cond in record["conditions"]:
                    if cond["key"] and cond["value"]:
                        conditions[cond["key"]] = cond["value"]
                
                return EnvironmentInfo(
                    location=record["location"],
                    conditions=conditions,
                    risks=[r for r in record["risks"] if r],
                    recommendations=[rec for rec in record["recommendations"] if rec]
                )
        except Exception as e:
            logger.error(f"查询环境信息失败: {str(e)}")
            raise QueryExecutionError(f"查询环境信息失败: {str(e)}")
    
    async def get_rescue_procedures(self, material_name: Optional[str] = None, 
                                 environment: Optional[str] = None) -> List[RescueProcedure]:
        """获取救援程序"""
        if material_name and environment:
            query = """
            MATCH (p:Procedure)
            WHERE (p)-[:APPLIES_TO]->(:Material {name: $material_name})
               OR (p)-[:APPLIES_TO]->(:Environment {location: $environment})
            OPTIONAL MATCH (p)-[:HAS_STEP]->(s:Step)
            OPTIONAL MATCH (p)-[:REQUIRES_MATERIAL]->(mat:Material)
            OPTIONAL MATCH (p)-[:HAS_SAFETY_NOTE]->(sn:SafetyNote)
            RETURN p.id as procedure_id,
                   p.title as title,
                   p.description as description,
                   collect(DISTINCT s.description) as steps,
                   collect(DISTINCT mat.name) as materials_needed,
                   collect(DISTINCT sn.description) as safety_notes,
                   p.priority as priority
            ORDER BY p.priority DESC
            """
            params = {"material_name": material_name, "environment": environment}
        elif material_name:
            query = """
            MATCH (p:Procedure)-[:APPLIES_TO]->(m:Material {name: $material_name})
            OPTIONAL MATCH (p)-[:HAS_STEP]->(s:Step)
            OPTIONAL MATCH (p)-[:REQUIRES_MATERIAL]->(mat:Material)
            OPTIONAL MATCH (p)-[:HAS_SAFETY_NOTE]->(sn:SafetyNote)
            RETURN p.id as procedure_id,
                   p.title as title,
                   p.description as description,
                   collect(DISTINCT s.description) as steps,
                   collect(DISTINCT mat.name) as materials_needed,
                   collect(DISTINCT sn.description) as safety_notes,
                   p.priority as priority
            ORDER BY p.priority DESC
            """
            params = {"material_name": material_name}
        elif environment:
            query = """
            MATCH (p:Procedure)-[:APPLIES_TO]->(e:Environment {location: $environment})
            OPTIONAL MATCH (p)-[:HAS_STEP]->(s:Step)
            OPTIONAL MATCH (p)-[:REQUIRES_MATERIAL]->(mat:Material)
            OPTIONAL MATCH (p)-[:HAS_SAFETY_NOTE]->(sn:SafetyNote)
            RETURN p.id as procedure_id,
                   p.title as title,
                   p.description as description,
                   collect(DISTINCT s.description) as steps,
                   collect(DISTINCT mat.name) as materials_needed,
                   collect(DISTINCT sn.description) as safety_notes,
                   p.priority as priority
            ORDER BY p.priority DESC
            """
            params = {"environment": environment}
        else:
            query = """
            MATCH (p:Procedure)
            OPTIONAL MATCH (p)-[:HAS_STEP]->(s:Step)
            OPTIONAL MATCH (p)-[:REQUIRES_MATERIAL]->(mat:Material)
            OPTIONAL MATCH (p)-[:HAS_SAFETY_NOTE]->(sn:SafetyNote)
            RETURN p.id as procedure_id,
                   p.title as title,
                   p.description as description,
                   collect(DISTINCT s.description) as steps,
                   collect(DISTINCT mat.name) as materials_needed,
                   collect(DISTINCT sn.description) as safety_notes,
                   p.priority as priority
            ORDER BY p.priority DESC
            """
            params = {}
        
        try:
            with self.driver.session() as session:
                result = session.run(query, **params)
                procedures = []
                
                for record in result:
                    procedures.append(RescueProcedure(
                        procedure_id=record["procedure_id"],
                        title=record["title"],
                        description=record["description"],
                        steps=[s for s in record["steps"] if s],
                        materials_needed=[m for m in record["materials_needed"] if m],
                        safety_notes=[sn for sn in record["safety_notes"] if sn]
                    ))
                
                return procedures
        except Exception as e:
            logger.error(f"查询救援程序失败: {str(e)}")
            raise QueryExecutionError(f"查询救援程序失败: {str(e)}")
    
    async def search_materials(self, keyword: str) -> List[str]:
        """搜索材质"""
        query = """
        MATCH (m:Material)
        WHERE toLower(m.name) CONTAINS toLower($keyword)
        RETURN m.name as name
        ORDER BY m.name
        LIMIT 20
        """
        
        try:
            with self.driver.session() as session:
                result = session.run(query, keyword=keyword)
                return [record["name"] for record in result]
        except Exception as e:
            logger.error(f"搜索材质失败: {str(e)}")
            raise QueryExecutionError(f"搜索材质失败: {str(e)}")
    
    async def get_related_materials(self, material_name: str) -> List[str]:
        """获取相关材质"""
        query = """
        MATCH (m:Material {name: $material_name})-[:RELATED_TO]->(related:Material)
        RETURN related.name as name
        ORDER BY related.name
        """
        
        try:
            with self.driver.session() as session:
                result = session.run(query, material_name=material_name)
                return [record["name"] for record in result]
        except Exception as e:
            logger.error(f"查询相关材质失败: {str(e)}")
            raise QueryExecutionError(f"查询相关材质失败: {str(e)}")

# 创建服务实例
kg_service = KnowledgeGraphService()

# FastAPI应用
app = FastAPI(
    title="知识图谱服务",
    description="火灾应急救援知识图谱查询服务",
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
def get_kg_service() -> KnowledgeGraphService:
    return kg_service

# API路由
@app.get("/", response_model=QueryResponse)
async def root():
    """根路径 - 服务信息"""
    return QueryResponse(
        success=True,
        data={
            "service": "知识图谱服务",
            "version": "1.0.0",
            "description": "火灾应急救援知识图谱查询服务",
            "endpoints": {
                "health": "/health",
                "materials": "/materials/{material_name}",
                "environments": "/environments/{location}",
                "procedures": "/procedures",
                "search": "/materials/search/{keyword}",
                "related": "/materials/{material_name}/related",
                "docs": "/docs"
            }
        },
        message="知识图谱服务运行正常"
    )

@app.get("/health", response_model=QueryResponse)
async def health_check(service: KnowledgeGraphService = Depends(get_kg_service)):
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

@app.get("/materials/{material_name}", response_model=QueryResponse)
async def get_material(
    material_name: str,
    service: KnowledgeGraphService = Depends(get_kg_service)
):
    """获取材质信息"""
    try:
        material_info = await service.get_material_info(material_name)
        if not material_info:
            raise HTTPException(status_code=404, detail=f"未找到材质: {material_name}")
        
        return QueryResponse(
            success=True,
            data=material_info.model_dump(),
            message=f"成功获取材质 {material_name} 的信息"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取材质信息失败: {str(e)}")

@app.get("/environments/{location}", response_model=QueryResponse)
async def get_environment(
    location: str,
    service: KnowledgeGraphService = Depends(get_kg_service)
):
    """获取环境信息"""
    try:
        env_info = await service.get_environment_info(location)
        if not env_info:
            raise HTTPException(status_code=404, detail=f"未找到环境: {location}")
        
        return QueryResponse(
            success=True,
            data=env_info.model_dump(),
            message=f"成功获取环境 {location} 的信息"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取环境信息失败: {str(e)}")

@app.get("/procedures", response_model=QueryResponse)
async def get_procedures(
    material_name: Optional[str] = None,
    environment: Optional[str] = None,
    service: KnowledgeGraphService = Depends(get_kg_service)
):
    """获取救援程序"""
    try:
        procedures = await service.get_rescue_procedures(material_name, environment)
        return QueryResponse(
            success=True,
            data=[p.model_dump() for p in procedures],
            message=f"成功获取 {len(procedures)} 个救援程序"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取救援程序失败: {str(e)}")

@app.get("/materials/search/{keyword}", response_model=QueryResponse)
async def search_materials(
    keyword: str,
    service: KnowledgeGraphService = Depends(get_kg_service)
):
    """搜索材质"""
    try:
        materials = await service.search_materials(keyword)
        return QueryResponse(
            success=True,
            data=materials,
            message=f"搜索到 {len(materials)} 个相关材质"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"搜索材质失败: {str(e)}")

@app.get("/materials/{material_name}/related", response_model=QueryResponse)
async def get_related_materials(
    material_name: str,
    service: KnowledgeGraphService = Depends(get_kg_service)
):
    """获取相关材质"""
    try:
        related = await service.get_related_materials(material_name)
        return QueryResponse(
            success=True,
            data=related,
            message=f"找到 {len(related)} 个相关材质"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取相关材质失败: {str(e)}")

# 添加前端API兼容端点
@app.get("/api/v1/knowledge/graph", response_model=QueryResponse)
async def knowledge_graph_query(
    q: str = Query(..., description="搜索关键词"),
    service: KnowledgeGraphService = Depends(get_kg_service)
):
    """知识图谱查询接口（前端兼容）"""
    try:
        logger.info(f"收到知识图谱查询请求: {q}")
        
        # 搜索相关材质和信息
        materials = await service.search_materials(q)
        
        # 构建图谱节点和边
        nodes = []
        edges = []
        
        # 为每个找到的材质创建节点
        for i, material in enumerate(materials[:10]):  # 限制返回数量
            node_id = f"node_{i}"
            nodes.append({
                "id": node_id,
                "label": material,
                "type": "material",
                "properties": {"name": material}
            })
            
            # 如果不是第一个节点，创建与前一个节点的关联
            if i > 0:
                edges.append({
                    "source": f"node_{i-1}",
                    "target": node_id,
                    "type": "related_to"
                })
        
        response_data = {
            "nodes": nodes,
            "edges": edges,
            "query": q,
            "count": len(nodes)
        }
        
        return QueryResponse(
            success=True,
            data=response_data,
            message=f"找到 {len(nodes)} 个相关节点"
        )
    except Exception as e:
        logger.error(f"知识图谱查询失败: {str(e)}")
        return QueryResponse(
            success=False,
            data={"nodes": [], "edges": [], "query": q, "count": 0},
            message=f"查询失败: {str(e)}"
        )

# 启动和关闭事件
@app.on_event("startup")
async def startup_event():
    """应用启动事件"""
    logger.info("知识图谱服务启动中...")
    try:
        is_healthy = await kg_service.test_connection()
        if is_healthy:
            logger.info("知识图谱服务启动成功")
        else:
            logger.warning("知识图谱服务启动，但数据库连接异常")
    except Exception as e:
        logger.error(f"知识图谱服务启动失败: {str(e)}")

@app.on_event("shutdown")
async def shutdown_event():
    """应用关闭事件"""
    logger.info("知识图谱服务关闭中...")
    kg_service.close()
    logger.info("知识图谱服务已关闭")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
