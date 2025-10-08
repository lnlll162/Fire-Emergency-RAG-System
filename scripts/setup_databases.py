#!/usr/bin/env python3
"""
数据库初始化脚本
用于初始化所有数据库和验证连接
"""

import asyncio
import sys
import os
from pathlib import Path
import logging

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from shared.config import get_config
from shared.service_registry import ServiceRegistry
import asyncpg
import redis.asyncio as redis
from neo4j import GraphDatabase
import chromadb
from chromadb.config import Settings
import httpx

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class DatabaseInitializer:
    """数据库初始化器"""
    
    def __init__(self):
        self.config = get_config()
        self.results = {}
    
    async def initialize_all(self):
        """初始化所有数据库"""
        logger.info("开始初始化所有数据库...")
        
        tasks = [
            self.init_postgresql(),
            self.init_redis(),
            self.init_neo4j(),
            self.init_chromadb(),
            self.init_ollama()
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # 处理结果
        db_names = ["PostgreSQL", "Redis", "Neo4j", "ChromaDB", "Ollama"]
        for db_name, result in zip(db_names, results):
            if isinstance(result, Exception):
                logger.error(f"{db_name} 初始化失败: {str(result)}")
                self.results[db_name] = False
            else:
                logger.info(f"{db_name} 初始化成功")
                self.results[db_name] = True
        
        # 输出总结
        self.print_summary()
        
        return all(self.results.values())
    
    async def init_postgresql(self):
        """初始化PostgreSQL"""
        logger.info("初始化PostgreSQL...")
        
        try:
            # 尝试多种连接方式
            connection_urls = [
                self.config.database.postgres_url,
                f"postgresql://postgres:password@127.0.0.1:5432/fire_emergency",
                f"postgresql://postgres:password@localhost:5432/fire_emergency"
            ]
            
            conn = None
            for i, url in enumerate(connection_urls, 1):
                try:
                    logger.info(f"尝试连接方式 {i}: {url}")
                    conn = await asyncpg.connect(url, timeout=10)
                    logger.info(f"PostgreSQL连接成功 (方式 {i})")
                    break
                except Exception as e:
                    logger.warning(f"连接方式 {i} 失败: {str(e)}")
                    if i == len(connection_urls):
                        raise e
                    continue
            
            if conn is None:
                raise Exception("所有连接方式都失败了")
            
            # 检查表是否存在
            tables = await conn.fetch("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
            """)
            
            if not tables:
                logger.info("PostgreSQL数据库为空，需要运行初始化脚本")
                # 这里可以运行初始化SQL脚本
                # await self.run_postgresql_init_script(conn)
            else:
                logger.info(f"PostgreSQL数据库已存在 {len(tables)} 个表")
            
            await conn.close()
            return True
            
        except Exception as e:
            logger.error(f"PostgreSQL初始化失败: {str(e)}")
            # 不抛出异常，而是返回False，让其他数据库继续初始化
            logger.warning("PostgreSQL连接失败，但其他服务可以继续运行")
            return False
    
    async def init_redis(self):
        """初始化Redis"""
        logger.info("初始化Redis...")
        
        try:
            redis_client = redis.from_url(
                self.config.database.redis_url,
                decode_responses=True
            )
            
            # 测试连接
            await redis_client.ping()
            
            # 设置测试键
            await redis_client.set("test_key", "test_value", ex=60)
            value = await redis_client.get("test_key")
            
            if value != "test_value":
                raise Exception("Redis测试失败")
            
            await redis_client.delete("test_key")
            await redis_client.close()
            
            return True
            
        except Exception as e:
            logger.error(f"Redis初始化失败: {str(e)}")
            raise
    
    async def init_neo4j(self):
        """初始化Neo4j"""
        logger.info("初始化Neo4j...")
        
        try:
            driver = GraphDatabase.driver(
                self.config.database.neo4j_uri,
                auth=(self.config.database.neo4j_user, self.config.database.neo4j_password)
            )
            
            # 测试连接
            with driver.session() as session:
                result = session.run("RETURN 1 as test")
                record = result.single()
                if record["test"] != 1:
                    raise Exception("Neo4j测试失败")
            
            # 检查是否有数据
            with driver.session() as session:
                result = session.run("MATCH (n) RETURN count(n) as count")
                record = result.single()
                count = record["count"]
                
                if count == 0:
                    logger.info("Neo4j数据库为空，需要导入数据")
                    # 这里可以运行数据导入脚本
                    # await self.import_neo4j_data(driver)
                else:
                    logger.info(f"Neo4j数据库已存在 {count} 个节点")
            
            driver.close()
            return True
            
        except Exception as e:
            logger.error(f"Neo4j初始化失败: {str(e)}")
            raise
    
    async def init_chromadb(self):
        """初始化ChromaDB"""
        logger.info("初始化ChromaDB...")
        
        try:
            client = chromadb.HttpClient(
                host=self.config.database.chroma_host,
                port=self.config.database.chroma_port
            )
            
            # 测试连接
            client.heartbeat()
            
            # 获取或创建集合
            collection_name = self.config.database.chroma_collection_name
            try:
                collection = client.get_collection(collection_name)
                logger.info(f"ChromaDB集合 '{collection_name}' 已存在")
            except:
                collection = client.create_collection(
                    name=collection_name,
                    metadata={"description": "火灾救援知识库"}
                )
                logger.info(f"ChromaDB集合 '{collection_name}' 创建成功")
            
            # 检查集合中的文档数量
            count = collection.count()
            if count == 0:
                logger.info("ChromaDB集合为空，需要导入文档")
                # 这里可以运行文档导入脚本
                # await self.import_chromadb_documents(collection)
            else:
                logger.info(f"ChromaDB集合已存在 {count} 个文档")
            
            return True
            
        except Exception as e:
            logger.error(f"ChromaDB初始化失败: {str(e)}")
            raise
    
    async def init_ollama(self):
        """初始化Ollama"""
        logger.info("初始化Ollama...")
        
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                # 测试连接
                response = await client.get(
                    f"{self.config.database.ollama_url}/api/tags"
                )
                
                if response.status_code != 200:
                    raise Exception(f"Ollama API返回错误: {response.status_code}")
                
                # 检查模型是否存在
                models = response.json().get("models", [])
                model_name = self.config.database.ollama_model
                
                model_exists = any(model["name"].startswith(model_name) for model in models)
                
                if not model_exists:
                    logger.warning(f"Ollama模型 '{model_name}' 不存在，需要下载")
                    # 这里可以触发模型下载
                    # await self.download_ollama_model(model_name)
                else:
                    logger.info(f"Ollama模型 '{model_name}' 已存在")
                
                return True
                
        except Exception as e:
            logger.error(f"Ollama初始化失败: {str(e)}")
            raise
    
    def print_summary(self):
        """打印初始化总结"""
        logger.info("\n" + "="*50)
        logger.info("数据库初始化总结")
        logger.info("="*50)
        
        for db_name, success in self.results.items():
            status = "✅ 成功" if success else "❌ 失败"
            logger.info(f"{db_name}: {status}")
        
        all_success = all(self.results.values())
        overall_status = "✅ 所有数据库初始化成功" if all_success else "❌ 部分数据库初始化失败"
        logger.info(f"\n总体状态: {overall_status}")
        logger.info("="*50)


async def main():
    """主函数"""
    logger.info("开始数据库初始化...")
    
    initializer = DatabaseInitializer()
    success = await initializer.initialize_all()
    
    if success:
        logger.info("数据库初始化完成！")
        sys.exit(0)
    else:
        logger.error("数据库初始化失败！")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
