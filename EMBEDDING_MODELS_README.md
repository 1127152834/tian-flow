# DeerFlow 向量模型集成指南

本文档介绍如何在 DeerFlow 中配置和使用向量模型（Embedding Models）和重排序模型（Rerank Models）来增强 Text2SQL 功能。

## 🎯 功能概述

DeerFlow 现在支持：
- **向量模型（Embedding Models）**: 将文本转换为向量表示，用于语义相似度搜索
- **重排序模型（Rerank Models）**: 对搜索结果进行重新排序，提高相关性
- **多种提供商**: 支持 OpenAI、SiliconFlow、本地模型等
- **智能回退**: 当 API 模型不可用时自动回退到本地模型

## 📋 配置说明

### 1. 配置文件设置

在 `conf.yaml` 中添加向量模型配置：

```yaml
# 向量模型配置（必需）
BASE_EMBEDDING_MODEL:
  api_key: sk-your-api-key-here
  base_url: https://api.siliconflow.cn/v1
  model: BAAI/bge-m3
  vector_dimension: 1024

# 重排序模型配置（可选）
BASE_RERANK_MODEL:
  api_key: sk-your-api-key-here
  base_url: https://api.siliconflow.cn/v1
  model: BAAI/bge-reranker-v2-m3
```

### 2. 环境变量配置

也可以通过环境变量配置（优先级更高）：

```bash
# 向量模型
export BASE_EMBEDDING_MODEL__api_key="sk-your-api-key-here"
export BASE_EMBEDDING_MODEL__base_url="https://api.siliconflow.cn/v1"
export BASE_EMBEDDING_MODEL__model="BAAI/bge-m3"
export BASE_EMBEDDING_MODEL__vector_dimension="1024"

# 重排序模型
export BASE_RERANK_MODEL__api_key="sk-your-api-key-here"
export BASE_RERANK_MODEL__base_url="https://api.siliconflow.cn/v1"
export BASE_RERANK_MODEL__model="BAAI/bge-reranker-v2-m3"
```

## 🔧 支持的模型提供商

### 1. SiliconFlow（推荐）
```yaml
BASE_EMBEDDING_MODEL:
  api_key: sk-your-siliconflow-key
  base_url: https://api.siliconflow.cn/v1
  model: BAAI/bge-m3
  vector_dimension: 1024
```

### 2. OpenAI
```yaml
BASE_EMBEDDING_MODEL:
  api_key: sk-your-openai-key
  base_url: https://api.openai.com/v1
  model: text-embedding-3-small
  vector_dimension: 1536
```

### 3. 本地模型
```yaml
BASE_EMBEDDING_MODEL:
  model: sentence-transformers/all-MiniLM-L6-v2
  vector_dimension: 384
  # 不需要 api_key 和 base_url
```

## 🚀 使用方法

### 1. 在代码中使用

```python
from src.llms.embedding import embed_query, embed_texts
from src.llms.reranker import rerank_documents

# 生成单个文本的向量
embedding = embed_query("Show me all active users", "BASE_EMBEDDING")

# 批量生成向量
texts = ["Query 1", "Query 2", "Query 3"]
embeddings = embed_texts(texts, "BASE_EMBEDDING")

# 重排序文档
query = "user information"
documents = ["SELECT * FROM users", "SELECT * FROM products"]
reranked = rerank_documents(query, documents, "BASE_RERANK", top_k=5)
```

### 2. Text2SQL 中的自动使用

向量模型会自动在以下场景中使用：

- **训练数据存储**: 自动为训练数据生成向量
- **相似查询搜索**: 基于语义相似度查找相关的 SQL 示例
- **结果重排序**: 使用重排序模型提高搜索结果的相关性

## 🧪 测试和验证

### 1. 运行测试脚本

```bash
python test_embedding_models.py
```

这个脚本会测试：
- 配置加载
- 向量生成
- 重排序功能
- 集成工作流

### 2. 预期输出

```
🚀 DeerFlow Embedding & Rerank Models Test
============================================================

🧪 Testing Embedding Models
==================================================
✅ Settings loaded successfully
   Embedding model: BAAI/bge-m3
   Vector dimension: 1024
   Rerank model: BAAI/bge-reranker-v2-m3

📝 Testing single text embedding...
✅ Generated embedding with dimension: 1024

📝 Testing batch text embedding...
✅ Generated 4 embeddings

🔄 Testing Rerank Models
==================================================
📝 Testing document reranking...
✅ Reranked to top 3 documents

🎉 All tests passed! The embedding and rerank models are working correctly.
```

## 🔍 故障排除

### 1. 常见问题

**问题**: `ImportError: No module named 'sentence_transformers'`
**解决**: 安装依赖 `pip install sentence-transformers`

**问题**: API 调用失败
**解决**: 检查 API 密钥和网络连接

**问题**: 向量维度不匹配
**解决**: 确保配置中的 `vector_dimension` 与模型实际输出维度一致

### 2. 日志调试

启用详细日志：

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### 3. 回退机制

系统具有多层回退机制：
1. API 模型失败 → 本地模型
2. 本地模型失败 → 简单哈希向量
3. 重排序失败 → 保持原始顺序

## 📈 性能优化

### 1. 模型缓存

模型会自动缓存，避免重复加载：

```python
from src.llms.embedding import clear_embedding_cache
from src.config.settings import clear_settings_cache

# 清除缓存（如果需要重新加载配置）
clear_embedding_cache()
clear_settings_cache()
```

### 2. 批量处理

对于大量文本，使用批量处理：

```python
# 推荐：批量处理
embeddings = embed_texts(large_text_list, "BASE_EMBEDDING")

# 避免：逐个处理
# embeddings = [embed_query(text, "BASE_EMBEDDING") for text in large_text_list]
```

### 3. 向量维度选择

- **小模型** (384维): 速度快，适合简单场景
- **中等模型** (768维): 平衡性能和质量
- **大模型** (1024+维): 最佳质量，适合复杂场景

## 🔗 相关文件

- `src/llms/embedding.py` - 向量模型管理
- `src/llms/reranker.py` - 重排序模型管理
- `src/config/settings.py` - 配置管理
- `src/services/vector_store.py` - 向量存储服务
- `conf.yaml.example` - 配置示例

## 📚 更多资源

- [SiliconFlow API 文档](https://docs.siliconflow.cn/)
- [Sentence Transformers 文档](https://www.sbert.net/)
- [BGE 模型介绍](https://huggingface.co/BAAI/bge-m3)
