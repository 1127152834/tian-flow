#!/usr/bin/env python3
"""
SQL Parser utilities for extracting table names and other metadata
"""

import re
from typing import List, Set, Optional
import logging

logger = logging.getLogger(__name__)

class SQLParser:
    """SQL parser for extracting table names and metadata"""
    
    def __init__(self):
        # Common SQL keywords that might precede table names
        self.table_keywords = [
            r'\bFROM\s+',
            r'\bJOIN\s+',
            r'\bINNER\s+JOIN\s+',
            r'\bLEFT\s+JOIN\s+',
            r'\bRIGHT\s+JOIN\s+',
            r'\bFULL\s+JOIN\s+',
            r'\bCROSS\s+JOIN\s+',
            r'\bINTO\s+',
            r'\bUPDATE\s+',
            r'\bINSERT\s+INTO\s+',
            r'\bDELETE\s+FROM\s+',
            r'\bTRUNCATE\s+TABLE\s+',
            r'\bDROP\s+TABLE\s+',
            r'\bCREATE\s+TABLE\s+',
            r'\bALTER\s+TABLE\s+',
        ]
        
        # Pattern to match table names (with optional schema)
        self.table_pattern = r'([a-zA-Z_][a-zA-Z0-9_]*(?:\.[a-zA-Z_][a-zA-Z0-9_]*)?)'
        
        # Pattern to match quoted table names
        self.quoted_table_pattern = r'(["`\[]([^"`\]]+)["`\]](?:\.["`\[]([^"`\]]+)["`\]])?)'
    
    def extract_table_names(self, sql: str) -> List[str]:
        """
        Extract all table names from SQL query
        
        Args:
            sql: SQL query string
            
        Returns:
            List of unique table names
        """
        try:
            if not sql or not sql.strip():
                return []
            
            # Clean up SQL - remove comments and normalize whitespace
            cleaned_sql = self._clean_sql(sql)
            
            table_names = set()
            
            # Extract tables using keyword patterns
            for keyword in self.table_keywords:
                pattern = keyword + self.table_pattern
                matches = re.finditer(pattern, cleaned_sql, re.IGNORECASE)
                
                for match in matches:
                    table_name = match.group(1)
                    # Clean up table name
                    table_name = self._clean_table_name(table_name)
                    if table_name:
                        table_names.add(table_name)
            
            # Also try to extract quoted table names
            for keyword in self.table_keywords:
                pattern = keyword + self.quoted_table_pattern
                matches = re.finditer(pattern, cleaned_sql, re.IGNORECASE)
                
                for match in matches:
                    # Extract table name from quotes
                    if match.group(3):  # schema.table format
                        table_name = f"{match.group(2)}.{match.group(3)}"
                    else:  # just table format
                        table_name = match.group(2)
                    
                    table_name = self._clean_table_name(table_name)
                    if table_name:
                        table_names.add(table_name)
            
            # Convert to sorted list for consistency
            result = sorted(list(table_names))
            
            logger.debug(f"Extracted table names from SQL: {result}")
            return result
            
        except Exception as e:
            logger.error(f"Failed to extract table names from SQL: {e}")
            return []
    
    def _clean_sql(self, sql: str) -> str:
        """Clean SQL by removing comments and normalizing whitespace"""
        try:
            # Remove single-line comments
            sql = re.sub(r'--.*$', '', sql, flags=re.MULTILINE)
            
            # Remove multi-line comments
            sql = re.sub(r'/\*.*?\*/', '', sql, flags=re.DOTALL)
            
            # Normalize whitespace
            sql = re.sub(r'\s+', ' ', sql)
            
            return sql.strip()
            
        except Exception as e:
            logger.error(f"Failed to clean SQL: {e}")
            return sql
    
    def _clean_table_name(self, table_name: str) -> Optional[str]:
        """Clean and validate table name"""
        try:
            if not table_name:
                return None
            
            # Remove quotes and brackets
            table_name = re.sub(r'["`\[\]]', '', table_name)
            
            # Remove trailing commas, semicolons, parentheses
            table_name = re.sub(r'[,;()]+$', '', table_name)
            
            # Remove leading/trailing whitespace
            table_name = table_name.strip()
            
            # Skip if it's a SQL keyword or function
            sql_keywords = {
                'SELECT', 'FROM', 'WHERE', 'JOIN', 'INNER', 'LEFT', 'RIGHT', 'FULL', 'CROSS',
                'ON', 'AND', 'OR', 'NOT', 'IN', 'EXISTS', 'BETWEEN', 'LIKE', 'IS', 'NULL',
                'ORDER', 'BY', 'GROUP', 'HAVING', 'LIMIT', 'OFFSET', 'UNION', 'ALL', 'DISTINCT',
                'COUNT', 'SUM', 'AVG', 'MIN', 'MAX', 'CASE', 'WHEN', 'THEN', 'ELSE', 'END',
                'AS', 'ASC', 'DESC', 'VALUES', 'DEFAULT', 'PRIMARY', 'KEY', 'FOREIGN', 'REFERENCES'
            }
            
            if table_name.upper() in sql_keywords:
                return None
            
            # Must be a valid identifier
            if not re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*(?:\.[a-zA-Z_][a-zA-Z0-9_]*)?$', table_name):
                return None
            
            return table_name
            
        except Exception as e:
            logger.error(f"Failed to clean table name '{table_name}': {e}")
            return None
    
    def get_primary_table(self, sql: str) -> Optional[str]:
        """
        Get the primary table from SQL (usually the first table in FROM clause)
        
        Args:
            sql: SQL query string
            
        Returns:
            Primary table name or None
        """
        try:
            table_names = self.extract_table_names(sql)
            
            if not table_names:
                return None
            
            # For simple queries, return the first table
            # For complex queries, try to identify the main table
            cleaned_sql = self._clean_sql(sql).upper()
            
            # Look for FROM clause specifically
            from_match = re.search(r'\bFROM\s+([a-zA-Z_][a-zA-Z0-9_]*(?:\.[a-zA-Z_][a-zA-Z0-9_]*)?)', 
                                 cleaned_sql, re.IGNORECASE)
            
            if from_match:
                primary_table = self._clean_table_name(from_match.group(1))
                if primary_table and primary_table in table_names:
                    return primary_table
            
            # Fallback to first table
            return table_names[0]
            
        except Exception as e:
            logger.error(f"Failed to get primary table from SQL: {e}")
            return None


# Global instance
sql_parser = SQLParser()
