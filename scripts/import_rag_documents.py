"""
导入消防知识文档到 RAG 服务

这个脚本从 data/knowledge_base/rag_documents.json 读取文档并导入到 RAG 服务
"""
import asyncio
import json
import sys
from pathlib import Path
from typing import Dict, Any, List
import httpx
from datetime import datetime

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

# RAG 服务配置
RAG_SERVICE_URL = "http://localhost:3000"
RAG_TIMEOUT = 30.0


async def upload_document(client: httpx.AsyncClient, doc: Dict[str, Any]) -> Dict[str, Any]:
    """上传单个文档到 RAG 服务"""
    try:
        # 准备请求参数（作为 query parameters 和 form data）
        params = {
            "title": doc["title"],
            "content": doc["content"]
        }
        
        # 如果有 metadata，需要作为 JSON 字符串传递
        if doc.get("metadata"):
            params["metadata"] = json.dumps(doc["metadata"], ensure_ascii=False)
        
        # 调用上传接口（使用 POST 的 params）
        response = await client.post(
            f"{RAG_SERVICE_URL}/documents",
            params=params,
            timeout=RAG_TIMEOUT
        )
        response.raise_for_status()
        
        result = response.json()
        return {
            "success": True,
            "doc_id": doc["id"],
            "title": doc["title"],
            "result": result
        }
    except Exception as e:
        return {
            "success": False,
            "doc_id": doc["id"],
            "title": doc["title"],
            "error": str(e)
        }


async def import_documents():
    """导入所有文档"""
    print("=" * 80)
    print("消防知识文档导入工具")
    print("=" * 80)
    print()
    
    # 读取文档
    doc_file = Path(__file__).parent.parent / "data" / "knowledge_base" / "rag_documents.json"
    
    if not doc_file.exists():
        print(f"[ERROR] 文档文件不存在: {doc_file}")
        return False
    
    print(f"[INFO] 读取文档文件: {doc_file}")
    with open(doc_file, "r", encoding="utf-8") as f:
        documents = json.load(f)
    
    print(f"[OK] 找到 {len(documents)} 个文档")
    print()
    
    # 跳过健康检查，直接开始上传（Windows httpx 有时有问题）
    print("[INFO] 跳过健康检查，开始导入...")
    print()
    
    # 上传文档
    print("[INFO] 开始导入文档...")
    print("-" * 80)
    
    success_count = 0
    error_count = 0
    
    async with httpx.AsyncClient() as client:
        for i, doc in enumerate(documents, 1):
            print(f"[{i}/{len(documents)}] 上传: {doc['title'][:50]}...", end=" ")
            
            result = await upload_document(client, doc)
            
            if result["success"]:
                print("[OK]")
                success_count += 1
            else:
                print(f"[FAIL] - {result['error']}")
                error_count += 1
            
            # 避免请求过快
            await asyncio.sleep(0.1)
    
    print("-" * 80)
    print()
    
    # 打印统计信息
    print("[STATS] 导入统计:")
    print(f"  总计: {len(documents)} 个文档")
    print(f"  成功: {success_count} 个")
    print(f"  失败: {error_count} 个")
    print()
    
    # 检查导入后的统计信息
    print("[INFO] 检查导入结果...")
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{RAG_SERVICE_URL}/stats", timeout=5.0)
            response.raise_for_status()
            stats = response.json()
            
            if stats.get("success"):
                data = stats.get("data", {})
                total_docs = data.get("total_documents", 0)
                print(f"[OK] RAG 数据库现有 {total_docs} 个文档")
    except Exception as e:
        print(f"[WARN] 无法获取统计信息: {e}")
    
    print()
    print("=" * 80)
    
    if error_count == 0:
        print("[SUCCESS] 所有文档导入成功！")
        return True
    else:
        print(f"[WARN] 导入完成，但有 {error_count} 个文档失败")
        return False


def main():
    """主函数"""
    try:
        result = asyncio.run(import_documents())
        sys.exit(0 if result else 1)
    except KeyboardInterrupt:
        print("\n\n[WARN] 导入被用户中断")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n[ERROR] 导入失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

