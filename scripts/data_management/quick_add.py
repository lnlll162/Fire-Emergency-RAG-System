#!/usr/bin/env python3
"""
快速数据添加脚本
提供简单的命令行界面来添加数据
"""

import json
import sys
from pathlib import Path

def add_item_to_cypher():
    """添加物品到Cypher文件"""
    cypher_file = Path("data/knowledge_base/neo4j_sample_data.cypher")
    
    print("🔥 添加新物品到知识图谱")
    print("=" * 40)
    
    # 获取用户输入
    name = input("物品名称: ")
    material = input("材质: ")
    category = input("分类: ")
    flammability = input("易燃性 (易燃/不燃/难燃): ")
    toxicity = input("毒性 (低/中/高): ")
    weight = input("重量 (可选): ") or "未知"
    size = input("尺寸 (可选): ") or "未知"
    
    # 生成新ID (简单递增)
    with open(cypher_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 计算现有物品数量
    item_count = content.count("CREATE (item")
    new_id = f"item_{str(item_count + 1).zfill(3)}"
    
    # 生成Cypher语句
    cypher_statement = f"""
CREATE (item{item_count + 1}:Item {{
    id: '{new_id}',
    name: '{name}',
    material: '{material}',
    flammability: '{flammability}',
    toxicity: '{toxicity}',
    category: '{category}',
    weight: '{weight}',
    size: '{size}'
}})
"""
    
    # 添加到文件末尾
    with open(cypher_file, 'a', encoding='utf-8') as f:
        f.write(cypher_statement)
    
    print(f"✅ 成功添加物品: {name} (ID: {new_id})")
    print(f"📝 Cypher语句已添加到文件末尾")

def add_document_to_json():
    """添加文档到JSON文件"""
    json_file = Path("data/knowledge_base/rag_documents.json")
    
    print("📄 添加新文档到知识库")
    print("=" * 40)
    
    # 获取用户输入
    title = input("文档标题: ")
    content = input("文档内容: ")
    document_type = input("文档类型 (rescue_procedure/case_study/equipment_guide): ")
    category = input("分类: ")
    priority = input("优先级 (低/中/高/紧急): ")
    
    # 读取现有数据
    with open(json_file, 'r', encoding='utf-8') as f:
        documents = json.load(f)
    
    # 生成新ID
    new_id = f"doc_{str(len(documents) + 1).zfill(3)}"
    
    # 创建新文档
    new_document = {
        "id": new_id,
        "title": title,
        "content": content,
        "metadata": {
            "document_type": document_type,
            "category": category,
            "priority": priority,
            "tags": [category, "火灾", "救援"]
        },
        "created_at": "2024-01-15T15:00:00Z",
        "updated_at": "2024-01-15T15:00:00Z"
    }
    
    # 添加到列表
    documents.append(new_document)
    
    # 写回文件
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(documents, f, ensure_ascii=False, indent=2)
    
    print(f"✅ 成功添加文档: {title} (ID: {new_id})")

def add_sample_scenario():
    """添加示例场景"""
    json_file = Path("data/samples/user_input_samples.json")
    
    print("🎯 添加新测试场景")
    print("=" * 40)
    
    # 获取用户输入
    name = input("场景名称: ")
    description = input("场景描述: ")
    
    print("\n添加物品信息 (输入空行结束):")
    items = []
    while True:
        item_name = input("物品名称: ")
        if not item_name:
            break
        material = input("材质: ")
        quantity = int(input("数量: ") or "1")
        location = input("位置: ")
        flammability = input("易燃性: ")
        toxicity = input("毒性: ")
        
        items.append({
            "name": item_name,
            "material": material,
            "quantity": quantity,
            "location": location,
            "condition": "良好",
            "flammability": flammability,
            "toxicity": toxicity
        })
    
    # 环境信息
    print("\n环境信息:")
    env_type = input("环境类型 (室内/室外): ")
    area = input("区域类型 (住宅/商业/工业): ")
    floor = input("楼层 (可选): ") or None
    ventilation = input("通风情况: ")
    exits = int(input("出口数量: ") or "1")
    occupancy = int(input("人员数量: ") or "1")
    
    environment = {
        "type": env_type,
        "area": area,
        "floor": int(floor) if floor else None,
        "ventilation": ventilation,
        "exits": exits,
        "occupancy": occupancy,
        "building_type": "住宅楼",
        "fire_safety_equipment": ["干粉灭火器"],
        "special_conditions": ""
    }
    
    # 读取现有数据
    with open(json_file, 'r', encoding='utf-8') as f:
        samples = json.load(f)
    
    # 生成新ID
    new_id = f"sample_{str(len(samples) + 1).zfill(3)}"
    
    # 创建新样本
    new_sample = {
        "id": new_id,
        "name": name,
        "description": description,
        "items": items,
        "environment": environment,
        "additional_info": "",
        "urgency_level": "中",
        "expected_rescue_plan": "待生成"
    }
    
    # 添加到列表
    samples.append(new_sample)
    
    # 写回文件
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(samples, f, ensure_ascii=False, indent=2)
    
    print(f"✅ 成功添加场景: {name} (ID: {new_id})")

def main():
    """主菜单"""
    while True:
        print("\n🔥 火灾应急RAG系统 - 数据扩展工具")
        print("=" * 50)
        print("1. 添加新物品到知识图谱")
        print("2. 添加新文档到知识库")
        print("3. 添加新测试场景")
        print("4. 退出")
        
        choice = input("\n请选择操作 (1-4): ")
        
        if choice == "1":
            add_item_to_cypher()
        elif choice == "2":
            add_document_to_json()
        elif choice == "3":
            add_sample_scenario()
        elif choice == "4":
            print("👋 再见！")
            break
        else:
            print("❌ 无效选择，请重试")

if __name__ == "__main__":
    main()
