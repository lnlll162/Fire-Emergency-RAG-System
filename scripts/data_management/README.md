# 数据扩展管理指南

## 概述
本目录提供多种方式来扩展火灾应急RAG系统的数据，从简单的手动编辑到自动化脚本。

## 扩展方法

### 🔥 **方法1: 直接编辑文件 (最简单)**

#### 1.1 扩展知识图谱数据
编辑 `../data/knowledge_base/neo4j_sample_data.cypher` 文件：

```cypher
// 在文件末尾添加新物品
CREATE (item9:Item {
    id: 'item_009',
    name: '洗衣机',
    material: '金属',
    flammability: '不燃',
    toxicity: '低',
    category: '电器'
})

// 添加关系
MATCH (item9:Item {id: 'item_009'}), (material2:Material {id: 'material_002'})
CREATE (item9)-[:HAS_MATERIAL]->(material2)
```

#### 1.2 扩展RAG文档
编辑 `../data/knowledge_base/rag_documents.json` 文件：

```json
{
  "id": "doc_011",
  "title": "洗衣机火灾救援指南",
  "content": "洗衣机火灾救援要点...",
  "metadata": {
    "document_type": "rescue_procedure",
    "category": "电器火灾",
    "priority": "高"
  }
}
```

#### 1.3 扩展测试场景
编辑 `../data/samples/user_input_samples.json` 文件：

```json
{
  "id": "sample_009",
  "name": "洗衣机火灾场景",
  "items": [...],
  "environment": {...}
}
```

### 🚀 **方法2: 使用快速添加工具**

运行交互式脚本：
```bash
cd scripts/data_management
python quick_add.py
```

选择要添加的数据类型：
- 1. 添加新物品到知识图谱
- 2. 添加新文档到知识库  
- 3. 添加新测试场景

### 🔧 **方法3: 使用编程接口**

```python
from add_new_data import DataAdder

adder = DataAdder()

# 添加新物品
adder.add_new_item(
    name="空调",
    material="金属", 
    category="电器",
    flammability="不燃",
    toxicity="低"
)

# 添加新文档
adder.add_new_document(
    title="空调火灾救援指南",
    content="空调火灾救援要点...",
    document_type="rescue_procedure",
    category="电器火灾",
    priority="高"
)
```

## 数据更新流程

### 1. 添加数据
使用上述任一方法添加新数据

### 2. 重新初始化数据库
```bash
cd scripts/data_initialization
python init_databases.py
```

### 3. 验证数据
```bash
# 检查Neo4j
python -c "
from neo4j import GraphDatabase
driver = GraphDatabase.driver('bolt://localhost:7687', auth=('neo4j', 'password'))
with driver.session() as session:
    result = session.run('MATCH (n:Item) RETURN count(n) as count')
    print(f'物品数量: {result.single()[\"count\"]}')
driver.close()
"

# 检查ChromaDB
python -c "
import chromadb
client = chromadb.HttpClient(host='localhost', port=8007)
collection = client.get_collection('fire_rescue_knowledge')
print(f'文档数量: {collection.count()}')
"
```

## 数据扩展建议

### 📈 **按优先级扩展**

#### 高优先级
1. **常见物品**: 床、衣柜、书桌、电脑等
2. **常见材质**: 玻璃、陶瓷、复合材料等
3. **常见环境**: 学校、医院、商场等

#### 中优先级
1. **特殊物品**: 化学品、易燃液体等
2. **特殊环境**: 地下室、阁楼、车库等
3. **特殊场景**: 夜间火灾、恶劣天气等

#### 低优先级
1. **罕见物品**: 古董、艺术品等
2. **极端环境**: 极地、沙漠等
3. **特殊案例**: 历史案例、国际案例等

### 🎯 **按类型扩展**

#### 物品类型
- **家具类**: 床、沙发、衣柜、书桌
- **电器类**: 电视、冰箱、洗衣机、空调
- **装饰类**: 窗帘、地毯、画作、植物
- **工具类**: 工具箱、清洁用品、维修设备

#### 材质类型
- **天然材料**: 木材、石材、皮革
- **金属材料**: 钢铁、铝材、铜材
- **合成材料**: 塑料、橡胶、复合材料
- **特殊材料**: 玻璃、陶瓷、纤维

#### 环境类型
- **居住环境**: 住宅、公寓、别墅
- **工作环境**: 办公室、工厂、仓库
- **公共环境**: 商场、学校、医院
- **特殊环境**: 车辆、船舶、飞机

## 数据质量保证

### ✅ **检查清单**

#### 物品数据
- [ ] 名称准确且唯一
- [ ] 材质信息正确
- [ ] 易燃性和毒性等级合理
- [ ] 尺寸和重量信息完整

#### 文档数据
- [ ] 标题简洁明了
- [ ] 内容专业准确
- [ ] 元数据完整
- [ ] 标签分类正确

#### 测试场景
- [ ] 场景描述清晰
- [ ] 物品信息完整
- [ ] 环境信息合理
- [ ] 预期结果明确

### 🔍 **验证方法**

1. **语法检查**: 确保JSON和Cypher语法正确
2. **数据一致性**: 检查ID唯一性和关系正确性
3. **内容质量**: 确保信息准确和专业
4. **系统测试**: 运行完整系统测试验证

## 常见问题

### Q: 添加数据后系统没有更新？
A: 需要重新运行初始化脚本：`python init_databases.py`

### Q: 如何批量添加数据？
A: 可以编写脚本批量处理，或使用 `add_new_data.py` 的编程接口

### Q: 数据格式错误怎么办？
A: 检查JSON语法和Cypher语法，使用在线验证工具

### Q: 如何备份现有数据？
A: 复制数据文件到备份目录，或导出数据库

## 最佳实践

1. **定期备份**: 在修改前备份原始数据
2. **小批量更新**: 避免一次性添加大量数据
3. **测试验证**: 每次更新后都要测试系统功能
4. **文档记录**: 记录每次数据更新的内容和原因
5. **版本控制**: 使用Git管理数据文件版本
