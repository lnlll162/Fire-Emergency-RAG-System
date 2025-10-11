# Scripts 目录说明

## 📁 目录结构

### 🚀 **核心启动脚本**
- `start_all_services.py` - **主启动脚本** - 启动所有服务
- `start_emergency_service.py` - 应急服务启动脚本
- `start_knowledge_graph_service.py` - 知识图谱服务启动脚本
- `start_rag_service.py` - RAG服务启动脚本
- `start_ollama_service.py` - Ollama服务启动脚本
- `start_cache_service.py` - 缓存服务启动脚本
- `start_ollama_backend.py` - Ollama后端启动脚本

### 🧪 **验证脚本**
- `verify_system.py` - 系统验证脚本

### 🗄️ **数据库管理**
- `data_initialization/` - 数据库初始化脚本
  - `init_databases.py` - 初始化所有数据库
  - `README.md` - 数据库初始化说明
- `data_management/` - 数据管理脚本
  - `add_new_data.py` - 添加新数据
  - `quick_add.py` - 快速添加数据
  - `README.md` - 数据管理说明

### 🐳 **Docker相关**
- `docker_start_all.sh` - Docker启动脚本

### 🛠️ **开发工具**
- `start_dev.bat` - Windows开发环境启动
- `start_dev.sh` - Linux/Mac开发环境启动

## 🎯 **使用建议**

### 快速启动系统
```bash
python scripts/start_all_services.py
```

### 单独启动服务
```bash
python scripts/start_emergency_service.py
python scripts/start_rag_service.py
# ... 其他服务
```

### 测试系统
```bash
python tests/test_ollama_model.py
python scripts/verify_system.py
```

### 数据库初始化
```bash
python scripts/data_initialization/init_databases.py
```

## 📝 **注意事项**

1. **启动顺序**: 建议先启动数据库服务，再启动应用服务
2. **端口冲突**: 确保没有其他程序占用服务端口
3. **环境变量**: 确保正确设置了所有必要的环境变量
4. **依赖服务**: 某些服务依赖其他服务，请按正确顺序启动
5. **测试文件**: 所有测试文件已移动到 `tests/` 目录
