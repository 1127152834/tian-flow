# Text2SQL Module Database Design

## 📋 Overview

This document outlines the database schema design for the Text2SQL module in deer-flow, migrated and adapted from ti-flow's architecture.

## 🗄️ Database Schema Structure

### Schema: `text2sql`

All Text2SQL related tables are organized under the `text2sql` schema for better organization and namespace isolation.

## 📊 Table Structures

### 1. `text2sql.query_history`

**Purpose**: Stores all SQL queries generated from natural language questions and their execution results.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | SERIAL | PRIMARY KEY | Unique query ID |
| `user_question` | TEXT | NOT NULL | Natural language question |
| `generated_sql` | TEXT | NOT NULL | Generated SQL query |
| `datasource_id` | INTEGER | NOT NULL, FK | Reference to database datasource |
| `status` | VARCHAR(50) | NOT NULL, CHECK | Query status (PENDING, SUCCESS, FAILED, TIMEOUT) |
| `execution_time_ms` | INTEGER | | Execution time in milliseconds |
| `result_rows` | INTEGER | | Number of result rows |
| `result_data` | JSONB | | Query results (limited for performance) |
| `error_message` | TEXT | | Error message if failed |
| `confidence_score` | FLOAT | CHECK (0-1) | AI confidence score |
| `model_used` | VARCHAR(100) | | AI model used for generation |
| `explanation` | TEXT | | SQL explanation |
| `similar_examples` | JSONB | | Similar training examples used |
| `user_rating` | INTEGER | CHECK (1-5) | User feedback rating |
| `user_feedback` | TEXT | | User feedback text |
| `created_at` | TIMESTAMP WITH TIME ZONE | NOT NULL, DEFAULT NOW() | Creation timestamp |

**Indexes**:
- `idx_query_history_datasource_id` on `datasource_id`
- `idx_query_history_created_at` on `created_at DESC`
- `idx_query_history_status` on `status`

### 2. `text2sql.training_data`

**Purpose**: Stores training examples for improving SQL generation accuracy.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | SERIAL | PRIMARY KEY | Unique training data ID |
| `datasource_id` | INTEGER | NOT NULL, FK | Reference to database datasource |
| `content_type` | VARCHAR(50) | NOT NULL, CHECK | Content type (DDL, DOCUMENTATION, SQL, SCHEMA) |
| `question` | TEXT | | Natural language question (for SQL type) |
| `sql_query` | TEXT | | Corresponding SQL query (for SQL type) |
| `content` | TEXT | NOT NULL | Raw content for embedding |
| `table_names` | TEXT[] | | Tables involved in this training data |
| `database_schema` | JSONB | | Relevant schema information |
| `embedding` | vector(1024) | | Vector embedding (1024 dimensions) |
| `embedding_model` | VARCHAR(100) | | Model used for embedding |
| `metadata` | JSONB | | Additional metadata |
| `content_hash` | VARCHAR(64) | NOT NULL | Hash for deduplication |
| `is_active` | BOOLEAN | NOT NULL, DEFAULT TRUE | Whether active |
| `is_validated` | BOOLEAN | NOT NULL, DEFAULT FALSE | Whether validated |
| `validation_score` | FLOAT | | Validation score |
| `created_at` | TIMESTAMP WITH TIME ZONE | NOT NULL, DEFAULT NOW() | Creation timestamp |
| `updated_at` | TIMESTAMP WITH TIME ZONE | NOT NULL, DEFAULT NOW() | Last update timestamp |

**Indexes**:
- `idx_training_data_datasource_id` on `datasource_id`
- `idx_training_data_content_type` on `content_type`
- `idx_training_data_is_active` on `is_active`
- `idx_training_data_content_hash` on `content_hash`
- `idx_training_data_embedding` (HNSW) on `embedding`

**Constraints**:
- `unique_training_content` UNIQUE on `(datasource_id, content_hash)`

### 3. `text2sql.sql_queries`

**Purpose**: Cache of frequently used queries with embeddings for fast similarity search.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | SERIAL | PRIMARY KEY | Unique cache ID |
| `query_text` | TEXT | NOT NULL | Natural language query |
| `sql_text` | TEXT | NOT NULL | Generated SQL |
| `datasource_id` | INTEGER | NOT NULL, FK | Reference to database datasource |
| `table_names` | TEXT[] | | Tables used in the query |
| `query_complexity` | VARCHAR(20) | DEFAULT 'SIMPLE', CHECK | Query complexity (SIMPLE, MEDIUM, COMPLEX) |
| `embedding` | vector(1024) | | Vector embedding |
| `embedding_model` | VARCHAR(100) | | Model used for embedding |
| `usage_count` | INTEGER | NOT NULL, DEFAULT 0 | Usage count |
| `last_used_at` | TIMESTAMP WITH TIME ZONE | | Last used timestamp |
| `average_execution_time_ms` | INTEGER | | Average execution time |
| `success_rate` | FLOAT | DEFAULT 1.0 | Success rate |
| `created_at` | TIMESTAMP WITH TIME ZONE | NOT NULL, DEFAULT NOW() | Creation timestamp |
| `updated_at` | TIMESTAMP WITH TIME ZONE | NOT NULL, DEFAULT NOW() | Last update timestamp |

