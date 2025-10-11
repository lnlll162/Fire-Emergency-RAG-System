# Tests 目录说明

## 📁 目录结构

### 🧪 **测试文件**
- `test_ollama_model.py` - Ollama模型测试脚本
- `test_system_integration.py` - 系统集成测试
- `test_cache_service.py` - 缓存服务测试
- `test_knowledge_graph_service.py` - 知识图谱服务测试
- `test_ollama_service.py` - Ollama服务测试
- `test_rag_service.py` - RAG服务测试

## 🎯 **使用建议**

### 运行所有测试
```bash
# 使用pytest运行所有测试
pytest tests/

# 或者运行特定测试
python tests/test_ollama_model.py
python tests/test_system_integration.py
```

### 测试特定服务
```bash
# 测试Ollama模型
python tests/test_ollama_model.py

# 测试系统集成
python tests/test_system_integration.py

# 测试单个服务
python tests/test_cache_service.py
python tests/test_knowledge_graph_service.py
python tests/test_ollama_service.py
python tests/test_rag_service.py
```

## 📝 **注意事项**

1. **测试前准备**: 确保所有服务都已启动
2. **测试环境**: 建议在开发环境中运行测试
3. **测试数据**: 某些测试可能需要特定的测试数据
4. **依赖服务**: 集成测试需要所有相关服务都在运行
