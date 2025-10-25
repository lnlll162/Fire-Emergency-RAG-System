# Neo4j管理工具说明

## 📁 工具清单

本目录包含4个Neo4j管理工具，用于确保Neo4j容器稳定运行。

### 1. fix_neo4j_permanent.bat ⭐ 推荐
**用途：** 永久修复Neo4j问题，彻底解决"already running"错误

**适用场景：**
- Neo4j启动失败
- 容器状态异常
- 健康检查不通过
- 出现任何错误

**功能：**
- 安全停止并移除旧容器
- 可选清理损坏的数据卷
- 使用优化配置重建容器
- 自动验证修复结果

**使用方法：**
```bash
cd "D:\Fire Emergency RAG System"
.\scripts\fix_neo4j_permanent.bat
```

**执行时间：** 约1-2分钟

---

### 2. start_neo4j_safe.bat
**用途：** 安全启动Neo4j，带预检查和自动清理

**适用场景：**
- 日常启动Neo4j
- 系统重启后启动
- 容器异常后重启

**功能：**
- Docker状态检查
- 端口占用检查
- 智能PID清理
- 渐进式健康验证
- 详细状态报告

**使用方法：**
```bash
cd "D:\Fire Emergency RAG System"
.\scripts\start_neo4j_safe.bat
```

**执行时间：** 约30-60秒

---

### 3. check_neo4j_status.bat
**用途：** 一键检查Neo4j所有关键指标

**适用场景：**
- 每日使用前检查
- 快速诊断问题
- 验证修复结果
- 定期健康检查

**功能：**
- Docker服务状态
- 容器存在性和运行状态
- 健康检查状态
- HTTP/Bolt接口连通性
- CPU和内存使用情况
- 错误日志扫描

**使用方法：**
```bash
cd "D:\Fire Emergency RAG System"
.\scripts\check_neo4j_status.bat
```

**执行时间：** 约5-10秒

**输出示例：**
```
========================================
Neo4j容器状态检查
========================================

[1/6] 检查Docker服务...
[V] Docker正常运行

[2/6] 检查容器存在性...
[V] 容器存在

[3/6] 检查容器运行状态...
[V] 容器正在运行

[4/6] 检查健康状态...
[V] 容器健康

[5/6] 测试HTTP接口 (7474)...
[V] HTTP接口正常

[6/6] 测试Bolt接口 (7687)...
[V] Bolt端口正常

========================================
状态: 一切正常！
========================================
```

---

### 4. monitor_neo4j.bat
**用途：** 持续监控Neo4j状态（每5分钟）

**适用场景：**
- 长期运行监控
- 开发环境后台监控
- 问题预警

**功能：**
- 定时自动检查（5分钟间隔）
- 实时错误检测
- 资源使用监控
- 异常自动告警

**使用方法：**
```bash
cd "D:\Fire Emergency RAG System"
.\scripts\monitor_neo4j.bat
```

**停止监控：** 按 Ctrl+C

**执行时间：** 持续运行直到手动停止

**输出示例：**
```
========================================
Neo4j容器健康监控
========================================

[2025-10-25 14:30] 检查中...
[正常] Neo4j容器运行正常且健康
[正常] HTTP接口可访问
[资源] CPU: 0.47% | MEM: 929MiB / 7.621GiB

下次检查: 5分钟后...
----------------------------------------
```

---

## 🎯 使用指南

### 推荐使用流程

#### 场景1：日常启动
```bash
# 1. 使用安全启动脚本
.\scripts\start_neo4j_safe.bat

# 2. 检查状态确认
.\scripts\check_neo4j_status.bat
```

#### 场景2：遇到问题
```bash
# 1. 运行永久修复（推荐）
.\scripts\fix_neo4j_permanent.bat

# 2. 验证修复结果
.\scripts\check_neo4j_status.bat
```

#### 场景3：长期监控
```bash
# 启动监控（保持窗口打开）
.\scripts\monitor_neo4j.bat
```

---

## 🔍 常见问题

### Q1: 应该使用哪个脚本？

**日常使用：**
- 启动：`start_neo4j_safe.bat`
- 检查：`check_neo4j_status.bat`

**遇到问题：**
- 首选：`fix_neo4j_permanent.bat`
- 备选：`start_neo4j_safe.bat`

**监控需求：**
- 使用：`monitor_neo4j.bat`

### Q2: fix_neo4j_permanent.bat会丢失数据吗？

**默认不会丢失数据。** 脚本会询问是否清理数据卷。

- 选择 `n`（默认）：保留所有数据
- 选择 `y`：清理数据（用于测试环境重置）

### Q3: 脚本执行失败怎么办？

**检查步骤：**
1. 确保Docker Desktop运行
2. 以管理员身份运行CMD/PowerShell
3. 检查网络连接
4. 查看详细日志：`docker logs fire_emergency_neo4j`

### Q4: 如何验证Neo4j完全正常？

```bash
# 运行状态检查工具
.\scripts\check_neo4j_status.bat

# 应该看到所有检查项都是 [V]
# 最后显示"状态: 一切正常！"
```

### Q5: 多久应该检查一次Neo4j状态？

**建议：**
- 每天使用前：运行 `check_neo4j_status.bat`
- 开发期间：可选运行 `monitor_neo4j.bat`
- 遇到问题时：先运行 `check_neo4j_status.bat` 诊断

---

## 📚 相关文档

### 详细文档
- **完整故障排除指南：** `docs/neo4j_troubleshooting.md`
- **解决方案总结：** `docs/neo4j_solution_summary.md`
- **系统启动指南：** `docs/startup_guide.md`

### 配置文件
- **Docker Compose配置：** `infrastructure/docker/docker-compose.yml`
- **环境变量：** `infrastructure/docker/.env`

### Neo4j访问
- **浏览器界面：** http://localhost:7474
- **用户名：** neo4j
- **密码：** password

---

## 🆘 获取帮助

如果遇到工具无法解决的问题：

1. **收集诊断信息：**
```bash
# 导出完整日志
docker logs fire_emergency_neo4j > neo4j_full_log.txt

# 导出诊断信息
.\scripts\check_neo4j_status.bat > diagnosis.txt
docker ps -a >> diagnosis.txt
docker volume ls >> diagnosis.txt
```

2. **查阅文档：**
- 阅读 `docs/neo4j_troubleshooting.md`
- 查看 `docs/neo4j_solution_summary.md`

3. **参考官方文档：**
- Neo4j文档：https://neo4j.com/docs/
- Docker文档：https://docs.docker.com/

---

## 🔄 更新历史

### v1.0 (2025-10-25)
- ✅ 创建4个Neo4j管理工具
- ✅ 彻底解决"already running"问题
- ✅ 完善文档和使用指南

---

**最后更新：** 2025-10-25  
**维护状态：** 积极维护 ✅

