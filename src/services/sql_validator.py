# Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
# SPDX-License-Identifier: MIT

"""
SQL Validator for Text2SQL
验证生成的SQL是否与实际数据库结构匹配
"""

import logging
import re
from typing import List, Dict, Set, Optional, Tuple
from dataclasses import dataclass
from difflib import SequenceMatcher

try:
    import sqlglot
    from sqlglot import parse_one, transpile
    from sqlglot.expressions import Table, Column, Select, Insert, Update, Delete
    SQLGLOT_AVAILABLE = True
except ImportError:
    SQLGLOT_AVAILABLE = False
    # Fallback to basic regex parsing
    sqlglot = None

logger = logging.getLogger(__name__)


@dataclass
class TableInfo:
    """表信息"""
    name: str
    columns: List[str]
    schema: Optional[str] = None


@dataclass
class ValidationResult:
    """验证结果"""
    is_valid: bool
    errors: List[str]
    warnings: List[str]
    missing_tables: List[str]
    missing_columns: List[str]
    suggestions: List[str]


class SQLValidator:
    """SQL验证器 - 确保生成的SQL与实际数据库结构匹配"""
    
    def __init__(self, datasource_id: int):
        self.datasource_id = datasource_id
        self._table_cache: Dict[str, TableInfo] = {}
        self._cache_timestamp: Optional[float] = None
        self._cache_ttl: int = 300  # 5 minutes cache TTL
        self._cache_timestamp = None
    
    async def validate_sql(self, sql: str) -> ValidationResult:
        """
        验证SQL查询是否与数据库结构匹配
        
        Args:
            sql: 要验证的SQL查询
            
        Returns:
            ValidationResult: 验证结果
        """
        try:
            # 检查是否是系统查询（如查询系统表）
            if self._is_system_query(sql):
                return ValidationResult(
                    is_valid=True,
                    errors=[],
                    warnings=[],
                    missing_tables=[],
                    missing_columns=[],
                    suggestions=[]
                )

            # 刷新表信息缓存（如果需要）
            await self._refresh_table_cache_if_needed()
            
            # 解析SQL中的表和列
            tables_in_sql = self._extract_tables_from_sql(sql)
            columns_in_sql = self._extract_columns_from_sql(sql)
            
            errors = []
            warnings = []
            missing_tables = []
            missing_columns = []
            suggestions = []
            
            # 检查表是否存在
            for table_name in tables_in_sql:
                if table_name.lower() not in self._table_cache:
                    missing_tables.append(table_name)
                    errors.append(f"表 '{table_name}' 在数据库中不存在")
                    
                    # 提供相似表名建议
                    similar_tables = self._find_similar_table_names(table_name)
                    if similar_tables:
                        suggestions.append(f"您是否想要查询表: {', '.join(similar_tables)}?")
            
            # 检查列是否存在（只检查存在的表）
            for table_name in tables_in_sql:
                if table_name.lower() in self._table_cache:
                    table_info = self._table_cache[table_name.lower()]
                    table_columns = [col.lower() for col in table_info.columns]
                    
                    # 检查该表相关的列
                    for column_name in columns_in_sql:
                        # 简单检查：如果列名不在任何已知表中，标记为可能的问题
                        if column_name.lower() not in table_columns:
                            # 检查是否是通配符或函数
                            if column_name not in ['*'] and not self._is_sql_function(column_name):
                                missing_columns.append(f"{table_name}.{column_name}")
                                warnings.append(f"列 '{column_name}' 在表 '{table_name}' 中可能不存在")
                                
                                # 提供相似列名建议
                                similar_columns = self._find_similar_column_names(column_name, table_columns)
                                if similar_columns:
                                    suggestions.append(f"在表 '{table_name}' 中，您是否想要查询列: {', '.join(similar_columns)}?")
            
            # 如果有缺失的表，这是严重错误
            is_valid = len(missing_tables) == 0
            
            if not is_valid:
                suggestions.append("请检查您的问题是否涉及数据库中实际存在的业务表")
                suggestions.append("您可以先查看数据库结构或添加相关的DDL训练数据")
            
            return ValidationResult(
                is_valid=is_valid,
                errors=errors,
                warnings=warnings,
                missing_tables=missing_tables,
                missing_columns=missing_columns,
                suggestions=suggestions
            )
            
        except Exception as e:
            logger.error(f"SQL validation failed: {e}")
            return ValidationResult(
                is_valid=False,
                errors=[f"验证过程出错: {str(e)}"],
                warnings=[],
                missing_tables=[],
                missing_columns=[],
                suggestions=["请检查SQL语法是否正确"]
            )
    
    async def _refresh_table_cache_if_needed(self):
        """根据需要刷新表信息缓存"""
        import time
        current_time = time.time()

        # 检查缓存是否需要刷新
        if (self._cache_timestamp is None or
            current_time - self._cache_timestamp > self._cache_ttl or
            not self._table_cache):
            await self._refresh_table_cache()
            self._cache_timestamp = current_time

    async def _refresh_table_cache(self):
        """刷新表信息缓存"""
        try:
            from src.services.database_datasource import DatabaseDatasourceService

            datasource_service = DatabaseDatasourceService()
            datasource = await datasource_service.get_datasource(self.datasource_id)

            if not datasource:
                logger.error(f"Datasource {self.datasource_id} not found")
                return

            # 获取数据库表结构
            schema_info = await datasource_service.get_database_schema(self.datasource_id)

            # 更新缓存
            self._table_cache.clear()
            for table in schema_info.tables:
                full_table_name = table.get('table_name', '').lower()
                simple_table_name = table.get('table_name_only', '').lower()
                columns = [col.get('column_name', '') for col in table.get('columns', [])]
                schema_name = table.get('schema_name', '')

                table_info = TableInfo(
                    name=full_table_name,
                    columns=columns,
                    schema=schema_name
                )

                # 同时存储完整表名和简单表名，以便查找
                self._table_cache[full_table_name] = table_info
                if simple_table_name and simple_table_name != full_table_name:
                    self._table_cache[simple_table_name] = table_info

            logger.info(f"Refreshed table cache with {len(self._table_cache)} tables")

        except Exception as e:
            logger.error(f"Failed to refresh table cache: {e}")

    def _is_system_query(self, sql: str) -> bool:
        """检查是否是系统查询（如查询系统表）"""
        sql_upper = sql.upper().strip()

        # 系统表和系统schema
        system_patterns = [
            r'INFORMATION_SCHEMA\.',
            r'PG_CATALOG\.',
            r'SYS\.',
            r'MYSQL\.',
            r'PERFORMANCE_SCHEMA\.',
            r'DATABASE\(\)',
            r'SCHEMA\(\)',
            r'CURRENT_DATABASE\(\)',
            r'CURRENT_SCHEMA\(\)',
            r'SHOW\s+TABLES',
            r'SHOW\s+DATABASES',
            r'SHOW\s+SCHEMAS',
            r'DESC\s+',
            r'DESCRIBE\s+',
            r'EXPLAIN\s+',
        ]

        for pattern in system_patterns:
            if re.search(pattern, sql_upper):
                return True

        return False

    def _extract_tables_from_sql(self, sql: str) -> List[str]:
        """从SQL中提取表名 - 使用 sqlglot 进行精确解析"""
        try:
            if SQLGLOT_AVAILABLE:
                return self._extract_tables_with_sqlglot(sql)
            else:
                return self._extract_tables_with_regex(sql)
        except Exception as e:
            logger.error(f"Failed to extract tables from SQL: {e}")
            # 降级到正则表达式方法
            return self._extract_tables_with_regex(sql)

    def _extract_tables_with_sqlglot(self, sql: str) -> List[str]:
        """使用 sqlglot 提取表名"""
        try:
            # 尝试解析 SQL
            parsed = parse_one(sql, dialect="postgres")  # 默认使用 PostgreSQL 方言

            tables = set()

            # 遍历 AST 查找所有表引用
            for table in parsed.find_all(Table):
                table_name = table.name
                if table_name:
                    tables.add(table_name.lower())

            return list(tables)

        except Exception as e:
            logger.warning(f"sqlglot parsing failed, falling back to regex: {e}")
            return self._extract_tables_with_regex(sql)

    def _extract_tables_with_regex(self, sql: str) -> List[str]:
        """使用正则表达式提取表名（备用方法）"""
        try:
            sql_upper = sql.upper().strip()
            tables = []

            # 更全面的正则表达式模式
            patterns = [
                # SELECT ... FROM table
                r'FROM\s+(?:(?:`?(\w+)`?\.)?`?(\w+)`?(?:\s+(?:AS\s+)?`?\w+`?)?)',
                # JOIN table
                r'(?:INNER\s+|LEFT\s+|RIGHT\s+|FULL\s+|CROSS\s+)?JOIN\s+(?:(?:`?(\w+)`?\.)?`?(\w+)`?(?:\s+(?:AS\s+)?`?\w+`?)?)',
                # INSERT INTO table
                r'INSERT\s+INTO\s+(?:(?:`?(\w+)`?\.)?`?(\w+)`?)',
                # UPDATE table
                r'UPDATE\s+(?:(?:`?(\w+)`?\.)?`?(\w+)`?)',
                # DELETE FROM table
                r'DELETE\s+FROM\s+(?:(?:`?(\w+)`?\.)?`?(\w+)`?)',
                # WITH table AS
                r'WITH\s+(?:`?(\w+)`?\s+AS)',
            ]

            for pattern in patterns:
                matches = re.finditer(pattern, sql_upper)
                for match in matches:
                    # 获取表名（优先使用第二个组，如果没有则使用第一个）
                    groups = match.groups()
                    schema_name = None
                    table_name = None

                    # 提取 schema 和 table 名称
                    if len(groups) >= 2:
                        schema_name = groups[0] if groups[0] and groups[0].strip() else None
                        table_name = groups[1] if groups[1] and groups[1].strip() else None
                    elif len(groups) >= 1:
                        table_name = groups[0] if groups[0] and groups[0].strip() else None

                    if table_name:
                        # 构建完整表名和简单表名
                        simple_name = table_name.lower()
                        full_name = f"{schema_name.lower()}.{simple_name}" if schema_name else simple_name

                        # 添加两种形式的表名
                        if simple_name not in [t.lower() for t in tables]:
                            tables.append(simple_name)
                        if full_name != simple_name and full_name not in [t.lower() for t in tables]:
                            tables.append(full_name)

            return tables

        except Exception as e:
            logger.error(f"Regex table extraction failed: {e}")
            return []
    
    def _extract_columns_from_sql(self, sql: str) -> List[str]:
        """从SQL中提取列名 - 使用 sqlglot 进行精确解析"""
        try:
            if SQLGLOT_AVAILABLE:
                return self._extract_columns_with_sqlglot(sql)
            else:
                return self._extract_columns_with_regex(sql)
        except Exception as e:
            logger.error(f"Failed to extract columns from SQL: {e}")
            # 降级到正则表达式方法
            return self._extract_columns_with_regex(sql)

    def _extract_columns_with_sqlglot(self, sql: str) -> List[str]:
        """使用 sqlglot 提取列名"""
        try:
            # 尝试解析 SQL
            parsed = parse_one(sql, dialect="postgres")

            columns = set()

            # 遍历 AST 查找所有列引用
            for column in parsed.find_all(Column):
                column_name = column.name
                if column_name and column_name != "*":
                    columns.add(column_name.lower())

            # 对于 SELECT 语句，还需要检查选择列表
            if isinstance(parsed, Select):
                for expression in parsed.expressions:
                    if hasattr(expression, 'name') and expression.name:
                        columns.add(expression.name.lower())
                    elif hasattr(expression, 'alias') and expression.alias:
                        columns.add(expression.alias.lower())

            return list(columns)

        except Exception as e:
            logger.warning(f"sqlglot column parsing failed, falling back to regex: {e}")
            return self._extract_columns_with_regex(sql)

    def _extract_columns_with_regex(self, sql: str) -> List[str]:
        """使用正则表达式提取列名（备用方法）"""
        try:
            columns = set()

            # 提取 SELECT 子句中的列名
            select_pattern = r'SELECT\s+(.*?)\s+FROM'
            select_match = re.search(select_pattern, sql, re.IGNORECASE | re.DOTALL)

            if select_match:
                select_clause = select_match.group(1).strip()

                # 处理复杂的 SELECT 子句
                columns.update(self._parse_select_clause(select_clause))

            # 提取 WHERE 子句中的列名
            where_pattern = r'WHERE\s+(.*?)(?:\s+(?:GROUP\s+BY|ORDER\s+BY|HAVING|LIMIT|$))'
            where_match = re.search(where_pattern, sql, re.IGNORECASE | re.DOTALL)

            if where_match:
                where_clause = where_match.group(1).strip()
                columns.update(self._parse_where_clause(where_clause))

            # 提取 ORDER BY 子句中的列名
            order_pattern = r'ORDER\s+BY\s+(.*?)(?:\s+(?:LIMIT|$))'
            order_match = re.search(order_pattern, sql, re.IGNORECASE | re.DOTALL)

            if order_match:
                order_clause = order_match.group(1).strip()
                columns.update(self._parse_order_clause(order_clause))

            # 提取 GROUP BY 子句中的列名
            group_pattern = r'GROUP\s+BY\s+(.*?)(?:\s+(?:HAVING|ORDER\s+BY|LIMIT|$))'
            group_match = re.search(group_pattern, sql, re.IGNORECASE | re.DOTALL)

            if group_match:
                group_clause = group_match.group(1).strip()
                columns.update(self._parse_group_clause(group_clause))

            return list(columns)

        except Exception as e:
            logger.error(f"Regex column extraction failed: {e}")
            return []

    def _parse_select_clause(self, select_clause: str) -> Set[str]:
        """解析 SELECT 子句中的列名"""
        columns = set()

        # 分割列名，考虑括号和引号
        parts = self._smart_split(select_clause, ',')

        for part in parts:
            part = part.strip()

            # 跳过通配符
            if part == '*' or part.endswith('.*'):
                continue

            # 跳过明显的函数调用
            if self._is_function_call(part):
                continue

            # 提取列名
            column_name = self._extract_column_name(part)
            if column_name:
                columns.add(column_name.lower())

        return columns

    def _parse_where_clause(self, where_clause: str) -> Set[str]:
        """解析 WHERE 子句中的列名"""
        columns = set()

        # 简单的列名提取，匹配 column = value 或 column IN (...) 等模式
        patterns = [
            r'(?:^|\s|,|\()\s*(?:`?(\w+)`?\.)?`?(\w+)`?\s*(?:=|!=|<>|<|>|<=|>=|IN|NOT\s+IN|LIKE|NOT\s+LIKE|IS|IS\s+NOT)',
            r'(?:^|\s|,|\()\s*(?:`?(\w+)`?\.)?`?(\w+)`?\s*(?:BETWEEN)',
        ]

        for pattern in patterns:
            matches = re.finditer(pattern, where_clause, re.IGNORECASE)
            for match in matches:
                groups = match.groups()
                column_name = groups[-1] if groups[-1] else groups[-2] if len(groups) > 1 else None
                if column_name and not self._is_sql_keyword(column_name):
                    columns.add(column_name.lower())

        return columns

    def _parse_order_clause(self, order_clause: str) -> Set[str]:
        """解析 ORDER BY 子句中的列名"""
        columns = set()

        parts = self._smart_split(order_clause, ',')
        for part in parts:
            part = part.strip()
            # 移除 ASC/DESC
            part = re.sub(r'\s+(ASC|DESC)$', '', part, flags=re.IGNORECASE)

            column_name = self._extract_column_name(part)
            if column_name:
                columns.add(column_name.lower())

        return columns

    def _parse_group_clause(self, group_clause: str) -> Set[str]:
        """解析 GROUP BY 子句中的列名"""
        columns = set()

        parts = self._smart_split(group_clause, ',')
        for part in parts:
            part = part.strip()

            column_name = self._extract_column_name(part)
            if column_name:
                columns.add(column_name.lower())

        return columns

    def _smart_split(self, text: str, delimiter: str) -> List[str]:
        """智能分割，考虑括号和引号"""
        parts = []
        current_part = ""
        paren_count = 0
        in_quotes = False
        quote_char = None

        i = 0
        while i < len(text):
            char = text[i]

            if char in ('"', "'", '`') and not in_quotes:
                in_quotes = True
                quote_char = char
            elif char == quote_char and in_quotes:
                in_quotes = False
                quote_char = None
            elif not in_quotes:
                if char == '(':
                    paren_count += 1
                elif char == ')':
                    paren_count -= 1
                elif char == delimiter and paren_count == 0:
                    parts.append(current_part.strip())
                    current_part = ""
                    i += 1
                    continue

            current_part += char
            i += 1

        if current_part.strip():
            parts.append(current_part.strip())

        return parts

    def _extract_column_name(self, expression: str) -> Optional[str]:
        """从表达式中提取列名"""
        expression = expression.strip()

        # 处理别名 (column AS alias 或 column alias)
        alias_match = re.search(r'^(.+?)\s+(?:AS\s+)?(?:`?(\w+)`?)$', expression, re.IGNORECASE)
        if alias_match:
            expression = alias_match.group(1).strip()

        # 处理 table.column 格式
        if '.' in expression:
            parts = expression.split('.')
            column_name = parts[-1].strip('`"[]')
        else:
            column_name = expression.strip('`"[]')

        # 验证是否为有效的列名
        if re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', column_name):
            return column_name

        return None

    def _is_function_call(self, expression: str) -> bool:
        """检查是否为函数调用"""
        # 常见的 SQL 函数
        functions = [
            'COUNT', 'SUM', 'AVG', 'MAX', 'MIN', 'DISTINCT',
            'UPPER', 'LOWER', 'LENGTH', 'SUBSTRING', 'CONCAT',
            'NOW', 'CURRENT_DATE', 'CURRENT_TIME', 'CURRENT_TIMESTAMP',
            'COALESCE', 'ISNULL', 'NULLIF', 'CASE'
        ]

        expression_upper = expression.upper().strip()

        # 检查是否包含函数名和括号
        for func in functions:
            if func in expression_upper and '(' in expression:
                return True

        # 检查是否为 CASE 表达式
        if expression_upper.startswith('CASE'):
            return True

        return False

    def _is_sql_keyword(self, word: str) -> bool:
        """检查是否为 SQL 关键字"""
        keywords = [
            'SELECT', 'FROM', 'WHERE', 'JOIN', 'INNER', 'LEFT', 'RIGHT', 'FULL',
            'ON', 'AND', 'OR', 'NOT', 'IN', 'EXISTS', 'BETWEEN', 'LIKE',
            'IS', 'NULL', 'TRUE', 'FALSE', 'ASC', 'DESC', 'GROUP', 'BY',
            'HAVING', 'ORDER', 'LIMIT', 'OFFSET', 'UNION', 'ALL', 'DISTINCT'
        ]

        return word.upper() in keywords
    
    def _find_similar_table_names(self, target_table: str) -> List[str]:
        """查找相似的表名 - 使用多种相似度算法"""
        try:
            target_lower = target_table.lower()
            similarities = []

            for table_name in self._table_cache.keys():
                # 计算多种相似度分数
                scores = {
                    'exact_match': 1.0 if target_lower == table_name else 0.0,
                    'substring': self._substring_similarity(target_lower, table_name),
                    'levenshtein': self._levenshtein_similarity(target_lower, table_name),
                    'jaro_winkler': self._jaro_winkler_similarity(target_lower, table_name),
                    'semantic': self._semantic_similarity(target_lower, table_name)
                }

                # 加权平均分数
                weighted_score = (
                    scores['exact_match'] * 1.0 +
                    scores['substring'] * 0.3 +
                    scores['levenshtein'] * 0.25 +
                    scores['jaro_winkler'] * 0.25 +
                    scores['semantic'] * 0.2
                )

                if weighted_score > 0.4:  # 阈值
                    similarities.append((table_name, weighted_score, scores))

            # 按相似度排序
            similarities.sort(key=lambda x: x[1], reverse=True)

            # 返回最相似的表名
            return [item[0] for item in similarities[:5]]

        except Exception as e:
            logger.error(f"Failed to find similar table names: {e}")
            return []

    def _substring_similarity(self, str1: str, str2: str) -> float:
        """子字符串相似度"""
        if str1 in str2 or str2 in str1:
            return 0.8

        # 检查共同子字符串
        common_substrings = []
        for i in range(len(str1)):
            for j in range(i + 2, len(str1) + 1):  # 至少2个字符
                substring = str1[i:j]
                if substring in str2:
                    common_substrings.append(substring)

        if common_substrings:
            max_length = max(len(s) for s in common_substrings)
            return max_length / max(len(str1), len(str2))

        return 0.0

    def _levenshtein_similarity(self, str1: str, str2: str) -> float:
        """Levenshtein 距离相似度"""
        if len(str1) == 0:
            return 0.0 if len(str2) > 0 else 1.0
        if len(str2) == 0:
            return 0.0

        # 创建距离矩阵
        matrix = [[0] * (len(str2) + 1) for _ in range(len(str1) + 1)]

        # 初始化第一行和第一列
        for i in range(len(str1) + 1):
            matrix[i][0] = i
        for j in range(len(str2) + 1):
            matrix[0][j] = j

        # 填充矩阵
        for i in range(1, len(str1) + 1):
            for j in range(1, len(str2) + 1):
                if str1[i-1] == str2[j-1]:
                    cost = 0
                else:
                    cost = 1

                matrix[i][j] = min(
                    matrix[i-1][j] + 1,      # 删除
                    matrix[i][j-1] + 1,      # 插入
                    matrix[i-1][j-1] + cost  # 替换
                )

        distance = matrix[len(str1)][len(str2)]
        max_length = max(len(str1), len(str2))

        return 1.0 - (distance / max_length)

    def _jaro_winkler_similarity(self, str1: str, str2: str) -> float:
        """Jaro-Winkler 相似度"""
        # 使用 difflib 的 SequenceMatcher 作为近似
        matcher = SequenceMatcher(None, str1, str2)
        return matcher.ratio()

    def _semantic_similarity(self, str1: str, str2: str) -> float:
        """语义相似度 - 基于常见的表名模式"""
        # 常见的表名同义词和相关词
        semantic_groups = [
            ['user', 'users', 'account', 'accounts', 'member', 'members'],
            ['order', 'orders', 'purchase', 'purchases', 'transaction', 'transactions'],
            ['product', 'products', 'item', 'items', 'goods', 'merchandise'],
            ['category', 'categories', 'type', 'types', 'class', 'classes'],
            ['log', 'logs', 'history', 'record', 'records', 'audit'],
            ['config', 'configuration', 'setting', 'settings', 'option', 'options'],
            ['file', 'files', 'document', 'documents', 'attachment', 'attachments'],
            ['role', 'roles', 'permission', 'permissions', 'privilege', 'privileges'],
            ['session', 'sessions', 'token', 'tokens', 'auth', 'authentication'],
            ['comment', 'comments', 'review', 'reviews', 'feedback', 'feedbacks']
        ]

        # 检查是否在同一语义组中
        for group in semantic_groups:
            if str1 in group and str2 in group:
                return 0.7

        # 检查词根相似性
        if self._have_common_root(str1, str2):
            return 0.5

        return 0.0

    def _have_common_root(self, str1: str, str2: str) -> bool:
        """检查是否有共同词根"""
        # 简单的词根检查
        min_length = min(len(str1), len(str2))
        if min_length < 3:
            return False

        # 检查前缀
        for i in range(3, min_length + 1):
            if str1[:i] == str2[:i]:
                return True

        # 检查后缀
        for i in range(3, min_length + 1):
            if str1[-i:] == str2[-i:]:
                return True

        return False
    
    def _find_similar_column_names(self, target_column: str, available_columns: List[str]) -> List[str]:
        """查找相似的列名 - 使用多种相似度算法"""
        try:
            target_lower = target_column.lower()
            similarities = []

            for column_name in available_columns:
                column_lower = column_name.lower()

                # 计算多种相似度分数
                scores = {
                    'exact_match': 1.0 if target_lower == column_lower else 0.0,
                    'substring': self._substring_similarity(target_lower, column_lower),
                    'levenshtein': self._levenshtein_similarity(target_lower, column_lower),
                    'jaro_winkler': self._jaro_winkler_similarity(target_lower, column_lower),
                    'semantic': self._column_semantic_similarity(target_lower, column_lower)
                }

                # 加权平均分数（列名相似度权重略有不同）
                weighted_score = (
                    scores['exact_match'] * 1.0 +
                    scores['substring'] * 0.35 +
                    scores['levenshtein'] * 0.3 +
                    scores['jaro_winkler'] * 0.25 +
                    scores['semantic'] * 0.1
                )

                if weighted_score > 0.5:  # 列名使用更高的阈值
                    similarities.append((column_name, weighted_score, scores))

            # 按相似度排序
            similarities.sort(key=lambda x: x[1], reverse=True)

            # 返回最相似的列名
            return [item[0] for item in similarities[:3]]

        except Exception as e:
            logger.error(f"Failed to find similar column names: {e}")
            return []

    def _column_semantic_similarity(self, str1: str, str2: str) -> float:
        """列名语义相似度 - 基于常见的列名模式"""
        # 常见的列名同义词和相关词
        column_semantic_groups = [
            ['id', 'pk', 'primary_key', 'key', 'identifier'],
            ['name', 'title', 'label', 'display_name', 'full_name'],
            ['email', 'mail', 'email_address', 'e_mail'],
            ['phone', 'telephone', 'mobile', 'phone_number', 'tel'],
            ['address', 'addr', 'location', 'street', 'address_line'],
            ['date', 'time', 'datetime', 'timestamp', 'created_at', 'updated_at'],
            ['status', 'state', 'condition', 'flag', 'is_active', 'enabled'],
            ['price', 'cost', 'amount', 'value', 'fee', 'charge'],
            ['count', 'number', 'num', 'quantity', 'qty', 'total'],
            ['description', 'desc', 'detail', 'details', 'comment', 'note'],
            ['type', 'kind', 'category', 'class', 'group', 'classification'],
            ['url', 'link', 'uri', 'path', 'endpoint', 'href'],
            ['image', 'img', 'picture', 'photo', 'avatar', 'thumbnail'],
            ['password', 'pwd', 'pass', 'secret', 'hash', 'encrypted'],
            ['first_name', 'fname', 'given_name', 'forename'],
            ['last_name', 'lname', 'surname', 'family_name'],
            ['created', 'created_at', 'create_time', 'creation_date'],
            ['updated', 'updated_at', 'update_time', 'modification_date', 'modified'],
            ['deleted', 'deleted_at', 'delete_time', 'removal_date', 'removed']
        ]

        # 检查是否在同一语义组中
        for group in column_semantic_groups:
            if str1 in group and str2 in group:
                return 0.8

        # 检查常见前缀/后缀模式
        common_patterns = [
            ('is_', 'has_', 'can_', 'should_'),  # 布尔值前缀
            ('_id', '_key', '_pk'),              # ID 后缀
            ('_at', '_time', '_date'),           # 时间后缀
            ('_count', '_num', '_total'),        # 数量后缀
            ('_url', '_link', '_path'),          # 链接后缀
        ]

        for pattern_group in common_patterns:
            str1_matches = any(str1.startswith(p) or str1.endswith(p) for p in pattern_group)
            str2_matches = any(str2.startswith(p) or str2.endswith(p) for p in pattern_group)

            if str1_matches and str2_matches:
                return 0.6

        # 检查词根相似性
        if self._have_common_root(str1, str2):
            return 0.4

        return 0.0
    

    
    def _is_sql_function(self, text: str) -> bool:
        """检查是否是SQL函数"""
        sql_functions = [
            'COUNT', 'SUM', 'AVG', 'MAX', 'MIN', 'DISTINCT',
            'NOW', 'CURRENT_DATE', 'CURRENT_TIME', 'CURRENT_TIMESTAMP',
            'UPPER', 'LOWER', 'LENGTH', 'SUBSTRING', 'CONCAT'
        ]
        
        return any(func in text.upper() for func in sql_functions)
