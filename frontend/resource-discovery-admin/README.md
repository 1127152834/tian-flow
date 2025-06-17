# DeerFlow 资源发现管理界面

基于 Next.js 和 React 构建的现代化资源发现管理界面，参考 Ti-Flow 的设计模式。

## 功能特性

### 🎯 核心功能
- **系统概览** - 实时监控系统状态和性能指标
- **资源管理** - 查看、搜索、过滤和管理所有发现的资源
- **发现测试** - 交互式测试资源发现功能
- **系统设置** - 配置系统参数和行为

### 📊 可视化组件
- **实时图表** - 使用 Recharts 展示资源分布和性能数据
- **响应式设计** - 适配桌面和移动设备
- **暗色主题** - 支持明暗主题切换
- **交互式界面** - 现代化的用户交互体验

### 🔧 技术栈
- **Next.js 14** - React 全栈框架
- **TypeScript** - 类型安全的开发体验
- **Tailwind CSS** - 实用优先的CSS框架
- **Radix UI** - 无障碍的UI组件库
- **Recharts** - 数据可视化图表库
- **Sonner** - 优雅的通知系统

## 快速开始

### 1. 安装依赖

```bash
cd frontend/resource-discovery-admin
npm install
```

### 2. 配置环境

创建 `.env.local` 文件：

```env
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
```

### 3. 启动开发服务器

```bash
npm run dev
```

访问 http://localhost:3000 查看管理界面。

### 4. 构建生产版本

```bash
npm run build
npm start
```

## 页面结构

### 系统概览 (Overview)
- **系统健康状态** - 实时监控各服务状态
- **性能指标** - 查询时间、成功率、缓存命中率等
- **资源分布图表** - 柱状图和饼图展示资源类型分布
- **快捷操作** - 一键同步、刷新等常用操作

### 资源管理 (Resources)
- **资源列表** - 表格形式展示所有资源
- **搜索过滤** - 按名称、类型、状态筛选资源
- **状态监控** - 实时显示资源状态和向量化进度
- **批量操作** - 支持批量管理资源

### 发现测试 (Testing)
- **交互式测试** - 输入查询测试资源发现功能
- **参数调节** - 调整最大结果数、置信度阈值等
- **结果分析** - 详细展示匹配结果和置信度评分
- **预设查询** - 快速选择常用测试查询

### 系统设置 (Settings)
- **同步设置** - 配置自动同步间隔和并发数
- **匹配参数** - 调整相似度阈值和查询限制
- **性能优化** - 配置缓存、监控等性能参数
- **系统状态** - 查看各服务运行状态

## API 集成

管理界面通过以下 API 端点与后端通信：

```typescript
// 获取系统统计
GET /api/admin/resource-discovery/statistics

// 资源发现测试
POST /api/admin/resource-discovery/discover

// 系统同步
POST /api/admin/resource-discovery/sync

// 获取资源列表
GET /api/admin/resource-discovery/resources

// 获取/更新系统配置
GET/PUT /api/admin/resource-discovery/config
```

## 组件架构

```
app/
├── page.tsx                 # 主页面组件
├── layout.tsx              # 布局组件
├── globals.css             # 全局样式
└── components/
    ├── system-overview.tsx     # 系统概览
    ├── resource-management.tsx # 资源管理
    ├── discovery-testing.tsx   # 发现测试
    └── system-settings.tsx     # 系统设置

components/ui/
├── card.tsx                # 卡片组件
├── button.tsx              # 按钮组件
└── index.tsx               # UI组件集合
```

## 自定义样式

项目使用 Tailwind CSS 和自定义 CSS 变量：

```css
/* 状态指示器 */
.status-active { @apply bg-green-100 text-green-800; }
.status-inactive { @apply bg-gray-100 text-gray-800; }
.status-error { @apply bg-red-100 text-red-800; }

/* 置信度标签 */
.confidence-high { @apply bg-green-100 text-green-800; }
.confidence-medium { @apply bg-yellow-100 text-yellow-800; }
.confidence-low { @apply bg-red-100 text-red-800; }
```

## 开发指南

### 添加新页面
1. 在 `app/components/` 下创建新组件
2. 在主页面 `page.tsx` 中添加新的 Tab
3. 更新导航和路由逻辑

### 添加新的 API 调用
1. 在组件中使用 `fetch` 调用 API
2. 处理加载状态和错误状态
3. 使用 `toast` 显示操作结果

### 样式定制
1. 修改 `tailwind.config.js` 配置主题
2. 在 `globals.css` 中添加自定义样式
3. 使用 CSS 变量支持主题切换

## 部署说明

### 开发环境
```bash
npm run dev
```

### 生产环境
```bash
npm run build
npm start
```

### Docker 部署
```dockerfile
FROM node:18-alpine
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production
COPY . .
RUN npm run build
EXPOSE 3000
CMD ["npm", "start"]
```

## 故障排除

### 常见问题

1. **API 连接失败**
   - 检查后端服务是否运行在 http://localhost:8000
   - 确认 CORS 配置正确

2. **样式不生效**
   - 确认 Tailwind CSS 配置正确
   - 检查 PostCSS 配置

3. **组件导入错误**
   - 检查相对路径是否正确
   - 确认组件导出语法

### 调试技巧
- 使用浏览器开发者工具查看网络请求
- 检查控制台错误信息
- 使用 React Developer Tools 调试组件状态

## 贡献指南

1. Fork 项目
2. 创建功能分支: `git checkout -b feature/new-feature`
3. 提交更改: `git commit -am 'Add new feature'`
4. 推送分支: `git push origin feature/new-feature`
5. 创建 Pull Request

## 许可证

MIT License - 详见 LICENSE 文件
