# 系统验证指南

## 概述

本文档提供了完整的系统验证方案，确保火灾应急RAG系统能够正常运行。

## 🚀 快速验证

### 方法1: 一键启动脚本

```bash
# 使用Python脚本启动所有服务
python scripts/start_all_services.py

# 使用Docker Compose启动所有服务
bash scripts/docker_start_all.sh
```

### 方法2: 手动启动

```bash
# 1. 启动基础服务
docker-compose up -d redis postgres neo4j chromadb ollama

# 2. 启动应用服务
python scripts/start_cache_service.py &
python scripts/start_ollama_service.py &
python scripts/start_rag_service.py &
python scripts/start_knowledge_graph_service.py &
python scripts/start_emergency_service.py &
python scripts/start_user_service.py &
python scripts/start_admin_service.py &
```

## 🔍 健康检查

### 快速健康检查

```bash
python scripts/run_health_check.py
```

### 详细健康检查

```bash
python scripts/run_health_check.py --detailed
```

### 手动检查各服务

```bash
# 检查缓存服务
curl http://localhost:8004/health

# 检查Ollama服务
curl http://localhost:8003/health

# 检查RAG服务
curl http://localhost:8005/health

# 检查知识图谱服务
curl http://localhost:8006/health

# 检查应急服务
curl http://localhost:8000/health

# 检查用户服务
curl http://localhost:8001/health

# 检查管理服务
curl http://localhost:8002/health
```

## 🧪 功能测试

### 运行完整集成测试

```bash
python tests/test_system_integration.py
```

### 运行各服务单元测试

```bash
# 缓存服务测试
python -m pytest tests/test_cache_service.py -v

# Ollama服务测试
python -m pytest tests/test_ollama_service.py -v

# RAG服务测试
python -m pytest tests/test_rag_service.py -v

# 知识图谱服务测试
python -m pytest tests/test_knowledge_graph_service.py -v

# 应急服务测试
python -m pytest tests/test_emergency_service.py -v

# 用户服务测试
python -m pytest tests/test_user_service.py -v

# 管理服务测试
python -m pytest tests/test_admin_service.py -v
```

## 📊 验证标准

### 1. 服务健康检查标准

- ✅ 所有服务响应HTTP 200状态码
- ✅ 健康检查端点返回"healthy"状态
- ✅ 响应时间小于5秒
- ✅ 无连接错误或超时

### 2. 功能测试标准

- ✅ 缓存服务：CRUD操作、批量操作、统计功能
- ✅ Ollama服务：模型管理、文本生成、救援方案生成
- ✅ RAG服务：文档搜索、嵌入生成、上下文增强
- ✅ 知识图谱服务：材料查询、环境查询、程序查询
- ✅ 应急服务：救援方案生成、应急响应
- ✅ 用户服务：用户注册、登录、管理
- ✅ 管理服务：系统监控、服务管理

### 3. 端到端测试标准

- ✅ 用户登录流程
- ✅ 救援方案生成流程
- ✅ 缓存存储和检索
- ✅ 知识图谱查询
- ✅ 文档搜索功能
- ✅ 服务间通信正常

## 🔧 故障排除

### 常见问题及解决方案

#### 1. 服务启动失败

**问题**: 服务无法启动
**解决方案**:
```bash
# 检查端口占用
netstat -tulpn | grep :8000

# 检查Docker容器状态
docker ps -a

# 查看服务日志
docker-compose logs [service_name]
```

#### 2. 数据库连接失败

**问题**: 无法连接到Redis/PostgreSQL/Neo4j
**解决方案**:
```bash
# 检查数据库服务状态
docker ps | grep redis
docker ps | grep postgres
docker ps | grep neo4j

# 重启数据库服务
docker-compose restart redis postgres neo4j
```

#### 3. 服务间通信失败

**问题**: 服务间无法通信
**解决方案**:
```bash
# 检查网络连接
docker network ls
docker network inspect fire_emergency_network

# 检查服务发现
curl http://localhost:8000/services
```

