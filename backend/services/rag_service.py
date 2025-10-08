#!/usr/bin/env python3
"""
RAG服务
提供检索增强生成功能，包括文档嵌入、语义搜索、上下文增强等
"""

import asyncio
import logging
import sys
import os
import json
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

from fastapi import FastAPI, HTTPException, Depends, UploadFile, File
from pydantic import BaseModel, Field
import chromadb
from chromadb.config import Settings
import httpx
import numpy as np
from sentence_transformers import SentenceTransformer

from shared.config import get_config
from shared.exceptions import DatabaseConnectionError, QueryExecutionError

# 配置日志
logger = logging.getLogger(__name__)

# 数据模型
class DocumentInfo(BaseModel):
    """文档信息"""
    id: str = Field(..., description="文档ID")
    title: str = Field(..., description="文档标题")
    content: str = Field(..., description="文档内容")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="文档元数据")
    created_at: datetime = Field(default_factory=datetime.now, description="创建时间")
    updated_at: datetime = Field(default_factory=datetime.now, description="更新时间")

class SearchResult(BaseModel):
    """搜索结果"""
    document_id: str = Field(..., description="文档ID")
    title: str = Field(..., description="文档标题")
    content: str = Field(..., description="文档内容")
    score: float = Field(..., description="相似度分数")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="文档元数据")

class SearchRequest(BaseModel):
    """搜索请求"""
    query: str = Field(..., description="搜索查询")
    limit: int = Field(default=10, ge=1, le=100, description="返回结果数量限制")
    filter_metadata: Optional[Dict[str, Any]] = Field(default=None, description="元数据过滤条件")

class SearchResponse(BaseModel):
    """搜索响应"""
    query: str = Field(..., description="搜索查询")
    results: List[SearchResult] = Field(..., description="搜索结果")
    total_count: int = Field(..., description="总结果数")
    search_time: float = Field(..., description="搜索耗时(秒)")

class ContextEnhancementRequest(BaseModel):
    """上下文增强请求"""
    query: str = Field(..., description="用户查询")
    context_documents: List[SearchResult] = Field(..., description="上下文文档")
    max_context_length: int = Field(default=4000, ge=1000, le=8000, description="最大上下文长度")

class ContextEnhancementResponse(BaseModel):
    """上下文增强响应"""
    enhanced_query: str = Field(..., description="增强后的查询")
    context_summary: str = Field(..., description="上下文摘要")
    relevant_sections: List[str] = Field(..., description="相关段落")
    confidence_score: float = Field(..., description="置信度分数")

class DocumentUploadResponse(BaseModel):
    """文档上传响应"""
    document_id: str = Field(..., description="文档ID")
    title: str = Field(..., description="文档标题")
    status: str = Field(..., description="处理状态")
    message: str = Field(..., description="处理消息")

class QueryResponse(BaseModel):
    """查询响应"""
    success: bool = Field(..., description="查询是否成功")
    data: Any = Field(..., description="查询结果数据")
    message: str = Field(default="", description="响应消息")
    timestamp: datetime = Field(default_factory=datetime.now, description="响应时间")

