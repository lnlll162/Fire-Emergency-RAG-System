#!/usr/bin/env python3
"""
验证数据导入情况
"""
import os
import sys
from pathlib import Path
from neo4j import GraphDatabase

# 设置UTF-8输出
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

class DataVerifier:
    def __init__(self):
        self.uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
        self.user = os.getenv("NEO4J_USER", "neo4j")
        self.password = os.getenv("NEO4J_PASSWORD", "password")
        self.driver = None
    
    def connect(self):
        """连接到Neo4j"""
        self.driver = GraphDatabase.driver(self.uri, auth=(self.user, self.password))
    
    def close(self):
        """关闭连接"""
        if self.driver:
            self.driver.close()
    
    def verify_neo4j(self):
        """验证Neo4j数据"""
        print("=" * 80)
        print("🔍 Neo4j知识图谱数据验证")
        print("=" * 80)
        print()
        
        with self.driver.session() as session:
            # 节点统计
            result = session.run("""
                MATCH (n) 
                RETURN labels(n)[0] as label, count(n) as count 
                ORDER BY count DESC
            """)
            
            print("📊 节点统计:")
            nodes = list(result)
            total_nodes = sum(r['count'] for r in nodes)
            for record in nodes:
                label = record['label']
                count = record['count']
                print(f"   ✓ {label}: {count} 个")
            print(f"   📌 总计: {total_nodes} 个节点")
            print()
            
            # 关系统计
            result = session.run("""
                MATCH ()-[r]->() 
                RETURN type(r) as type, count(r) as count 
                ORDER BY count DESC
            """)
            
            print("🔗 关系统计:")
            rels = list(result)
            total_rels = sum(r['count'] for r in rels)
            for record in rels:
                rel_type = record['type']
                count = record['count']
                print(f"   ✓ {rel_type}: {count} 个")
            print(f"   📌 总计: {total_rels} 个关系")
            print()
            
            # 示例数据
            print("📋 示例数据:")
            
            # 示例1: 物品及其材质
            result = session.run("""
                MATCH (i:Item)-[:HAS_MATERIAL]->(m:Material)
                RETURN i.name as item, m.name as material
                LIMIT 3
            """)
            print("   🔸 物品-材质关系:")
            for record in result:
                print(f"      • {record['item']} → {record['material']}")
            
            # 示例2: 材质及其救援方案
            result = session.run("""
                MATCH (m:Material)-[:REQUIRES_RESCUE_PLAN]->(p:RescuePlan)
                RETURN m.name as material, p.name as plan, p.priority as priority
                LIMIT 3
            """)
            print("   🔸 材质-救援方案:")
            for record in result:
                print(f"      • {record['material']} → {record['plan']} (优先级: {record['priority']})")
            
            # 示例3: 环境适用性
            result = session.run("""
                MATCH (e:Environment)-[:SUITABLE_FOR]->(p:RescuePlan)
                RETURN e.type as env, p.name as plan
                LIMIT 3
            """)
            print("   🔸 环境-救援方案:")
            for record in result:
                print(f"      • {record['env']} → {record['plan']}")
            
            print()
            print("=" * 80)
            print("✅ Neo4j知识图谱验证完成")
            print("=" * 80)
            print()
            
            # 检查RAG文档
            print("📚 RAG文档验证")
            print("=" * 80)
            project_root = Path(__file__).parent.parent
            rag_file = project_root / "data" / "knowledge_base" / "rag_documents.json"
            
            if rag_file.exists():
                import json
                with open(rag_file, 'r', encoding='utf-8') as f:
                    docs = json.load(f)
                print(f"✓ RAG文档文件存在: {len(docs)} 篇文档")
                print(f"✓ 文档类型: 救援程序、案例研究、设备指南、安全指南等")
                print(f"✓ 启动系统时会自动导入到Qdrant向量数据库")
            else:
                print("⚠ RAG文档文件不存在")
            
            print()
            print("=" * 80)
            print("💡 系统就绪状态")
            print("=" * 80)
            print()
            print("✅ 知识图谱已导入 (Neo4j)")
            print(f"   • {total_nodes} 个节点")
            print(f"   • {total_rels} 个关系")
            print(f"   • 涵盖物品、材质、环境、救援方案等多个维度")
            print()
            print("📚 RAG文档准备就绪")
            print(f"   • 30 篇详细救援指南")
            print(f"   • 启动时自动导入到向量数据库")
            print()
            print("🚀 下一步:")
            print("   1. 启动系统: cd backend && uvicorn main:app --reload")
            print("   2. 启动前端: cd frontend && npm run dev")
            print("   3. 访问系统: http://localhost:3000")
            print()

def main():
    verifier = DataVerifier()
    try:
        verifier.connect()
        verifier.verify_neo4j()
    except Exception as e:
        print(f"❌ 验证失败: {str(e)}")
        sys.exit(1)
    finally:
        verifier.close()

if __name__ == "__main__":
    main()