**Indexes**:
- `idx_sql_queries_datasource_id` on `datasource_id`
- `idx_sql_queries_usage_count` on `usage_count DESC`
- `idx_sql_queries_last_used` on `last_used_at DESC`
- `idx_sql_queries_embedding` (HNSW) on `embedding`

### 4. `text2sql.training_sessions`

**Purpose**: Tracks model training sessions and their results.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | SERIAL | PRIMARY KEY | Unique session ID |
| `datasource_id` | INTEGER | NOT NULL, FK | Reference to database datasource |
| `session_name` | VARCHAR(255) | | Session name |
| `training_data_count` | INTEGER | NOT NULL, DEFAULT 0 | Training data count |
| `model_version` | VARCHAR(50) | | Model version |
| `training_parameters` | JSONB | | Training parameters |
| `status` | VARCHAR(50) | NOT NULL, DEFAULT 'PENDING', CHECK | Session status (PENDING, RUNNING, COMPLETED, FAILED) |
| `accuracy_score` | FLOAT | | Accuracy score |
| `validation_score` | FLOAT | | Validation score |
| `training_time_seconds` | INTEGER | | Training time in seconds |
| `notes` | TEXT | | Notes |
| `error_message` | TEXT | | Error message |
| `started_at` | TIMESTAMP WITH TIME ZONE | NOT NULL, DEFAULT NOW() | Start timestamp |
| `completed_at` | TIMESTAMP WITH TIME ZONE | | Completion timestamp |

**Indexes**:
- `idx_training_sessions_datasource_id` on `datasource_id`
- `idx_training_sessions_status` on `status`

## 🔗 Foreign Key Relationships

All tables reference `database_management.database_datasources(id)` with CASCADE delete to maintain referential integrity.

## 🚀 Vector Search Capabilities

### pgvector Integration

- **Extension**: Uses PostgreSQL's `pgvector` extension
- **Dimensions**: 1024-dimensional vectors (compatible with BGE-M3 model)
- **Index Type**: HNSW (Hierarchical Navigable Small World) for efficient similarity search
- **Distance Metric**: Cosine similarity (`vector_cosine_ops`)

### Vector Search Use Cases

1. **Training Data Similarity**: Find similar training examples for better SQL generation
2. **Query Caching**: Retrieve cached SQL for similar natural language queries
3. **Example Retrieval**: Get relevant examples during SQL generation process

## 🔧 Performance Optimizations

### Indexing Strategy

- **Primary Keys**: All tables use SERIAL primary keys
- **Foreign Keys**: Indexed for join performance
- **Temporal Data**: Indexed on timestamp columns for time-based queries
- **Status Fields**: Indexed for filtering by status
- **Vector Data**: HNSW indexes for fast similarity search

### Data Management

- **Content Deduplication**: Hash-based uniqueness constraints
- **Automatic Timestamps**: Triggers for `updated_at` columns
- **Cascading Deletes**: Maintain referential integrity
- **JSONB Storage**: Efficient storage and querying of metadata

## 📈 Scalability Considerations

### Horizontal Scaling

- **Partitioning**: Tables can be partitioned by `datasource_id` or time
- **Read Replicas**: Query history and training data are read-heavy
- **Caching**: Frequently accessed queries cached in `sql_queries` table

### Storage Optimization

- **Vector Compression**: pgvector supports various compression techniques
- **Result Data Limits**: Query results stored with size limits
- **Archive Strategy**: Old query history can be archived

## 🔒 Security & Privacy

### Data Protection

- **No Sensitive Data**: No user credentials stored in Text2SQL tables
- **Audit Trail**: Complete query history for compliance
- **Access Control**: Schema-level permissions

### Data Retention

- **Configurable Retention**: Query history retention policies
- **Training Data Lifecycle**: Active/inactive status for training data
- **User Feedback**: Optional user ratings and feedback

---

*This design provides a robust foundation for the Text2SQL module while maintaining compatibility with deer-flow's architecture and PostgreSQL best practices.*
