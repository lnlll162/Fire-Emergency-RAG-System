#!/usr/bin/env python3
"""
模型下载脚本
用于下载和缓存嵌入模型，解决网络连接问题
"""

import os
import sys
import logging
from pathlib import Path
from typing import List, Dict, Any
import json
from datetime import datetime

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

try:
    from sentence_transformers import SentenceTransformer
    import torch
except ImportError as e:
    print(f"❌ 缺少必要的依赖包: {e}")
    print("请运行: pip install sentence-transformers torch")
    sys.exit(1)

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ModelDownloader:
    """模型下载器"""
    
    def __init__(self):
        self.models_dir = Path("models/embeddings")
        self.models_dir.mkdir(parents=True, exist_ok=True)
        
        # 模型配置
        self.model_configs = [
            {
                'name': 'paraphrase-multilingual-MiniLM-L12-v2',
                'description': '多语言轻量级模型',
                'size': '~120MB',
                'priority': 1,
                'recommended': True
            },
            {
                'name': 'all-MiniLM-L6-v2',
                'description': '英文轻量级模型',
                'size': '~80MB',
                'priority': 2,
                'recommended': True
            },
            {
                'name': 'distiluse-base-multilingual-cased',
                'description': '多语言基础模型',
                'size': '~500MB',
                'priority': 3,
                'recommended': False
            },
            {
                'name': 'all-mpnet-base-v2',
                'description': '高性能英文模型',
                'size': '~400MB',
                'priority': 4,
                'recommended': False
            }
        ]
    
    def download_model(self, model_name: str) -> bool:
        """下载指定模型"""
        try:
            logger.info(f"开始下载模型: {model_name}")
            
            # 检查模型是否已存在
            model_path = self.models_dir / model_name
            if model_path.exists():
                logger.info(f"模型 {model_name} 已存在，跳过下载")
                return True
            
            # 下载模型
            logger.info(f"正在下载模型 {model_name}...")
            model = SentenceTransformer(model_name)
            
            # 测试模型
            test_text = "测试文本"
            embedding = model.encode([test_text])
            
            if embedding is not None and len(embedding) > 0:
                logger.info(f"✅ 模型 {model_name} 下载并测试成功")
                logger.info(f"模型维度: {embedding.shape[1]}")
                
                # 保存模型信息
                self._save_model_info(model_name, True)
                return True
            else:
                logger.error(f"❌ 模型 {model_name} 测试失败")
                return False
                
        except Exception as e:
            logger.error(f"❌ 下载模型 {model_name} 失败: {str(e)}")
            self._save_model_info(model_name, False, str(e))
            return False
    
    def download_recommended_models(self) -> Dict[str, bool]:
        """下载推荐的模型"""
        results = {}
        recommended_models = [m for m in self.model_configs if m['recommended']]
        
        logger.info("开始下载推荐的模型...")
        
        for model_config in recommended_models:
            model_name = model_config['name']
            logger.info(f"下载推荐模型: {model_name} ({model_config['description']})")
            results[model_name] = self.download_model(model_name)
        
        return results
    
    def download_all_models(self) -> Dict[str, bool]:
        """下载所有模型"""
        results = {}
        
        logger.info("开始下载所有模型...")
        
        for model_config in self.model_configs:
            model_name = model_config['name']
            logger.info(f"下载模型: {model_name} ({model_config['description']})")
            results[model_name] = self.download_model(model_name)
        
        return results
    
    def _save_model_info(self, model_name: str, success: bool, error: str = None):
        """保存模型信息"""
        info = {
            "model_name": model_name,
            "success": success,
            "timestamp": datetime.now().isoformat(),
            "error": error
        }
        
        info_file = self.models_dir / f"{model_name}_info.json"
        try:
            with open(info_file, 'w', encoding='utf-8') as f:
                json.dump(info, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.warning(f"保存模型信息失败: {str(e)}")
    
    def check_models(self) -> Dict[str, Dict[str, Any]]:
        """检查已下载的模型"""
        results = {}
        
        for model_config in self.model_configs:
            model_name = model_config['name']
            model_path = self.models_dir / model_name
            
            info = {
                "name": model_name,
                "description": model_config['description'],
                "size": model_config['size'],
                "downloaded": model_path.exists(),
                "recommended": model_config['recommended']
            }
            
            # 检查模型信息文件
            info_file = self.models_dir / f"{model_name}_info.json"
            if info_file.exists():
                try:
                    with open(info_file, 'r', encoding='utf-8') as f:
                        model_info = json.load(f)
                    info.update(model_info)
                except Exception as e:
                    logger.warning(f"读取模型信息失败: {str(e)}")
            
            results[model_name] = info
        
        return results
    
    def print_status(self):
        """打印模型状态"""
        models = self.check_models()
        
        print("\n" + "="*60)
        print("📊 模型下载状态")
        print("="*60)
        
        for model_name, info in models.items():
            status = "✅ 已下载" if info['downloaded'] else "❌ 未下载"
            recommended = "⭐ 推荐" if info['recommended'] else ""
            
            print(f"{model_name}")
            print(f"  状态: {status} {recommended}")
            print(f"  描述: {info['description']}")
            print(f"  大小: {info['size']}")
            
            if info.get('timestamp'):
                print(f"  时间: {info['timestamp']}")
            
            if info.get('error'):
                print(f"  错误: {info['error']}")
            
            print()
    
    def cleanup_failed_models(self):
        """清理失败的模型下载"""
        logger.info("清理失败的模型下载...")
        
        for model_config in self.model_configs:
            model_name = model_config['name']
            model_path = self.models_dir / model_name
            info_file = self.models_dir / f"{model_name}_info.json"
            
            # 如果模型目录存在但信息文件显示失败，则清理
            if model_path.exists() and info_file.exists():
                try:
                    with open(info_file, 'r', encoding='utf-8') as f:
                        info = json.load(f)
                    
                    if not info.get('success', False):
                        logger.info(f"清理失败的模型: {model_name}")
                        import shutil
                        shutil.rmtree(model_path, ignore_errors=True)
                        info_file.unlink(missing_ok=True)
                        
                except Exception as e:
                    logger.warning(f"清理模型 {model_name} 失败: {str(e)}")


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="模型下载脚本")
    parser.add_argument("--model", help="下载指定模型")
    parser.add_argument("--recommended", action="store_true", help="下载推荐模型")
    parser.add_argument("--all", action="store_true", help="下载所有模型")
    parser.add_argument("--check", action="store_true", help="检查模型状态")
    parser.add_argument("--cleanup", action="store_true", help="清理失败的模型")
    
    args = parser.parse_args()
    
    downloader = ModelDownloader()
    
    if args.check:
        downloader.print_status()
        return
    
    if args.cleanup:
        downloader.cleanup_failed_models()
        return
    
    if args.model:
        success = downloader.download_model(args.model)
        if success:
            print(f"✅ 模型 {args.model} 下载成功")
        else:
            print(f"❌ 模型 {args.model} 下载失败")
            sys.exit(1)
    
    elif args.recommended:
        results = downloader.download_recommended_models()
        success_count = sum(1 for success in results.values() if success)
        total_count = len(results)
        
        print(f"\n📊 推荐模型下载完成: {success_count}/{total_count}")
        downloader.print_status()
        
        if success_count == 0:
            sys.exit(1)
    
    elif args.all:
        results = downloader.download_all_models()
        success_count = sum(1 for success in results.values() if success)
        total_count = len(results)
        
        print(f"\n📊 所有模型下载完成: {success_count}/{total_count}")
        downloader.print_status()
        
        if success_count == 0:
            sys.exit(1)
    
    else:
        print("请指定操作参数:")
        print("  --check        检查模型状态")
        print("  --recommended  下载推荐模型")
        print("  --all          下载所有模型")
        print("  --model NAME   下载指定模型")
        print("  --cleanup      清理失败的模型")


if __name__ == "__main__":
    main()
