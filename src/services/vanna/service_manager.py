# Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
# SPDX-License-Identifier: MIT

"""
Vanna AI service manager for DeerFlow
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

from vanna.base import VannaBase

from .vector_store import PgVectorStore
from .database_adapter import DatabaseAdapter

logger = logging.getLogger(__name__)


class VannaServiceManager:
    """Vanna AI service manager for DeerFlow"""
    
    def __init__(self):
        self._vanna_instances: Dict[str, VannaBase] = {}
        self._vector_stores: Dict[str, PgVectorStore] = {}
        self._db_adapters: Dict[int, DatabaseAdapter] = {}
        
        # Services are initialized per-instance as needed
        
        logger.info("✅ VannaServiceManager initialized")
    
    def _get_vanna_instance(self, datasource_id: int, embedding_model_id: Optional[int] = None) -> VannaBase:
        """Get or create Vanna instance"""
        instance_key = f"{datasource_id}_{embedding_model_id or 'default'}"
        
        if instance_key not in self._vanna_instances:
            # Create vector store
            if instance_key not in self._vector_stores:
                vector_store = PgVectorStore(datasource_id, embedding_model_id)
                self._vector_stores[instance_key] = vector_store
            else:
                vector_store = self._vector_stores[instance_key]
            
            # Create database adapter
            if datasource_id not in self._db_adapters:
                db_adapter = DatabaseAdapter(datasource_id)
                self._db_adapters[datasource_id] = db_adapter
            else:
                db_adapter = self._db_adapters[datasource_id]
            
            # Create custom Vanna instance
            class DeerFlowVanna(VannaBase):
                def __init__(self, config=None):
                    VannaBase.__init__(self, config=config)
                    self.vector_store = vector_store
                    self.db_adapter = db_adapter

                # Required abstract methods from VannaBase
                def system_message(self, message: str) -> Any:
                    """System message for LLM"""
                    return {"role": "system", "content": message}

                def user_message(self, message: str) -> Any:
                    """User message for LLM"""
                    return {"role": "user", "content": message}

                def assistant_message(self, message: str) -> Any:
                    """Assistant message for LLM"""
                    return {"role": "assistant", "content": message}

                def generate_embedding(self, data: str, **kwargs) -> List[float]:
                    """Generate embedding for data"""
                    return self.vector_store._get_embedding(data)

                def submit_prompt(self, prompt, **kwargs) -> str:
                    """Submit prompt to LLM and get SQL response using Vanna AI approach"""
                    # Handle both string and list inputs
                    if isinstance(prompt, list):
                        # Extract the last user message from the conversation
                        user_messages = [msg for msg in prompt if isinstance(msg, dict) and msg.get('role') == 'user']
                        if user_messages:
                            question = user_messages[-1].get('content', '')
                        else:
                            question = str(prompt)
                    else:
                        question = str(prompt)

                    logger.info(f"🤖 Generating SQL using LLM for question: {question}")

                    try:
                        # Get relevant context from vector store
                        similar_sqls = self.vector_store.get_similar_question_sql(question, limit=3)
                        similar_ddls = self.vector_store.get_similar_ddl(question, limit=5)

                        logger.info(f"Found {len(similar_sqls)} similar SQL examples and {len(similar_ddls)} DDL statements")

                        # Build context for LLM
                        context_parts = []

                        # Add DDL context
                        if similar_ddls:
                            context_parts.append("Database Schema:")
                            for ddl in similar_ddls[:3]:  # Limit to top 3 DDL statements
                                context_parts.append(ddl)
                            context_parts.append("")

                        # Add SQL examples context
                        if similar_sqls:
                            context_parts.append("Example SQL queries:")
                            for i, example in enumerate(similar_sqls[:2]):  # Limit to top 2 examples
                                if isinstance(example, dict):
                                    example_q = example.get('question', '')
                                    example_sql = example.get('sql', '')
                                    if example_q and example_sql:
                                        context_parts.append(f"Q: {example_q}")
                                        context_parts.append(f"SQL: {example_sql}")
                                        context_parts.append("")

                        # Build the full prompt for LLM
                        context = "\n".join(context_parts)

                        full_prompt = f"""You are a SQL expert. Based on the provided database schema and examples, generate a SQL query for the following question.

{context}

Question: {question}

