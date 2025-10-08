# 数据库初始化指南

## 概述
本目录包含用于初始化火灾应急救援RAG系统数据库的脚本和配置文件。

## 文件说明

### 数据文件
- `../data/knowledge_base/neo4j_sample_data.cypher` - Neo4j知识图谱示例数据
- `../data/knowledge_base/rag_documents.json` - ChromaDB向量数据库文档数据
- `../data/samples/user_input_samples.json` - 用户输入示例数据

### 脚本文件
- `init_databases.py` - 数据库初始化主脚本
- `requirements.txt` - Python依赖包列表

## 使用方法

### 1. 安装依赖
```bash
cd scripts/data_initialization
pip install -r requirements.txt
```

### 2. 配置环境变量
创建 `.env` 文件：
```bash
# Neo4j配置
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=password

# ChromaDB配置
CHROMA_HOST=localhost
CHROMA_PORT=8007
```

### 3. 启动数据库服务
```bash
# 启动Neo4j
docker run -d --name neo4j \
  -p 7474:7474 -p 7687:7687 \
  -e NEO4J_AUTH=neo4j/password \
  neo4j:5.15

# 启动ChromaDB
docker run -d --name chromadb \
  -p 8007:8000 \
  chromadb/chroma:latest
```

### 4. 运行初始化脚本
```bash
python init_databases.py
```

## 生成的数据内容

### Neo4j知识图谱
- **物品节点**: 8个常见物品（椅子、桌子、冰箱等）
- **材质节点**: 5种材质（木质、金属、布料、塑料、泡沫）
- **环境节点**: 5种环境（室内住宅、高层住宅、商业建筑等）
- **救援方案节点**: 5个救援方案
- **关系数据**: 物品-材质、材质-救援方案、环境-救援方案等关系

### ChromaDB向量数据库
- **救援程序文档**: 5个救援程序指南
- **案例研究文档**: 1个真实案例
- **设备指南文档**: 2个设备使用指南
- **安全指南文档**: 3个安全指南

### 示例数据
- **用户输入样本**: 8个不同场景的测试用例
- **物品信息**: 包含材质、数量、位置、易燃性等属性
- **环境信息**: 包含类型、区域、通风、人员数量等属性

## 数据特点

### 1. 真实性
- 基于真实消防知识和标准
- 符合实际救援场景
- 包含真实的救援程序

### 2. 完整性
- 覆盖多种火灾类型
- 包含不同材质和环境
- 提供完整的救援流程

### 3. 可扩展性
- 易于添加新的物品和材质
- 支持新的救援方案
- 可以持续更新文档

## 验证数据

初始化完成后，可以通过以下方式验证数据：

### Neo4j验证
```cypher
// 查看所有节点数量
MATCH (n) RETURN labels(n) as label, count(n) as count

// 查看物品关系
MATCH (item:Item)-[r]->(material:Material) 
RETURN item.name, r, material.name
```

### ChromaDB验证
```python
import chromadb
client = chromadb.HttpClient(host="localhost", port=8007)
collection = client.get_collection("fire_rescue_knowledge")
print(f"文档数量: {collection.count()}")
```

## 注意事项

1. **数据库版本**: 确保使用兼容的数据库版本
2. **内存要求**: 初始化过程需要足够的内存
3. **网络连接**: 确保数据库服务正常运行
4. **权限设置**: 确保有足够的数据库操作权限

## 故障排除

### 常见问题
1. **连接失败**: 检查数据库服务是否启动
2. **权限错误**: 检查用户名和密码
3. **内存不足**: 增加系统内存或减少批量大小
4. **端口冲突**: 检查端口是否被占用

### 日志查看
```bash
# 查看初始化日志
tail -f logs/init_databases.log
```
