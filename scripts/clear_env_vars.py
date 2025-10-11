#!/usr/bin/env python3
"""
清理环境变量脚本
清除可能冲突的环境变量设置
"""

import os
import sys

def clear_environment_variables():
    """清理环境变量"""
    print("清理环境变量...")
    
    # 需要清理的环境变量
    env_vars_to_clear = [
        'OLLAMA_HOST',
        'OLLAMA_PORT', 
        'OLLAMA_MODEL',
        'RAG_SERVICE_HOST',
        'RAG_SERVICE_PORT',
        'CHROMA_HOST',
        'CHROMA_PORT',
        'NEO4J_HOST',
        'NEO4J_PORT',
        'REDIS_HOST',
        'REDIS_PORT'
    ]
    
    cleared_vars = []
    for var in env_vars_to_clear:
        if var in os.environ:
            del os.environ[var]
            cleared_vars.append(var)
            print(f"  [OK] 已清理: {var}")
    
    if cleared_vars:
        print(f"\n清理了 {len(cleared_vars)} 个环境变量")
    else:
        print("  没有需要清理的环境变量")
    
    # 设置正确的默认值
    print("\n设置正确的环境变量默认值...")
    os.environ['OLLAMA_HOST'] = 'localhost'
    os.environ['OLLAMA_PORT'] = '11434'
    os.environ['RAG_SERVICE_PORT'] = '8008'
    os.environ['CHROMA_HOST'] = 'localhost'
    os.environ['CHROMA_PORT'] = '8007'
    os.environ['NEO4J_HOST'] = 'localhost'
    os.environ['NEO4J_PORT'] = '7687'
    os.environ['REDIS_HOST'] = 'localhost'
    os.environ['REDIS_PORT'] = '6379'
    
    print("  环境变量设置完成")
    
    # 验证设置
    print("\n验证环境变量设置...")
    for var in ['OLLAMA_HOST', 'OLLAMA_PORT', 'RAG_SERVICE_PORT']:
        value = os.environ.get(var, 'NOT_SET')
        print(f"  {var} = {value}")

if __name__ == "__main__":
    clear_environment_variables()
    print("\n环境变量清理完成！")
