#!/usr/bin/env python3
"""
导入Neo4j完整数据的脚本
分批执行语句以避免语法错误
"""

import sys
import os
from pathlib import Path
from neo4j import GraphDatabase
import logging

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class Neo4jDataImporter:
    def __init__(self):
        self.uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
        self.user = os.getenv("NEO4J_USER", "neo4j")
        self.password = os.getenv("NEO4J_PASSWORD", "password")
        self.driver = None
    
    def connect(self):
        """连接到Neo4j"""
        logger.info(f"连接到Neo4j: {self.uri}")
        self.driver = GraphDatabase.driver(self.uri, auth=(self.user, self.password))
    
    def close(self):
        """关闭连接"""
        if self.driver:
            self.driver.close()
            logger.info("已关闭Neo4j连接")
    
    def clear_database(self):
        """清空数据库"""
        logger.info("清空现有数据...")
        with self.driver.session() as session:
            session.run("MATCH (n) DETACH DELETE n")
        logger.info("数据库已清空")
    
    def import_file(self, file_path):
        """导入Cypher文件"""
        logger.info(f"读取文件: {file_path}")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 按语句分割（处理注释和空行）
        lines = content.split('\n')
        statements = []
        current_statement = []
        
        for line in lines:
            # 跳过注释和空行
            line = line.strip()
            if not line or line.startswith('//'):
                if current_statement:
                    # 保存当前语句
                    stmt = ' '.join(current_statement)
                    if stmt:
                        statements.append(stmt)
                    current_statement = []
                continue
            
            current_statement.append(line)
            
            # 如果行以分号结尾，这是一个完整的语句
            if line.endswith(';'):
                stmt = ' '.join(current_statement)
                if stmt:
                    statements.append(stmt)
                current_statement = []
        
        # 添加最后一个语句（如果有）
        if current_statement:
            stmt = ' '.join(current_statement)
            if stmt:
                statements.append(stmt)
        
        logger.info(f"找到 {len(statements)} 个语句")
        
        # 执行语句
        with self.driver.session() as session:
            for i, statement in enumerate(statements, 1):
                try:
                    # 移除末尾分号
                    statement = statement.rstrip(';')
                    if not statement:
                        continue
                    
                    session.run(statement)
                    
                    if i % 100 == 0:
                        logger.info(f"已执行 {i}/{len(statements)} 个语句")
                    
                except Exception as e:
                    logger.error(f"执行语句失败 (第{i}个): {str(e)}")
                    logger.error(f"语句内容: {statement[:100]}...")
                    # 继续执行其他语句
        
        logger.info("数据导入完成")
    
    def verify_data(self):
        """验证导入的数据"""
        logger.info("验证数据...")
        
        with self.driver.session() as session:
            # 统计各类节点
            result = session.run("""
                MATCH (n) 
                RETURN labels(n) as label, count(n) as count 
                ORDER BY count DESC
            """)
            
            logger.info("节点统计:")
            total_nodes = 0
            for record in result:
                label = record['label'][0] if record['label'] else 'Unknown'
                count = record['count']
                total_nodes += count
                logger.info(f"  {label}: {count}个节点")
            
            logger.info(f"总节点数: {total_nodes}")
            
            # 统计关系
            result = session.run("""
                MATCH ()-[r]->() 
                RETURN type(r) as type, count(r) as count 
                ORDER BY count DESC 
                LIMIT 10
            """)
            
            logger.info("关系统计 (前10种):")
            total_rels = 0
            for record in result:
                rel_type = record['type']
                count = record['count']
                total_rels += count
                logger.info(f"  {rel_type}: {count}个关系")
            
            result = session.run("MATCH ()-[r]->() RETURN count(r) as total")
            total_rels = result.single()['total']
            logger.info(f"总关系数: {total_rels}")
    
    def create_indexes(self):
        """创建索引"""
        logger.info("创建索引...")
        
        indexes = [
            "CREATE INDEX IF NOT EXISTS FOR (i:Item) ON (i.name)",
            "CREATE INDEX IF NOT EXISTS FOR (i:Item) ON (i.id)",
            "CREATE INDEX IF NOT EXISTS FOR (m:Material) ON (m.name)",
            "CREATE INDEX IF NOT EXISTS FOR (m:Material) ON (m.id)",
            "CREATE INDEX IF NOT EXISTS FOR (e:Environment) ON (e.type)",
            "CREATE INDEX IF NOT EXISTS FOR (e:Environment) ON (e.id)",
            "CREATE INDEX IF NOT EXISTS FOR (r:RescuePlan) ON (r.priority)",
            "CREATE INDEX IF NOT EXISTS FOR (r:RescuePlan) ON (r.id)",
        ]
        
        with self.driver.session() as session:
            for index_query in indexes:
                try:
                    session.run(index_query)
                    logger.info(f"  创建索引: {index_query[:60]}...")
                except Exception as e:
                    logger.warning(f"  索引创建失败: {str(e)}")
        
        logger.info("索引创建完成")
    
    def run(self, file_path, clear_first=False):
        """执行完整的导入流程"""
        try:
            self.connect()
            
            if clear_first:
                self.clear_database()
            
            self.import_file(file_path)
            self.create_indexes()
            self.verify_data()
            
            logger.info("✅ 数据导入成功！")
            
        except Exception as e:
            logger.error(f"❌ 导入失败: {str(e)}")
            sys.exit(1)
        finally:
            self.close()

def main():
    """主函数"""
    project_root = Path(__file__).parent.parent
    data_file = project_root / "data" / "knowledge_base" / "neo4j_sample_data.cypher"
    
    if not data_file.exists():
        logger.error(f"数据文件不存在: {data_file}")
        sys.exit(1)
    
    importer = Neo4jDataImporter()
    importer.run(data_file, clear_first=True)

if __name__ == "__main__":
    main()

