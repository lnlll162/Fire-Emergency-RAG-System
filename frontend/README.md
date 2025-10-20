# 消防应急RAG系统 - 前端

基于 Next.js 14 + TypeScript + Tailwind CSS 构建的现代化消防应急响应系统前端界面。

## 🚀 技术栈

- **框架**: Next.js 14 (App Router)
- **语言**: TypeScript 5.0+
- **样式**: Tailwind CSS 4.0
- **UI组件**: Headless UI + Radix UI
- **图标**: Heroicons
- **图表**: Recharts
- **HTTP客户端**: Axios

## 📁 项目结构

```
frontend/
├── src/
│   ├── app/                    # Next.js App Router 页面
│   │   ├── emergency/         # 应急查询页面
│   │   ├── knowledge/         # 知识图谱页面
│   │   ├── admin/             # 管理后台页面
│   │   ├── layout.tsx         # 根布局
│   │   └── page.tsx           # 首页
│   ├── components/            # 可复用组件
│   │   ├── ui/               # 基础UI组件
│   │   └── layout/           # 布局组件
│   └── lib/                  # 工具库
│       ├── api.ts            # API接口
│       └── utils.ts          # 工具函数
├── public/                   # 静态资源
└── package.json
```

## 🛠️ 开发指南

### 环境要求

- Node.js 18.0+
- npm 或 yarn

### 安装依赖

```bash
npm install
```

### 启动开发服务器

```bash
npm run dev
```

应用将在 http://localhost:3001 启动

### 构建生产版本

```bash
npm run build
npm start
```

## 🎨 功能特性

### 1. 首页 (/)
- 系统介绍和功能概览
- 快速导航到各个功能模块
- 系统统计数据展示

### 2. 应急查询 (/emergency)
- 智能问答界面
- 快速查询按钮
- 查询历史记录
- 置信度显示
- 参考来源展示

### 3. 知识图谱 (/knowledge)
- 知识实体可视化
- 关系网络展示
- 实体搜索功能
- 详细信息查看

### 4. 管理后台 (/admin)
- 系统状态监控
- 服务运行状态
- 数据库状态
- 系统操作面板

## 🔧 配置说明

### API配置

在 `src/lib/api.ts` 中配置后端API地址：

```typescript
const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000'
```

### 环境变量

创建 `.env.local` 文件：

```env
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
NEXT_PUBLIC_APP_NAME=消防应急RAG系统
NEXT_PUBLIC_APP_VERSION=1.0.0
```

## 🎯 核心组件

### UI组件库

- `Button` - 按钮组件
- `Card` - 卡片组件
- `Input` - 输入框组件
- `Textarea` - 文本域组件

### 布局组件

- `Header` - 顶部导航栏
- `Footer` - 底部页脚

### API集成

- `emergencyAPI` - 应急查询接口
- `knowledgeGraphAPI` - 知识图谱接口
- `systemAPI` - 系统状态接口
- `ragAPI` - RAG搜索接口

## 📱 响应式设计

- 移动端优先设计
- 支持平板和桌面端
- 自适应布局
- 触摸友好的交互

## 🚀 部署

### Vercel部署

1. 连接GitHub仓库
2. 配置环境变量
3. 自动部署

### Docker部署

```dockerfile
FROM node:18-alpine
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production
COPY . .
RUN npm run build
EXPOSE 3001
CMD ["npm", "start"]
```

## 🔍 开发注意事项

1. **TypeScript**: 严格类型检查，确保代码质量
2. **组件复用**: 优先使用已封装的UI组件
3. **API集成**: 统一使用 `src/lib/api.ts` 中的接口
4. **样式规范**: 使用Tailwind CSS类名，保持一致性
5. **性能优化**: 使用Next.js的优化特性

## 📞 技术支持

如有问题，请查看：
- [Next.js文档](https://nextjs.org/docs)
- [Tailwind CSS文档](https://tailwindcss.com/docs)
- [TypeScript文档](https://www.typescriptlang.org/docs)

---

© 2024 消防应急RAG系统. 保留所有权利.