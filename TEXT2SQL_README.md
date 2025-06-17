# 🦌 DeerFlow Text2SQL System

## 🎉 完整功能实现

我们成功将 ti-flow 的 Text2SQL 功能完整移植到 deer-flow，包括所有核心功能、实时监控和用户界面。

## 🏗️ 系统架构

### 后端架构
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   API Routes    │    │   Services      │    │  Repositories   │
│                 │    │                 │    │                 │
│ • SQL生成       │───▶│ • Text2SQL      │───▶│ • Text2SQL      │
│ • 查询执行      │    │ • 向量存储      │    │ • 数据库连接    │
│ • 训练管理      │    │ • 数据源管理    │    │ • 缓存管理      │
│ • WebSocket     │    │                 │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Celery Tasks  │    │   WebSocket     │    │   PostgreSQL    │
│                 │    │   Manager       │    │   + pgvector    │
│ • 模型训练      │    │                 │    │                 │
│ • 向量生成      │    │ • 实时进度      │    │ • 查询历史      │
│ • 数据清理      │    │ • 状态推送      │    │ • 训练数据      │
│                 │    │ • 连接管理      │    │ • 向量索引      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### 前端架构
```
┌─────────────────────────────────────────────────────────────┐
│                    Settings Page                            │
│  ┌─────────────────┐  ┌─────────────────┐  ┌──────────────┐ │
│  │   Overview      │  │   Query         │  │   Training   │ │
│  │                 │  │                 │  │              │ │
│  │ • 统计信息      │  │ • SQL生成界面   │  │ • 训练数据   │ │
│  │ • 成功率        │  │ • 查询执行      │  │ • 数据管理   │ │
│  │ • 训练数据分布  │  │ • 结果展示      │  │ • 批量操作   │ │
│  └─────────────────┘  └─────────────────┘  └──────────────┘ │
│  ┌─────────────────┐  ┌─────────────────┐                   │
│  │   Monitoring    │  │   Settings      │                   │
│  │                 │  │                 │                   │
│  │ • 实时活动      │  │ • 模型配置      │                   │
│  │ • 训练进度      │  │ • 参数调整      │                   │
│  │ • WebSocket     │  │ • 系统设置      │                   │
│  └─────────────────┘  └─────────────────┘                   │
└─────────────────────────────────────────────────────────────┘
```

## 📊 核心功能

### ✅ 已实现功能

#### 🗄️ 数据管理
- **查询历史** - 完整的 SQL 生成和执行记录
- **训练数据** - 支持 SQL、Schema、文档等多种类型
- **SQL 缓存** - 智能查询缓存和相似度搜索
- **训练会话** - 模型训练会话管理和监控

#### 🧠 AI 功能
- **SQL 生成** - 自然语言转 SQL
- **置信度评分** - AI 模型置信度评估
- **相似查询** - 基于向量的相似查询推荐
- **解释生成** - SQL 查询解释和说明

#### ⚡ 后台任务
- **模型训练** - Celery 异步训练任务
- **向量生成** - 训练数据向量化处理
- **数据清理** - 定期清理旧数据
- **进度监控** - 实时任务进度跟踪

#### 🌐 实时通信
- **WebSocket 管理** - 实时状态推送
- **训练进度** - 实时训练进度监控
- **查询状态** - 实时查询执行状态
- **系统通知** - 系统状态和错误通知

#### 🎨 用户界面
- **SQL 查询界面** - 自然语言输入和 SQL 生成
- **训练数据管理** - 可视化训练数据管理
- **统计仪表板** - 系统使用统计和分析
- **实时监控** - 实时活动和任务监控

## 🚀 快速开始

### 1. 安装依赖
```bash
cd deer-flow
pip install -e .
```

### 2. 数据库迁移
```bash
make migrate
```

### 3. 启动服务
```bash
# 启动 Redis (后台任务队列)
redis-server --port 6380 &

# 启动 Celery Worker (后台任务处理)
celery -A src.tasks.text2sql_tasks worker --loglevel=info --concurrency=2 &

# 启动 FastAPI 服务器
python -m uvicorn src.server.app:app --host 0.0.0.0 --port 8000 --reload
```

### 4. 访问界面
- **API 文档**: http://localhost:8000/docs
- **Text2SQL API**: http://localhost:8000/api/text2sql
- **前端测试**: http://localhost:8000/test_frontend.html
- **设置页面**: http://localhost:3000/settings (需要启动前端)

