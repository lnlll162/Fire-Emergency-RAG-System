#!/usr/bin/env python3
"""
简单数据添加脚本
用于快速添加新的物品、材质、环境和救援方案
"""

import json
import asyncio
from neo4j import GraphDatabase
import chromadb
from sentence_transformers import SentenceTransformer

class DataAdder:
    def __init__(self):
        self.neo4j_uri = "bolt://localhost:7687"
        self.neo4j_user = "neo4j"
        self.neo4j_password = "password"
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
    
    def add_new_item(self, name, material, category, flammability, toxicity):
        """添加新物品到Neo4j"""
        driver = GraphDatabase.driver(self.neo4j_uri, auth=(self.neo4j_user, self.neo4j_password))
        
        with driver.session() as session:
            # 生成新ID
            result = session.run("MATCH (i:Item) RETURN count(i) as count")
            count = result.single()['count']
            new_id = f"item_{str(count + 1).zfill(3)}"
            
            # 创建物品节点
            query = """
            CREATE (item:Item {
                id: $id,
                name: $name,
                material: $material,
                flammability: $flammability,
                toxicity: $toxicity,
                category: $category
            })
            """
            session.run(query, 
                       id=new_id, 
                       name=name, 
                       material=material, 
                       flammability=flammability, 
                       toxicity=toxicity, 
                       category=category)
            
            print(f"✅ 成功添加物品: {name} (ID: {new_id})")
        
        driver.close()
    
    def add_new_document(self, title, content, document_type, category, priority):
        """添加新文档到ChromaDB"""
        client = chromadb.HttpClient(host="localhost", port=8007)
        collection = client.get_collection("fire_rescue_knowledge")
        
        # 生成新ID
        doc_count = collection.count()
        new_id = f"doc_{str(doc_count + 1).zfill(3)}"
        
        # 生成嵌入向量
        embedding = self.embedding_model.encode(content).tolist()
        
        # 准备元数据
        metadata = {
            "document_type": document_type,
            "category": category,
            "priority": priority,
            "tags": [category, "火灾", "救援"]
        }
        
        # 添加到ChromaDB
        collection.add(
            ids=[new_id],
            documents=[content],
            metadatas=[metadata],
            embeddings=[embedding]
        )
        
        print(f"✅ 成功添加文档: {title} (ID: {new_id})")
    
    def add_new_rescue_plan(self, name, priority, steps, equipment, warnings):
        """添加新救援方案到Neo4j"""
        driver = GraphDatabase.driver(self.neo4j_uri, auth=(self.neo4j_user, self.neo4j_password))
        
        with driver.session() as session:
            # 生成新ID
            result = session.run("MATCH (r:RescuePlan) RETURN count(r) as count")
            count = result.single()['count']
            new_id = f"plan_{str(count + 1).zfill(3)}"
            
            # 创建救援方案节点
            query = """
            CREATE (plan:RescuePlan {
                id: $id,
                name: $name,
                priority: $priority,
                steps: $steps,
                equipment: $equipment,
                warnings: $warnings
            })
            """
            session.run(query, 
                       id=new_id, 
                       name=name, 
                       priority=priority, 
                       steps=steps, 
                       equipment=equipment, 
                       warnings=warnings)
            
            print(f"✅ 成功添加救援方案: {name} (ID: {new_id})")
        
        driver.close()

def main():
    """主函数 - 示例用法"""
    adder = DataAdder()
    
    print("🔥 火灾应急RAG系统 - 数据添加工具")
    print("=" * 50)
    
    # 示例：添加新物品
    print("\n1. 添加新物品...")
    adder.add_new_item(
        name="空调",
        material="金属",
        category="电器",
        flammability="不燃",
        toxicity="低"
    )
    
    # 示例：添加新文档
    print("\n2. 添加新文档...")
    adder.add_new_document(
        title="空调火灾救援指南",
        content="空调火灾救援要点：1. 立即切断电源；2. 使用干粉灭火器；3. 注意防止触电...",
        document_type="rescue_procedure",
        category="电器火灾",
        priority="高"
    )
    
    # 示例：添加新救援方案
    print("\n3. 添加新救援方案...")
    adder.add_new_rescue_plan(
        name="空调火灾救援",
        priority="高",
        steps=["切断电源", "使用干粉灭火器", "确保安全距离"],
        equipment=["干粉灭火器", "绝缘手套"],
        warnings=["注意触电危险", "确保电源已切断"]
    )
    
    print("\n✅ 数据添加完成！")

if __name__ == "__main__":
    main()
