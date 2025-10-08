#!/usr/bin/env python3
"""
导入知识图谱示例数据到Neo4j
"""

import asyncio
import logging
import sys
from pathlib import Path
from neo4j import GraphDatabase

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from shared.config import get_config

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def import_kg_data():
    """导入知识图谱数据"""
    config = get_config()
    
    try:
        # 连接Neo4j
        driver = GraphDatabase.driver(
            config.database.neo4j_uri,
            auth=(config.database.neo4j_user, config.database.neo4j_password)
        )
        
        # 读取Cypher文件
        cypher_file = Path(__file__).parent.parent / "data" / "knowledge_base" / "sample_kg_data.cypher"
        
        if not cypher_file.exists():
            logger.error(f"Cypher文件不存在: {cypher_file}")
            return False
        
        with open(cypher_file, 'r', encoding='utf-8') as f:
            cypher_script = f.read()
        
        # 执行Cypher脚本
        with driver.session() as session:
            # 先清空现有数据（可选）
            logger.info("清空现有数据...")
            session.run("MATCH (n) DETACH DELETE n")
            
            # 执行导入脚本
            logger.info("导入知识图谱数据...")
            session.run(cypher_script)
            
            # 验证数据导入
            result = session.run("MATCH (n) RETURN count(n) as node_count")
            node_count = result.single()["node_count"]
            logger.info(f"成功导入 {node_count} 个节点")
            
            # 统计各类节点
            result = session.run("""
                MATCH (n)
                RETURN labels(n)[0] as label, count(n) as count
                ORDER BY count DESC
            """)
            
            logger.info("节点统计:")
            for record in result:
                logger.info(f"  {record['label']}: {record['count']} 个")
        
        driver.close()
        logger.info("知识图谱数据导入完成!")
        return True
        
    except Exception as e:
        logger.error(f"导入数据失败: {str(e)}")
        return False

if __name__ == "__main__":
    success = import_kg_data()
    exit(0 if success else 1)