## 🧪 测试

### 基础功能测试
```bash
make test-basic
```

### 完整系统测试
```bash
make test-text2sql
```

### 服务状态检查
```bash
make status
```

## 📡 API 端点

### SQL 生成和执行
- `POST /api/text2sql/generate` - 生成 SQL
- `POST /api/text2sql/execute` - 执行 SQL
- `GET /api/text2sql/history` - 查询历史

### 训练数据管理
- `POST /api/text2sql/training` - 添加训练数据
- `GET /api/text2sql/training` - 获取训练数据
- `DELETE /api/text2sql/training/{id}` - 删除训练数据

### 模型训练
- `POST /api/text2sql/retrain/{datasource_id}` - 重新训练模型
- `POST /api/text2sql/training-session` - 开始训练会话
- `GET /api/text2sql/training-sessions` - 获取训练会话

### 统计和监控
- `GET /api/text2sql/statistics` - 获取统计信息
- `GET /api/text2sql/datasource/{id}/training-summary` - 训练摘要
- `WS /api/text2sql/ws/{datasource_id}` - WebSocket 连接

## 🔧 配置

### 环境变量
```bash
# 数据库配置
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=aolei_db
POSTGRES_USER=aolei
POSTGRES_PASSWORD=aolei123456

# Redis 配置
REDIS_URL=redis://localhost:6380/0

# AI 模型配置 (可选)
OPENAI_API_KEY=your_openai_key
ANTHROPIC_API_KEY=your_anthropic_key
```

### 数据库架构
- **text2sql.query_history** - 查询历史记录
- **text2sql.training_data** - 训练数据
- **text2sql.sql_queries** - SQL 查询缓存
- **text2sql.training_sessions** - 训练会话
- **text2sql.vanna_embeddings** - 向量嵌入

## 🎯 使用示例

### 1. 创建数据源
```python
from src.services.database_datasource import DatabaseDatasourceService

service = DatabaseDatasourceService()
datasource = await service.create_datasource({
    "name": "My Database",
    "database_type": "POSTGRESQL",
    "host": "localhost",
    "port": 5432,
    "database_name": "mydb",
    "username": "user",
    "password": "pass"
})
```

### 2. 生成 SQL
```python
from src.services.text2sql import Text2SQLService

service = Text2SQLService()
response = await service.generate_sql({
    "datasource_id": 1,
    "question": "Show me all active users",
    "include_explanation": True
})
print(response.generated_sql)
```

### 3. 添加训练数据
```python
await service.add_training_data({
    "datasource_id": 1,
    "content_type": "SQL",
    "content": "SELECT * FROM users WHERE active = true",
    "question": "Show me all active users",
    "sql_query": "SELECT * FROM users WHERE active = true"
})
```

## 🔄 开发工作流

1. **开发环境设置**
   ```bash
   make install-dev
   make migrate
   ```

2. **启动开发服务**
   ```bash
   make dev
   ```

3. **运行测试**
   ```bash
   make test-basic
   make test-text2sql
   ```

4. **停止服务**
   ```bash
   make stop
   ```

## 📈 性能特点

- **异步处理** - 所有 I/O 操作都是异步的
- **连接池** - 数据库连接池管理
- **缓存机制** - 智能查询缓存
- **向量搜索** - pgvector 高性能向量搜索
- **实时通信** - WebSocket 低延迟通信
- **后台任务** - Celery 分布式任务处理

## 🛡️ 安全特性

- **只读模式** - 数据源可配置为只读
- **SQL 验证** - 生成的 SQL 安全验证
- **权限控制** - 基于数据源的权限管理
- **错误处理** - 完善的错误处理和日志记录

## 🔮 未来扩展

- **更多 AI 模型** - 支持更多 AI 模型提供商
- **高级分析** - 查询性能分析和优化建议
- **批量操作** - 批量 SQL 生成和执行
- **数据可视化** - 查询结果可视化
- **API 限流** - API 调用频率限制
- **审计日志** - 完整的操作审计日志

## 📞 支持

如有问题或建议，请查看：
- API 文档: http://localhost:8000/docs
- 测试页面: http://localhost:8000/test_frontend.html
- 日志文件: 检查应用日志获取详细信息

---

🎉 **恭喜！Text2SQL 系统已完全集成到 DeerFlow 中！**