class RAGService:
    """RAG服务类"""
    
    def __init__(self):
        self.config = get_config()
        self.chroma_client = None
        self.collection = None
        self.embedding_model = None
        self.model_cache_dir = Path("models/embeddings")
        self.model_info_file = self.model_cache_dir / "model_info.json"
        self._ensure_model_cache_dir()
        self._initialize_connection()
        self._load_embedding_model()
    
    def _ensure_model_cache_dir(self):
        """确保模型缓存目录存在"""
        self.model_cache_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"模型缓存目录: {self.model_cache_dir.absolute()}")
    
    def _save_model_info(self, model_name: str, success: bool, error_msg: str = None):
        """保存模型加载信息"""
        model_info = {
            "last_attempt": datetime.now().isoformat(),
            "model_name": model_name,
            "success": success,
            "error": error_msg
        }
        
        try:
            with open(self.model_info_file, 'w', encoding='utf-8') as f:
                json.dump(model_info, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.warning(f"保存模型信息失败: {str(e)}")
    
    def _load_model_info(self) -> Dict[str, Any]:
        """加载模型信息"""
        if not self.model_info_file.exists():
            return {}
        
        try:
            with open(self.model_info_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.warning(f"加载模型信息失败: {str(e)}")
            return {}
    
    def _initialize_connection(self):
        """初始化ChromaDB连接"""
        try:
            self.chroma_client = chromadb.HttpClient(
                host=self.config.database.chroma_host,
                port=self.config.database.chroma_port
            )
            
            # 获取或创建集合
            collection_name = "fire_rescue_knowledge"
            try:
                self.collection = self.chroma_client.get_collection(collection_name)
                logger.info(f"ChromaDB集合 '{collection_name}' 已存在")
            except:
                self.collection = self.chroma_client.create_collection(
                    name=collection_name,
                    metadata={"description": "火灾救援知识库"}
                )
                logger.info(f"ChromaDB集合 '{collection_name}' 创建成功")
            
            logger.info("ChromaDB连接初始化成功")
        except Exception as e:
            logger.error(f"ChromaDB连接初始化失败: {str(e)}")
            raise DatabaseConnectionError(f"无法连接到ChromaDB数据库: {str(e)}")
    
    def _load_embedding_model(self):
        """加载嵌入模型 - 支持多种模型和离线模式"""
        # 检查上次成功的模型
        model_info = self._load_model_info()
        if model_info.get('success') and model_info.get('model_name'):
            logger.info(f"尝试加载上次成功的模型: {model_info['model_name']}")
            if self._try_load_model(model_info['model_name']):
                return
        
        # 按优先级尝试不同的模型（优先使用384维模型）
        model_candidates = [
            {
                'name': 'paraphrase-multilingual-MiniLM-L12-v2',
                'description': '多语言轻量级模型（384维）',
                'priority': 1,
                'dimension': 384
            },
            {
                'name': 'all-MiniLM-L6-v2',
                'description': '英文轻量级模型（384维）',
                'priority': 2,
                'dimension': 384
            },
            {
                'name': 'distiluse-base-multilingual-cased',
                'description': '多语言基础模型（512维）',
                'priority': 3,
                'dimension': 512
            },
            {
                'name': 'all-mpnet-base-v2',
                'description': '高性能英文模型（768维）',
                'priority': 4,
                'dimension': 768
            }
        ]
        
        # 按优先级排序
        model_candidates.sort(key=lambda x: x['priority'])
        
        for model_info in model_candidates:
            logger.info(f"尝试加载模型: {model_info['name']} ({model_info['description']})")
            
            if self._try_load_model(model_info['name']):
                self._save_model_info(model_info['name'], True)
                return
            else:
                self._save_model_info(model_info['name'], False, "模型加载或测试失败")
        
        # 如果所有模型都失败，使用备用方案
        logger.warning("所有嵌入模型加载失败，使用备用嵌入方案")
        self.embedding_model = None
        self._save_model_info("none", False, "所有模型都加载失败")
    
    def _try_load_model(self, model_name: str) -> bool:
        """尝试加载指定模型"""
        try:
            # 尝试加载模型
            self.embedding_model = SentenceTransformer(model_name)
            
            # 测试模型是否正常工作
            test_text = "测试文本"
            test_embedding = self.embedding_model.encode([test_text])
            
            if test_embedding is not None and len(test_embedding) > 0:
                # 检查维度是否匹配（384维）
                embedding_dim = test_embedding.shape[1]
                if embedding_dim == 384:
                    logger.info(f"✅ 嵌入模型加载成功: {model_name}")
                    logger.info(f"模型维度: {embedding_dim}")
                    return True
                else:
                    logger.warning(f"模型 {model_name} 维度不匹配: {embedding_dim} (期望384)")
                    self.embedding_model = None
                    return False
            else:
                logger.warning(f"模型 {model_name} 测试失败")
                self.embedding_model = None
                return False
                
        except Exception as e:
            logger.warning(f"模型 {model_name} 加载失败: {str(e)}")
            self.embedding_model = None
            return False
    
    def _get_embeddings(self, texts: List[str]) -> List[List[float]]:
        """获取文本嵌入向量"""
        if self.embedding_model:
            try:
                # 使用模型生成嵌入向量
                embeddings = self.embedding_model.encode(texts, convert_to_tensor=False)
                
                # 确保返回的是列表格式
                if hasattr(embeddings, 'tolist'):
                    embeddings = embeddings.tolist()
                elif hasattr(embeddings, 'numpy'):
                    embeddings = embeddings.numpy().tolist()
                
                # 验证嵌入向量格式
                if isinstance(embeddings, list) and len(embeddings) > 0:
                    logger.debug(f"成功生成 {len(embeddings)} 个嵌入向量，维度: {len(embeddings[0])}")
                    return embeddings
                else:
                    logger.warning("模型返回的嵌入向量格式不正确，使用备用方案")
                    
            except Exception as e:
                logger.error(f"嵌入生成失败: {str(e)}")
                logger.warning("切换到备用嵌入方案")
        
        # 备用方案：使用增强的文本特征
        logger.info("使用备用嵌入方案")
        embeddings = []
        
        for text in texts:
            # 增强的文本特征向量
            features = self._extract_text_features(text)
            
            # 归一化特征
            normalized_features = self._normalize_features(features)
            
            # 扩展到标准维度（384维）
            embedding = self._expand_to_dimension(normalized_features, 384)
            embeddings.append(embedding)
        
        logger.info(f"使用备用方案生成 {len(embeddings)} 个嵌入向量")
        return embeddings
    
    def _extract_text_features(self, text: str) -> List[float]:
        """提取文本特征"""
        # 基础统计特征
        char_count = len(text)
        word_count = len(text.split())
        sentence_count = text.count('。') + text.count('!') + text.count('?') + 1
        
        # 火灾救援相关关键词特征
        fire_keywords = ['火', '火灾', '燃烧', '火焰', '烟雾', '爆炸']
        rescue_keywords = ['救援', '救助', '抢救', '疏散', '逃生', '安全']
        material_keywords = ['材料', '材质', '物品', '设备', '工具', '器材']
        environment_keywords = ['环境', '场所', '建筑', '房间', '室内', '室外']
        safety_keywords = ['安全', '危险', '防护', '预防', '措施', '程序']
        
        # 计算关键词出现次数
        text_lower = text.lower()
        features = [
            char_count,
            word_count,
            sentence_count,
            char_count / max(word_count, 1),  # 平均词长
            word_count / max(sentence_count, 1),  # 平均句长
        ]
        
        # 添加关键词特征
        for keyword_list in [fire_keywords, rescue_keywords, material_keywords, 
                           environment_keywords, safety_keywords]:
            count = sum(text.count(keyword) for keyword in keyword_list)
            features.append(count)
            features.append(count / max(word_count, 1))  # 关键词密度
        
        # 添加字符类型特征
        features.extend([
            sum(1 for c in text if c.isdigit()),  # 数字字符数
            sum(1 for c in text if c.isalpha()),  # 字母字符数
            sum(1 for c in text if c.isspace()),  # 空格字符数
            sum(1 for c in text if c in '，。！？；：'),  # 标点符号数
        ])
        
        return features
    
    def _normalize_features(self, features: List[float]) -> List[float]:
        """归一化特征向量"""
        if not features:
            return [0.0] * 20  # 返回默认长度的零向量
        
        # 计算最大值用于归一化
        max_val = max(features) if max(features) > 0 else 1.0
        
        # 归一化到 [0, 1] 范围
        normalized = [f / max_val for f in features]
        
        # 确保向量长度一致
        target_length = 20
        if len(normalized) < target_length:
            # 填充零
            normalized.extend([0.0] * (target_length - len(normalized)))
        elif len(normalized) > target_length:
            # 截断
            normalized = normalized[:target_length]
        
        return normalized
    
    def _expand_to_dimension(self, features: List[float], target_dim: int) -> List[float]:
        """将特征向量扩展到目标维度"""
        if len(features) >= target_dim:
            return features[:target_dim]
        
        # 使用重复和变化来填充
        expanded = features.copy()
        while len(expanded) < target_dim:
            # 重复现有特征并添加小的随机变化
            for i, val in enumerate(features):
                if len(expanded) >= target_dim:
                    break
                # 添加小的变化避免完全重复
                variation = (i % 10) * 0.01
                expanded.append((val + variation) % 1.0)
        
        return expanded
    
    async def test_connection(self) -> bool:
        """测试数据库连接"""
        try:
            # 测试ChromaDB连接
            self.chroma_client.heartbeat()
            return True
        except Exception as e:
            logger.error(f"ChromaDB连接测试失败: {str(e)}")
            return False
    
    async def add_document(self, title: str, content: str, metadata: Optional[Dict[str, Any]] = None) -> str:
        """添加文档到知识库"""
        try:
            # 生成文档ID
            doc_id = f"doc_{int(datetime.now().timestamp() * 1000)}"
            
            # 生成嵌入向量
            embeddings = self._get_embeddings([content])
            
            # 准备元数据
            doc_metadata = {
                "title": title,
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat(),
                **(metadata or {})
            }
            
            # 添加到ChromaDB
            self.collection.add(
                ids=[doc_id],
                documents=[content],
                metadatas=[doc_metadata],
                embeddings=embeddings
            )
            
            logger.info(f"文档添加成功: {doc_id}")
            return doc_id
            
        except Exception as e:
            logger.error(f"添加文档失败: {str(e)}")
            raise QueryExecutionError(f"添加文档失败: {str(e)}")
    
    async def search_documents(self, query: str, limit: int = 10, 
                             filter_metadata: Optional[Dict[str, Any]] = None) -> List[SearchResult]:
        """搜索文档"""
        try:
            # 生成查询嵌入
            query_embeddings = self._get_embeddings([query])
            
            # 执行搜索
            results = self.collection.query(
                query_embeddings=query_embeddings,
                n_results=limit,
                where=filter_metadata
            )
            
            # 处理结果
            search_results = []
            if results['ids'] and results['ids'][0]:
                for i, doc_id in enumerate(results['ids'][0]):
                    search_results.append(SearchResult(
                        document_id=doc_id,
                        title=results['metadatas'][0][i].get('title', ''),
                        content=results['documents'][0][i],
                        score=1 - results['distances'][0][i],  # 转换为相似度分数
                        metadata=results['metadatas'][0][i]
                    ))
            
            return search_results
            
        except Exception as e:
            logger.error(f"搜索文档失败: {str(e)}")
            raise QueryExecutionError(f"搜索文档失败: {str(e)}")
    
    async def get_document(self, document_id: str) -> Optional[DocumentInfo]:
        """获取文档详情"""
        try:
            results = self.collection.get(
                ids=[document_id],
                include=['documents', 'metadatas']
            )
            
            if not results['ids']:
                return None
            
            metadata = results['metadatas'][0]
            return DocumentInfo(
                id=document_id,
                title=metadata.get('title', ''),
                content=results['documents'][0],
                metadata=metadata,
                created_at=datetime.fromisoformat(metadata.get('created_at', datetime.now().isoformat())),
                updated_at=datetime.fromisoformat(metadata.get('updated_at', datetime.now().isoformat()))
            )
            
        except Exception as e:
            logger.error(f"获取文档失败: {str(e)}")
            raise QueryExecutionError(f"获取文档失败: {str(e)}")
    
    async def update_document(self, document_id: str, title: Optional[str] = None, 
                            content: Optional[str] = None, 
                            metadata: Optional[Dict[str, Any]] = None) -> bool:
        """更新文档"""
        try:
            # 获取现有文档
            existing = await self.get_document(document_id)
            if not existing:
                return False
            
            # 准备更新数据
            new_title = title or existing.title
            new_content = content or existing.content
            new_metadata = {**existing.metadata, **(metadata or {})}
            new_metadata['updated_at'] = datetime.now().isoformat()
            
            # 生成新的嵌入向量
            embeddings = self._get_embeddings([new_content])
            
            # 更新文档
            self.collection.update(
                ids=[document_id],
                documents=[new_content],
                metadatas=[new_metadata],
                embeddings=embeddings
            )
            
            logger.info(f"文档更新成功: {document_id}")
            return True
            
        except Exception as e:
            logger.error(f"更新文档失败: {str(e)}")
            raise QueryExecutionError(f"更新文档失败: {str(e)}")
    
    async def delete_document(self, document_id: str) -> bool:
        """删除文档"""
        try:
            self.collection.delete(ids=[document_id])
            logger.info(f"文档删除成功: {document_id}")
            return True
        except Exception as e:
            logger.error(f"删除文档失败: {str(e)}")
            raise QueryExecutionError(f"删除文档失败: {str(e)}")
    
    async def enhance_context(self, query: str, context_documents: List[SearchResult], 
                            max_context_length: int = 4000) -> ContextEnhancementResponse:
        """增强上下文"""
        try:
            # 按相似度分数排序
            sorted_docs = sorted(context_documents, key=lambda x: x.score, reverse=True)
            
            # 构建上下文
            context_parts = []
            current_length = 0
            
            for doc in sorted_docs:
                if current_length + len(doc.content) > max_context_length:
                    break
                context_parts.append(f"【{doc.title}】\n{doc.content[:500]}...")
                current_length += len(doc.content)
            
            # 生成上下文摘要
            context_summary = f"基于{len(context_parts)}个相关文档的上下文信息"
            
            # 提取相关段落
            relevant_sections = []
            for doc in sorted_docs[:5]:  # 取前5个最相关的文档
                # 简单的段落提取（按句号分割）
                sentences = doc.content.split('。')
                relevant_sections.extend(sentences[:3])  # 每篇文档取前3句
            
            # 计算置信度分数
            confidence_score = min(1.0, len(context_documents) / 10.0) if context_documents else 0.0
            
            return ContextEnhancementResponse(
                enhanced_query=f"基于火灾救援知识库的查询: {query}",
                context_summary=context_summary,
                relevant_sections=relevant_sections,
                confidence_score=confidence_score
            )
            
        except Exception as e:
            logger.error(f"上下文增强失败: {str(e)}")
            raise QueryExecutionError(f"上下文增强失败: {str(e)}")
    
    async def get_collection_stats(self) -> Dict[str, Any]:
        """获取集合统计信息"""
        try:
            count = self.collection.count()
            return {
                "total_documents": count,
                "collection_name": self.collection.name,
                "embedding_model": "paraphrase-multilingual-MiniLM-L12-v2" if self.embedding_model else "simple_features"
            }
        except Exception as e:
            logger.error(f"获取统计信息失败: {str(e)}")
            raise QueryExecutionError(f"获取统计信息失败: {str(e)}")

# 创建服务实例
rag_service = RAGService()

# FastAPI应用
app = FastAPI(
    title="RAG服务",
    description="检索增强生成服务，提供文档管理和语义搜索功能",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# 依赖注入
def get_rag_service() -> RAGService:
    return rag_service

# API路由
@app.get("/", response_model=QueryResponse)
async def root():
    """根路径 - 服务信息"""
    return QueryResponse(
        success=True,
        data={
            "service": "RAG服务",
            "version": "1.0.0",
            "description": "检索增强生成服务",
            "endpoints": {
                "health": "/health",
                "search": "/search",
                "documents": "/documents",
                "upload": "/upload",
                "stats": "/stats",
                "docs": "/docs"
            }
        },
        message="RAG服务运行正常"
    )

@app.get("/health", response_model=QueryResponse)
async def health_check(service: RAGService = Depends(get_rag_service)):
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

@app.post("/search", response_model=SearchResponse)
async def search_documents(
    request: SearchRequest,
    service: RAGService = Depends(get_rag_service)
):
    """搜索文档"""
    try:
        start_time = datetime.now()
        results = await service.search_documents(
            query=request.query,
            limit=request.limit,
            filter_metadata=request.filter_metadata
        )
        end_time = datetime.now()
        search_time = (end_time - start_time).total_seconds()
        
        return SearchResponse(
            query=request.query,
            results=results,
            total_count=len(results),
            search_time=search_time
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"搜索失败: {str(e)}")

@app.post("/documents", response_model=DocumentUploadResponse)
async def add_document(
    title: str,
    content: str,
    metadata: Optional[Dict[str, Any]] = None,
    service: RAGService = Depends(get_rag_service)
):
    """添加文档"""
    try:
        doc_id = await service.add_document(title, content, metadata)
        return DocumentUploadResponse(
            document_id=doc_id,
            title=title,
            status="success",
            message="文档添加成功"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"添加文档失败: {str(e)}")

@app.get("/documents/{document_id}", response_model=QueryResponse)
async def get_document(
    document_id: str,
    service: RAGService = Depends(get_rag_service)
):
    """获取文档详情"""
    try:
        document = await service.get_document(document_id)
        if not document:
            raise HTTPException(status_code=404, detail=f"文档未找到: {document_id}")
        
        return QueryResponse(
            success=True,
            data=document.model_dump(),
            message="文档获取成功"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取文档失败: {str(e)}")

@app.put("/documents/{document_id}", response_model=QueryResponse)
async def update_document(
    document_id: str,
    title: Optional[str] = None,
    content: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None,
    service: RAGService = Depends(get_rag_service)
):
    """更新文档"""
    try:
        success = await service.update_document(document_id, title, content, metadata)
        if not success:
            raise HTTPException(status_code=404, detail=f"文档未找到: {document_id}")
        
        return QueryResponse(
            success=True,
            data={"document_id": document_id},
            message="文档更新成功"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"更新文档失败: {str(e)}")

@app.delete("/documents/{document_id}", response_model=QueryResponse)
async def delete_document(
    document_id: str,
    service: RAGService = Depends(get_rag_service)
):
    """删除文档"""
    try:
        success = await service.delete_document(document_id)
        if not success:
            raise HTTPException(status_code=404, detail=f"文档未找到: {document_id}")
        
        return QueryResponse(
            success=True,
            data={"document_id": document_id},
            message="文档删除成功"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"删除文档失败: {str(e)}")

@app.post("/enhance-context", response_model=ContextEnhancementResponse)
async def enhance_context(
    request: ContextEnhancementRequest,
    service: RAGService = Depends(get_rag_service)
):
    """增强上下文"""
    try:
        result = await service.enhance_context(
            query=request.query,
            context_documents=request.context_documents,
            max_context_length=request.max_context_length
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"上下文增强失败: {str(e)}")

@app.get("/stats", response_model=QueryResponse)
async def get_stats(service: RAGService = Depends(get_rag_service)):
    """获取统计信息"""
    try:
        stats = await service.get_collection_stats()
        return QueryResponse(
            success=True,
            data=stats,
            message="统计信息获取成功"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取统计信息失败: {str(e)}")

@app.get("/model-status", response_model=QueryResponse)
async def get_model_status(service: RAGService = Depends(get_rag_service)):
    """获取模型状态信息"""
    try:
        model_info = service._load_model_info()
        is_model_loaded = service.embedding_model is not None
        
        # 测试当前模型性能
        if is_model_loaded:
            try:
                test_texts = ["火灾救援", "安全措施", "紧急疏散"]
                start_time = datetime.now()
                embeddings = service._get_embeddings(test_texts)
                end_time = datetime.now()
                processing_time = (end_time - start_time).total_seconds()
                
                model_status = {
                    "loaded": True,
                    "model_name": model_info.get('model_name', 'unknown'),
                    "last_success": model_info.get('last_attempt', 'unknown'),
                    "processing_time": f"{processing_time:.3f}s",
                    "embedding_dimension": len(embeddings[0]) if embeddings else 0,
                    "test_samples": len(embeddings)
                }
            except Exception as e:
                model_status = {
                    "loaded": True,
                    "model_name": model_info.get('model_name', 'unknown'),
                    "last_success": model_info.get('last_attempt', 'unknown'),
                    "error": f"模型测试失败: {str(e)}"
                }
        else:
            model_status = {
                "loaded": False,
                "fallback_mode": True,
                "last_attempt": model_info.get('last_attempt', 'unknown'),
                "last_error": model_info.get('error', 'unknown')
            }
        
        return QueryResponse(
            success=True,
            data=model_status,
            message="模型状态获取成功"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取模型状态失败: {str(e)}")

@app.post("/reload-model", response_model=QueryResponse)
async def reload_model(service: RAGService = Depends(get_rag_service)):
    """重新加载嵌入模型"""
    try:
        logger.info("开始重新加载嵌入模型...")
        service._load_embedding_model()
        
        is_loaded = service.embedding_model is not None
        status = "成功" if is_loaded else "失败，使用备用方案"
        
        return QueryResponse(
            success=is_loaded,
            data={
                "model_loaded": is_loaded,
                "status": status,
                "timestamp": datetime.now().isoformat()
            },
            message=f"模型重新加载{status}"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"重新加载模型失败: {str(e)}")

# 启动和关闭事件
@app.on_event("startup")
async def startup_event():
    """应用启动事件"""
    logger.info("RAG服务启动中...")
    try:
        is_healthy = await rag_service.test_connection()
        if is_healthy:
            logger.info("RAG服务启动成功")
        else:
            logger.warning("RAG服务启动，但数据库连接异常")
    except Exception as e:
        logger.error(f"RAG服务启动失败: {str(e)}")

@app.on_event("shutdown")
async def shutdown_event():
    """应用关闭事件"""
    logger.info("RAG服务关闭中...")
    logger.info("RAG服务已关闭")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=3000)