Generate only the SQL query, no explanations. The query should be syntactically correct and follow best practices."""

                        # Use the LLM to generate SQL
                        try:
                            from src.llms.llm import get_llm_by_type

                            # Get basic LLM for SQL generation
                            llm = get_llm_by_type("basic")

                            # Generate SQL using LLM
                            response = llm.invoke(full_prompt)

                            if response and hasattr(response, 'content') and response.content.strip():
                                # Clean up the response (remove markdown formatting if present)
                                sql = response.content.strip()

                                # Remove markdown code blocks
                                if '```sql' in sql:
                                    # Extract SQL from markdown code block
                                    import re
                                    match = re.search(r'```sql\s*(.*?)\s*```', sql, re.DOTALL)
                                    if match:
                                        sql = match.group(1).strip()
                                elif '```' in sql:
                                    # Remove generic code blocks
                                    sql = re.sub(r'```.*?\n', '', sql)
                                    sql = re.sub(r'\n```.*?', '', sql)
                                    sql = sql.strip()

                                # Remove any leading text before SQL
                                lines = sql.split('\n')
                                sql_lines = []
                                found_sql = False
                                for line in lines:
                                    line = line.strip()
                                    if line.upper().startswith(('SELECT', 'INSERT', 'UPDATE', 'DELETE', 'WITH', 'CREATE', 'DROP', 'ALTER')):
                                        found_sql = True
                                    if found_sql:
                                        sql_lines.append(line)

                                if sql_lines:
                                    sql = '\n'.join(sql_lines).strip()

                                logger.info(f"✅ Generated SQL using LLM: {sql}")
                                return sql
                            else:
                                logger.warning("LLM returned empty response")

                        except Exception as llm_error:
                            logger.warning(f"LLM generation failed: {llm_error}")

                        # Fallback: Use enhanced pattern matching with context
                        return self._generate_fallback_sql(question, similar_sqls, similar_ddls)

                    except Exception as e:
                        logger.error(f"Failed to generate SQL: {e}")
                        return "SELECT 1 as result -- Error generating SQL"

                def _generate_fallback_sql(self, question: str, similar_sqls: List, similar_ddls: List) -> str:
                    """Generate SQL using fallback logic when LLM fails"""
                    question_lower = question.lower()

                    # First try to use similar SQL examples with better matching
                    if similar_sqls:
                        best_match = None
                        best_score = 0

                        for example in similar_sqls:
                            if isinstance(example, dict):
                                example_question = example.get("question", "").lower()
                                example_sql = example.get("sql", "")

                                # Calculate similarity score
                                question_words = set(question_lower.split())
                                example_words = set(example_question.split())
                                common_words = question_words & example_words
                                score = len(common_words)

                                if score > best_score:
                                    best_score = score
                                    best_match = example_sql

                        if best_match and best_score > 0:
                            logger.info(f"Using best matching SQL example (score: {best_score})")
                            return best_match

                    # Then try to generate from DDL context
                    if similar_ddls:
                        return self._generate_sql_from_ddl_context(question, similar_ddls)

                    # Final fallback
                    return "SELECT 1 as result -- Please add more training data for better SQL generation"

                def _generate_sql_from_ddl_context(self, question: str, ddl_list: List[str]) -> str:
                    """Generate SQL based on question and DDL context"""
                    question_lower = question.lower()

                    # Extract table information from DDL
                    tables_info = []
                    for ddl in ddl_list:
                        table_info = self._parse_ddl_info(ddl)
                        if table_info:
                            tables_info.append(table_info)

                    if not tables_info:
                        return "SELECT 1 as result -- No valid table information found"

                    # Use the first table as primary
                    primary_table = tables_info[0]
                    table_name = primary_table["name"]
                    columns = primary_table.get("columns", [])

                    # Generate SQL based on question patterns
                    if any(word in question_lower for word in ['count', 'how many', '多少', '数量']):
                        return f"SELECT COUNT(*) as count FROM {table_name}"
                    elif any(word in question_lower for word in ['all', 'list', 'show', '所有', '列出', '显示']):
                        return f"SELECT * FROM {table_name} LIMIT 10"
                    elif any(word in question_lower for word in ['latest', 'recent', '最新', '最近']):
                        # Try to find a date/time column
                        date_columns = [col for col in columns if any(date_word in col.lower() for date_word in ['date', 'time', 'created', 'updated'])]
                        if date_columns:
                            return f"SELECT * FROM {table_name} ORDER BY {date_columns[0]} DESC LIMIT 10"
                        else:
                            return f"SELECT * FROM {table_name} ORDER BY id DESC LIMIT 10"
                    else:
                        # Default query
                        return f"SELECT * FROM {table_name} LIMIT 10"

                def _parse_ddl_info(self, ddl: str) -> Optional[Dict[str, Any]]:
                    """Parse DDL to extract table name and columns"""
                    try:
                        ddl_upper = ddl.upper().strip()
                        if not ddl_upper.startswith('CREATE TABLE'):
                            return None

                        # Extract table name
                        import re
                        table_match = re.search(r'CREATE\s+TABLE\s+(?:IF\s+NOT\s+EXISTS\s+)?(?:`?(\w+)`?\.)?`?(\w+)`?', ddl_upper)
                        if not table_match:
                            return None

                        table_name = table_match.group(2).lower()

                        # Extract column names (simple parsing)
                        columns = []
                        lines = ddl.split('\n')
                        for line in lines:
                            line = line.strip()
                            if line and not line.upper().startswith(('CREATE', 'PRIMARY', 'FOREIGN', 'INDEX', 'CONSTRAINT', ')', '(')):
                                # Try to extract column name
                                parts = line.split()
                                if parts and not parts[0].upper() in ('PRIMARY', 'FOREIGN', 'INDEX', 'CONSTRAINT'):
                                    column_name = parts[0].strip('`"[]').lower()
                                    if column_name and column_name != ',':
                                        columns.append(column_name)

                        return {
                            "name": table_name,
                            "columns": columns
                        }

                    except Exception as e:
                        logger.warning(f"Failed to parse DDL: {e}")
                        return None

                def get_training_data(self, **kwargs) -> List[Dict[str, Any]]:
                    """Get training data"""
                    return []

                def get_related_ddl(self, question: str, **kwargs) -> List[str]:
                    """Get related DDL"""
                    return self.vector_store.get_similar_ddl(question, **kwargs)

                def get_related_documentation(self, question: str, **kwargs) -> List[str]:
                    """Get related documentation"""
                    return []

                # Vector Store methods
                def add_ddl(self, ddl: str, **kwargs) -> str:
                    return self.vector_store.add_ddl(ddl, **kwargs)

                def add_documentation(self, documentation: str, **kwargs) -> str:
                    return self.vector_store.add_documentation(documentation, **kwargs)

                def add_question_sql(self, question: str, sql: str, **kwargs) -> str:
                    return self.vector_store.add_question_sql(question, sql, **kwargs)

                def get_similar_ddl(self, question: str, **kwargs) -> List[str]:
                    return self.vector_store.get_similar_ddl(question, **kwargs)

                def get_similar_question_sql(self, question: str, **kwargs) -> List[str]:
                    return self.vector_store.get_similar_question_sql(question, **kwargs)

                def remove_training_data(self, id: str) -> bool:
                    return self.vector_store.remove_training_data(id)
                
                # Database methods
                def run_sql(self, sql: str, **kwargs) -> Any:
                    """Execute SQL and return results"""
                    limit = kwargs.get('limit', 1000)
                    return self.db_adapter.execute_sql_sync(sql, limit)
                
                def connect_to_db(self, **kwargs):
                    """Connect to database (no-op as we handle connections internally)"""
                    pass
                
                def get_schema(self, **kwargs) -> str:
                    """Get database schema as string"""
                    # Return mock schema for now
                    schema_str = """Table: users
  id (INTEGER)
  name (VARCHAR)
  email (VARCHAR)
  created_at (TIMESTAMP)