#### 4. 内存不足

**问题**: 系统内存不足
**解决方案**:
```bash
# 检查内存使用
free -h
docker stats

# 清理Docker资源
docker system prune -a
```

## 📈 性能验证

### 1. 响应时间测试

```bash
# 测试各服务响应时间
for port in 8000 8001 8002 8003 8004 8005 8006; do
  echo "测试端口 $port:"
  time curl -s http://localhost:$port/health > /dev/null
done
```

### 2. 并发测试

```bash
# 使用Apache Bench进行并发测试
ab -n 100 -c 10 http://localhost:8004/health
ab -n 100 -c 10 http://localhost:8003/health
```

### 3. 内存使用监控

```bash
# 监控Docker容器内存使用
docker stats --no-stream

# 监控系统内存使用
htop
```

## 🎯 验收标准

### 必须满足的条件

1. **所有服务健康**: 7个服务全部返回健康状态
2. **功能完整**: 所有核心功能正常工作
3. **端到端流程**: 完整业务流程可以执行
4. **性能达标**: 响应时间小于5秒
5. **错误处理**: 异常情况能够正确处理

### 可选优化条件

1. **高可用性**: 服务支持故障恢复
2. **负载均衡**: 支持多实例部署
3. **监控告警**: 完整的监控和告警系统
4. **日志管理**: 结构化日志和日志聚合
5. **安全加固**: 认证授权和加密传输

## 📝 验证报告模板

### 系统验证报告

**验证时间**: [日期时间]
**验证人员**: [姓名]
**系统版本**: [版本号]

#### 服务健康状态
- [ ] 缓存服务 (8004): ✅/❌
- [ ] Ollama服务 (8003): ✅/❌
- [ ] RAG服务 (8005): ✅/❌
- [ ] 知识图谱服务 (8006): ✅/❌
- [ ] 应急服务 (8000): ✅/❌
- [ ] 用户服务 (8001): ✅/❌
- [ ] 管理服务 (8002): ✅/❌

#### 功能测试结果
- [ ] 缓存CRUD操作: ✅/❌
- [ ] 救援方案生成: ✅/❌
- [ ] 文档搜索: ✅/❌
- [ ] 知识图谱查询: ✅/❌
- [ ] 用户管理: ✅/❌
- [ ] 系统监控: ✅/❌

#### 端到端测试结果
- [ ] 用户登录流程: ✅/❌
- [ ] 救援方案生成流程: ✅/❌
- [ ] 服务间通信: ✅/❌

#### 性能测试结果
- [ ] 平均响应时间: [X]ms
- [ ] 并发处理能力: [X] req/s
- [ ] 内存使用率: [X]%

#### 总体评估
- [ ] 系统可用性: 通过/不通过
- [ ] 功能完整性: 通过/不通过
- [ ] 性能达标: 通过/不通过
- [ ] 建议: [具体建议]

## 🚀 部署验证

### 生产环境验证清单

1. **环境准备**
   - [ ] 服务器资源充足
   - [ ] 网络配置正确
   - [ ] 安全组规则配置
   - [ ] SSL证书配置

2. **服务部署**
   - [ ] 所有服务成功部署
   - [ ] 配置文件正确
   - [ ] 环境变量设置
   - [ ] 数据库初始化

3. **功能验证**
   - [ ] 所有API端点可访问
   - [ ] 核心业务流程正常
   - [ ] 数据持久化正常
   - [ ] 错误处理正常

4. **性能验证**
   - [ ] 响应时间满足要求
   - [ ] 并发处理能力达标
   - [ ] 资源使用率合理
   - [ ] 无内存泄漏

5. **安全验证**
   - [ ] 认证授权正常
   - [ ] 数据传输加密
   - [ ] 敏感信息保护
   - [ ] 访问控制有效

通过以上验证步骤，可以确保整个火灾应急RAG系统能够正常运行并满足生产环境的要求。
