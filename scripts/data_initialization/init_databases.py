#!/usr/bin/env python3
"""
数据库初始化脚本
用于初始化Neo4j知识图谱和ChromaDB向量数据库
"""

import json
import asyncio
import sys
import os
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

from neo4j import GraphDatabase
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DatabaseInitializer:
    def __init__(self):
        # Neo4j配置
        self.neo4j_uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
        self.neo4j_user = os.getenv("NEO4J_USER", "neo4j")
        self.neo4j_password = os.getenv("NEO4J_PASSWORD", "password")
        
        # ChromaDB配置
        self.chroma_host = os.getenv("CHROMA_HOST", "localhost")
        self.chroma_port = int(os.getenv("CHROMA_PORT", "8007"))
        
        # 嵌入模型
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
    
    async def init_neo4j(self):
        """初始化Neo4j知识图谱"""
        logger.info("开始初始化Neo4j知识图谱...")
        
        try:
            driver = GraphDatabase.driver(
                self.neo4j_uri, 
                auth=(self.neo4j_user, self.neo4j_password)
            )
            
            # 读取Cypher脚本
            cypher_file = project_root / "data" / "knowledge_base" / "neo4j_sample_data.cypher"
            with open(cypher_file, 'r', encoding='utf-8') as f:
                cypher_script = f.read()
            
            # 执行Cypher脚本
            with driver.session() as session:
                # 分割并执行每个语句
                statements = [stmt.strip() for stmt in cypher_script.split(';') if stmt.strip()]
                for statement in statements:
                    if statement:
                        session.run(statement)
                        logger.info(f"执行语句: {statement[:50]}...")
            
            driver.close()
            logger.info("Neo4j知识图谱初始化完成")
            
        except Exception as e:
            logger.error(f"Neo4j初始化失败: {str(e)}")
            raise
    
    async def init_chromadb(self):
        """初始化ChromaDB向量数据库"""
        logger.info("开始初始化ChromaDB向量数据库...")
        
        try:
            # 连接ChromaDB
            client = chromadb.HttpClient(
                host=self.chroma_host,
                port=self.chroma_port
            )
            
            # 创建或获取集合
            collection = client.get_or_create_collection(
                name="fire_rescue_knowledge",
                metadata={"description": "火灾救援知识库"}
            )
            
            # 读取文档数据
            docs_file = project_root / "data" / "knowledge_base" / "rag_documents.json"
            with open(docs_file, 'r', encoding='utf-8') as f:
                documents = json.load(f)
            
            # 准备数据
            ids = []
            documents_text = []
            metadatas = []
            embeddings = []
            
            for doc in documents:
                ids.append(doc['id'])
                documents_text.append(doc['content'])
                metadatas.append(doc['metadata'])
                
                # 生成嵌入向量
                embedding = self.embedding_model.encode(doc['content']).tolist()
                embeddings.append(embedding)
            
            # 批量添加到ChromaDB
            collection.add(
                ids=ids,
                documents=documents_text,
                metadatas=metadatas,
                embeddings=embeddings
            )
            
            logger.info(f"ChromaDB向量数据库初始化完成，添加了{len(documents)}个文档")
            
        except Exception as e:
            logger.error(f"ChromaDB初始化失败: {str(e)}")
            raise
    
    async def verify_data(self):
        """验证数据是否正确加载"""
        logger.info("开始验证数据...")
        
        try:
            # 验证Neo4j
            driver = GraphDatabase.driver(
                self.neo4j_uri, 
                auth=(self.neo4j_user, self.neo4j_password)
            )
            
            with driver.session() as session:
                # 检查节点数量
                item_count = session.run("MATCH (n:Item) RETURN count(n) as count").single()['count']
                material_count = session.run("MATCH (n:Material) RETURN count(n) as count").single()['count']
                plan_count = session.run("MATCH (n:RescuePlan) RETURN count(n) as count").single()['count']
                
                logger.info(f"Neo4j数据验证: 物品节点{item_count}个, 材质节点{material_count}个, 救援方案{plan_count}个")
            
            driver.close()
            
            # 验证ChromaDB
            client = chromadb.HttpClient(host=self.chroma_host, port=self.chroma_port)
            collection = client.get_collection("fire_rescue_knowledge")
            doc_count = collection.count()
            
            logger.info(f"ChromaDB数据验证: 文档{doc_count}个")
            
            logger.info("数据验证完成")
            
        except Exception as e:
            logger.error(f"数据验证失败: {str(e)}")
            raise
    
    async def run(self):
        """运行完整的初始化流程"""
        logger.info("开始数据库初始化流程...")
        
        try:
            # 初始化Neo4j
            await self.init_neo4j()
            
            # 初始化ChromaDB
            await self.init_chromadb()
            
            # 验证数据
            await self.verify_data()
            
            logger.info("数据库初始化完成！")
            
        except Exception as e:
            logger.error(f"数据库初始化失败: {str(e)}")
            sys.exit(1)

async def main():
    """主函数"""
    initializer = DatabaseInitializer()
    await initializer.run()

if __name__ == "__main__":
    asyncio.run(main())