Table: orders
  id (INTEGER)
  user_id (INTEGER)
  amount (DECIMAL)
  created_at (TIMESTAMP)

"""
                    logger.info("Returning mock database schema")
                    return schema_str
            
            # Create configuration
            config = db_adapter.to_vanna_config()
            config['allow_llm_to_see_data'] = True
            
            # Instantiate Vanna
            vanna_instance = DeerFlowVanna(config=config)
            self._vanna_instances[instance_key] = vanna_instance
            
            logger.info(f"✅ Created Vanna instance for datasource {datasource_id}, embedding model: {embedding_model_id or 'default'}")
        
        return self._vanna_instances[instance_key]
    
    async def generate_sql(self, datasource_id: int, question: str, embedding_model_id: Optional[int] = None) -> Dict[str, Any]:
        """
        Generate SQL from natural language question using Vanna AI

        Args:
            datasource_id: Database datasource ID
            question: Natural language question
            embedding_model_id: Embedding model ID (optional)

        Returns:
            SQL generation result
        """
        try:
            start_time = datetime.utcnow()

            # Get Vanna instance
            vanna_instance = self._get_vanna_instance(datasource_id, embedding_model_id)

            # Use Vanna's ask method to generate SQL
            # This will automatically retrieve relevant DDL, SQL examples, and documentation
            try:
                sql = vanna_instance.generate_sql(question)

                if not sql or sql.strip() == "":
                    # Fallback: try to get related information manually
                    similar_sqls = vanna_instance.get_similar_question_sql(question, limit=3)
                    similar_ddls = vanna_instance.get_similar_ddl(question, limit=5)

                    if similar_sqls:
                        sql = similar_sqls[0]
                        logger.info(f"Using similar SQL as fallback: {sql}")
                    elif similar_ddls:
                        # Try to generate a simple query based on DDL
                        sql = self._generate_simple_sql_from_ddl(question, similar_ddls)
                        logger.info(f"Generated simple SQL from DDL: {sql}")
                    else:
                        return {
                            "success": False,
                            "error": "未找到相关的训练数据",
                            "message": "请先训练相关的DDL或SQL示例",
                            "question": question,
                            "generated_at": start_time.isoformat()
                        }

                # Get similar examples for context
                similar_sqls = vanna_instance.get_similar_question_sql(question, limit=3)

                # Calculate confidence based on similarity and training data availability
                confidence = self._calculate_confidence(question, sql, similar_sqls)

                # Calculate generation time
                generation_time = (datetime.utcnow() - start_time).total_seconds()

                return {
                    "success": True,
                    "sql": sql,
                    "question": question,
                    "similar_sqls": similar_sqls,
                    "confidence": confidence,
                    "generation_time": generation_time,
                    "generated_at": start_time.isoformat()
                }

            except Exception as vanna_error:
                logger.warning(f"Vanna generate_sql failed: {vanna_error}, trying fallback approach")

                # Fallback approach: manual retrieval and generation
                similar_sqls = vanna_instance.get_similar_question_sql(question, limit=3)
                similar_ddls = vanna_instance.get_similar_ddl(question, limit=5)

                if similar_sqls:
                    sql = similar_sqls[0]
                    confidence = 0.7  # Lower confidence for exact match
                elif similar_ddls:
                    sql = self._generate_simple_sql_from_ddl(question, similar_ddls)
                    confidence = 0.5  # Even lower confidence for generated SQL
                else:
                    return {
                        "success": False,
                        "error": "无法生成SQL查询",
                        "message": "请先训练相关的DDL或SQL示例",
                        "question": question,
                        "generated_at": start_time.isoformat()
                    }

                generation_time = (datetime.utcnow() - start_time).total_seconds()

                return {
                    "success": True,
                    "sql": sql,
                    "question": question,
                    "similar_sqls": similar_sqls,
                    "confidence": confidence,
                    "generation_time": generation_time,
                    "generated_at": start_time.isoformat()
                }

        except Exception as e:
            logger.error(f"Failed to generate SQL: {e}")
            return {
                "success": False,
                "error": str(e),
                "question": question,
                "generated_at": datetime.utcnow().isoformat()
            }
    
    async def execute_sql(self, datasource_id: int, sql: str) -> Dict[str, Any]:
        """
        Execute SQL query
        
        Args:
            datasource_id: Database datasource ID
            sql: SQL query to execute
            
        Returns:
            Execution result
        """
        try:
            start_time = datetime.utcnow()
            
            # Get database adapter
            if datasource_id not in self._db_adapters:
                self._db_adapters[datasource_id] = DatabaseAdapter(datasource_id)
            
            db_adapter = self._db_adapters[datasource_id]
            
            # Execute SQL
            df = await db_adapter.execute_sql_async(sql)
            
            # Calculate execution time
            execution_time = (datetime.utcnow() - start_time).total_seconds()
            
            # Convert DataFrame to dict format with proper serialization
            def serialize_value(value):
                """Serialize value to JSON-compatible format"""
                if hasattr(value, 'isoformat'):
                    # Handle datetime, date, time objects
                    return value.isoformat()
                elif hasattr(value, '__float__'):
                    # Handle Decimal and other numeric objects
                    return float(value)
                elif value is None or isinstance(value, (str, int, float, bool)):
                    return value
                else:
                    # Fallback to string representation
                    return str(value)

            # Serialize all values in the DataFrame
            serialized_rows = []
            for row in df.values:
                serialized_row = [serialize_value(value) for value in row]
                serialized_rows.append(serialized_row)

            result_data = {
                "columns": df.columns.tolist(),
                "rows": serialized_rows,
                "row_count": len(df)
            }
            
            return {
                "success": True,
                "sql": sql,
                "data": result_data,
                "execution_time": execution_time,
                "executed_at": start_time.isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to execute SQL: {e}")
            return {
                "success": False,
                "error": str(e),
                "sql": sql,
                "executed_at": datetime.utcnow().isoformat()
            }
    
    async def ask_question(self, datasource_id: int, question: str, execute: bool = False, embedding_model_id: Optional[int] = None) -> Dict[str, Any]:
        """
        Complete question-answer flow: generate SQL and optionally execute
        
        Args:
            datasource_id: Database datasource ID
            question: Natural language question
            execute: Whether to execute the generated SQL
            embedding_model_id: Embedding model ID (optional)
            
        Returns:
            Complete answer result
        """
        try:
            # Step 1: Generate SQL
            sql_result = await self.generate_sql(datasource_id, question, embedding_model_id)
            
            if not sql_result["success"]:
                return sql_result
            
            sql = sql_result["sql"]
            response = {
                "success": True,
                "question": question,
                "sql": sql,
                "similar_sqls": sql_result.get("similar_sqls", []),
                "confidence": sql_result.get("confidence", 0.0),
                "generated_at": sql_result["generated_at"]
            }
            
            # Step 2: Execute SQL if requested
            if execute and sql:
                execution_result = await self.execute_sql(datasource_id, sql)
                
                if execution_result["success"]:
                    response.update({
                        "data": execution_result["data"],
                        "execution_time": execution_result["execution_time"],
                        "executed_at": execution_result["executed_at"]
                    })
                else:
                    response.update({
                        "execution_error": execution_result["error"],
                        "executed_at": execution_result["executed_at"]
                    })
            
            return response
            
        except Exception as e:
            logger.error(f"Failed to answer question: {e}")
            return {
                "success": False,
                "error": str(e),
                "question": question,
                "generated_at": datetime.utcnow().isoformat()
            }
    
    async def train_from_ddl(self, datasource_id: int, ddl_statements: List[str], embedding_model_id: Optional[int] = None, database_name: Optional[str] = None, skip_existing: bool = True) -> Dict[str, Any]:
        """
        Train model from DDL statements

        Args:
            datasource_id: Database datasource ID
            ddl_statements: List of DDL statements
            embedding_model_id: Embedding model ID (optional)
            database_name: Database name (optional)
            skip_existing: Whether to skip existing training data

        Returns:
            Training result
        """
        try:
            vanna_instance = self._get_vanna_instance(datasource_id, embedding_model_id)
            results = []
            skipped_count = 0

            # If skip_existing is True, check for already trained tables
            existing_tables = set()
            if skip_existing:
                try:
                    import asyncio
                    from src.config.database import get_database_connection

                    # Use deer-flow's database connection
                    def _check_existing_tables():
                        with get_database_connection() as conn:
                            with conn.cursor() as cursor:
                                cursor.execute("""
                                    SELECT DISTINCT table_name
                                    FROM text2sql.vanna_embeddings
                                    WHERE datasource_id = %s
                                    AND content_type = 'DDL'
                                    AND table_name IS NOT NULL
                                """, (datasource_id,))

                                rows = cursor.fetchall()
                                return {row['table_name'].lower() for row in rows if row['table_name']}

                    existing_tables = await asyncio.to_thread(_check_existing_tables)

                    if existing_tables:
                        logger.info(f"🔄 Found already trained tables: {existing_tables}")

                except Exception as e:
                    logger.warning(f"Failed to check existing tables: {e}")
                    existing_tables = set()

            for ddl in ddl_statements:
                try:
                    # Extract table name from DDL
                    table_name = self._extract_table_name_from_ddl(ddl)

                    # Check if we should skip this table
                    if skip_existing and table_name and table_name.lower() in existing_tables:
                        skipped_count += 1
                        results.append({
                            "ddl": ddl,
                            "success": True,
                            "skipped": True,
                            "table_name": table_name,
                            "reason": "Already exists in training data"
                        })
                        logger.info(f"⏭️ Skipping already trained table: {table_name}")
                        continue

                    # Add DDL to vector store
                    result_id = vanna_instance.add_ddl(
                        ddl,
                        database_name=database_name,
                        table_name=table_name
                    )

                    results.append({
                        "ddl": ddl,
                        "success": True,
                        "skipped": False,
                        "id": result_id,
                        "table_name": table_name
                    })

                except Exception as e:
                    results.append({
                        "ddl": ddl,
                        "success": False,
                        "error": str(e)
                    })
                    logger.error(f"Failed to train DDL: {e}")
            
            successful_count = sum(1 for r in results if r.get("success") and not r.get("skipped"))
            failed_count = sum(1 for r in results if not r.get("success"))

            return {
                "success": True,
                "total_items": len(ddl_statements),
                "successful_items": successful_count,
                "failed_items": failed_count,
                "skipped": skipped_count,
                "results": results
            }
            
        except Exception as e:
            logger.error(f"Failed to train from DDL: {e}")
            return {
                "success": False,
                "error": str(e),
                "total_items": len(ddl_statements)
            }
    
    def _extract_table_name_from_ddl(self, ddl: str) -> Optional[str]:
        """Extract table name from DDL statement"""
        try:
            ddl_upper = ddl.upper().strip()
            if ddl_upper.startswith('CREATE TABLE'):
                # Simple regex to extract table name
                import re
                match = re.search(r'CREATE\s+TABLE\s+(?:IF\s+NOT\s+EXISTS\s+)?(?:`?(\w+)`?\.)?`?(\w+)`?', ddl_upper)
                if match:
                    return match.group(2)  # Return table name without schema
            return None
        except Exception:
            return None

    def _generate_simple_sql_from_ddl(self, question: str, ddl_list: List[str]) -> str:
        """Generate simple SQL based on question and available DDL"""
        try:
            question_lower = question.lower()

            # Extract table names from DDL
            table_names = []
            for ddl in ddl_list:
                table_name = self._extract_table_name_from_ddl(ddl)
                if table_name:
                    table_names.append(table_name)

            if not table_names:
                return "SELECT 1 as result -- No tables found in DDL"

            # Use the first table as primary table
            primary_table = table_names[0]

            # Generate SQL based on question patterns
            if any(word in question_lower for word in ['count', 'how many', '多少', '数量']):
                return f"SELECT COUNT(*) as count FROM {primary_table}"
            elif any(word in question_lower for word in ['all', 'list', 'show', '所有', '列出', '显示']):
                return f"SELECT * FROM {primary_table} LIMIT 10"
            elif any(word in question_lower for word in ['latest', 'recent', '最新', '最近']):
                return f"SELECT * FROM {primary_table} ORDER BY id DESC LIMIT 10"
            else:
                # Default query
                return f"SELECT * FROM {primary_table} LIMIT 10"

        except Exception as e:
            logger.error(f"Failed to generate simple SQL from DDL: {e}")
            return "SELECT 1 as result -- Failed to generate SQL"

    def _calculate_confidence(self, question: str, sql: str, similar_sqls: List[str]) -> float:
        """Calculate confidence score for generated SQL"""
        try:
            # Base confidence
            confidence = 0.5

            # Increase confidence if we have similar SQL examples
            if similar_sqls:
                confidence += 0.2

                # If the generated SQL exactly matches a training example
                if sql in similar_sqls:
                    confidence += 0.2

            # Increase confidence for simple queries
            sql_lower = sql.lower()
            if any(pattern in sql_lower for pattern in ['select *', 'count(*)', 'limit']):
                confidence += 0.1

            # Cap confidence at 0.95
            return min(confidence, 0.95)

        except Exception:
            return 0.5
    
    def clear_cache(self, datasource_id: Optional[int] = None):
        """Clear cache"""
        if datasource_id:
            # Clear specific datasource cache
            keys_to_remove = [k for k in self._vanna_instances.keys() if k.startswith(f"{datasource_id}_")]
            for key in keys_to_remove:
                self._vanna_instances.pop(key, None)
                self._vector_stores.pop(key, None)
            self._db_adapters.pop(datasource_id, None)
            logger.info(f"✅ Cleared cache for datasource {datasource_id}")
        else:
            # Clear all cache
            self._vanna_instances.clear()
            self._vector_stores.clear()
            self._db_adapters.clear()
            logger.info("✅ Cleared all Vanna cache")


# Create global service instance
vanna_service_manager = VannaServiceManager()
