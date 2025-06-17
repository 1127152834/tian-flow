# Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
# SPDX-License-Identifier: MIT

"""
数据库触发器SQL生成器

为资源发现系统生成标准化的PostgreSQL触发器SQL
"""

import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class TriggerConfig:
    """触发器配置"""
    table_name: str
    fields: List[str]
    trigger_prefix: str = "rd_trigger_"
    notify_channel_prefix: str = "rd_notify_"
    operations: List[str] = None  # INSERT, UPDATE, DELETE
    
    def __post_init__(self):
        if self.operations is None:
            self.operations = ["INSERT", "UPDATE", "DELETE"]


class TriggerSQLGenerator:
    """触发器SQL生成器"""
    
    def __init__(self):
        self.generated_triggers: Dict[str, Dict[str, str]] = {}
    
    def generate_trigger_function(self, config: TriggerConfig) -> str:
        """生成触发器函数SQL（优化版本，避免 payload 过长）"""
        function_name = f"{config.trigger_prefix}function_{config.table_name.replace('.', '_')}"
        channel_name = f"{config.notify_channel_prefix}{config.table_name.replace('.', '_')}"

        # 构建字段提取逻辑
        field_extraction_old = self._generate_field_extraction_for_old(config.fields)
        field_extraction_new = self._generate_field_extraction_for_new(config.fields)

        sql = f"""
-- 资源发现触发器函数: {config.table_name} (优化版本)
CREATE OR REPLACE FUNCTION {function_name}()
RETURNS TRIGGER AS $$
DECLARE
    payload_text TEXT;
    operation_type TEXT;
    record_id_val INTEGER;
    field_data JSON;
BEGIN
    -- 确定操作类型和记录ID
    IF TG_OP = 'DELETE' THEN
        operation_type := 'DELETE';
        record_id_val := OLD.id;
    ELSIF TG_OP = 'UPDATE' THEN
        operation_type := 'UPDATE';
        record_id_val := NEW.id;
    ELSIF TG_OP = 'INSERT' THEN
        operation_type := 'INSERT';
        record_id_val := NEW.id;
    END IF;

    -- 构建字段数据（只包含指定字段，避免大字段）
    IF TG_OP = 'DELETE' THEN
        field_data := json_build_object({field_extraction_old});
    ELSE
        field_data := json_build_object({field_extraction_new});
    END IF;

    -- 构建简化的通知载荷
    payload_text := json_build_object(
        'table_name', TG_TABLE_SCHEMA || '.' || TG_TABLE_NAME,
        'operation', operation_type,
        'record_id', record_id_val,
        'timestamp', EXTRACT(EPOCH FROM NOW()),
        'fields', field_data
    )::text;

    -- 检查 payload 长度，如果太长则截断
    IF LENGTH(payload_text) > 7000 THEN
        payload_text := json_build_object(
            'table_name', TG_TABLE_SCHEMA || '.' || TG_TABLE_NAME,
            'operation', operation_type,
            'record_id', record_id_val,
            'timestamp', EXTRACT(EPOCH FROM NOW()),
            'truncated', true,
            'message', 'Payload truncated due to size limit'
        )::text;
    END IF;

    -- 发送通知
    PERFORM pg_notify('{channel_name}', payload_text);

    -- 返回适当的记录
    IF TG_OP = 'DELETE' THEN
        RETURN OLD;
    ELSE
        RETURN NEW;
    END IF;
END;
$$ LANGUAGE plpgsql;
"""
        return sql.strip()
    
    def generate_trigger_creation(self, config: TriggerConfig) -> str:
        """生成创建触发器的SQL"""
        function_name = f"{config.trigger_prefix}function_{config.table_name.replace('.', '_')}"
        trigger_name = f"{config.trigger_prefix}{config.table_name.replace('.', '_')}"
        
        # 构建操作列表
        operations_str = " OR ".join(config.operations)
        
        sql = f"""
-- 创建资源发现触发器: {config.table_name}
DROP TRIGGER IF EXISTS {trigger_name} ON {config.table_name};

CREATE TRIGGER {trigger_name}
    AFTER {operations_str}
    ON {config.table_name}
    FOR EACH ROW
    EXECUTE FUNCTION {function_name}();
"""
        return sql.strip()
    
    def generate_trigger_removal(self, config: TriggerConfig) -> str:
        """生成删除触发器的SQL"""
        function_name = f"{config.trigger_prefix}function_{config.table_name.replace('.', '_')}"
        trigger_name = f"{config.trigger_prefix}{config.table_name.replace('.', '_')}"
        
        sql = f"""
-- 删除资源发现触发器: {config.table_name}
DROP TRIGGER IF EXISTS {trigger_name} ON {config.table_name};
DROP FUNCTION IF EXISTS {function_name}();
"""
        return sql.strip()
    
    def generate_complete_trigger_setup(self, config: TriggerConfig) -> str:
        """生成完整的触发器设置SQL"""
        function_sql = self.generate_trigger_function(config)
        trigger_sql = self.generate_trigger_creation(config)
        
        return f"{function_sql}\n\n{trigger_sql}"
    
    def _generate_field_extraction(self, fields: List[str]) -> str:
        """生成字段提取逻辑（兼容旧版本）"""
        extractions = []
        for field in fields:
            # 安全的字段名处理
            safe_field = field.replace("'", "''")
            extractions.append(f"'{safe_field}', COALESCE(record_data->>'{safe_field}', '')")

        return ", ".join(extractions)

    def _generate_field_extraction_for_old(self, fields: List[str]) -> str:
        """生成 OLD 记录的字段提取逻辑"""
        extractions = []
        for field in fields:
            # 安全的字段名处理
            safe_field = field.replace("'", "''")
            # 对于文本字段，限制长度以避免 payload 过大
            if field.lower() in ['content', 'question', 'sql_query', 'description']:
                extractions.append(f"'{safe_field}', LEFT(COALESCE(OLD.{safe_field}::text, ''), 100)")
            else:
                extractions.append(f"'{safe_field}', COALESCE(OLD.{safe_field}::text, '')")

        return ", ".join(extractions)

    def _generate_field_extraction_for_new(self, fields: List[str]) -> str:
        """生成 NEW 记录的字段提取逻辑"""
        extractions = []
        for field in fields:
            # 安全的字段名处理
            safe_field = field.replace("'", "''")
            # 对于文本字段，限制长度以避免 payload 过大
            if field.lower() in ['content', 'question', 'sql_query', 'description']:
                extractions.append(f"'{safe_field}', LEFT(COALESCE(NEW.{safe_field}::text, ''), 100)")
            else:
                extractions.append(f"'{safe_field}', COALESCE(NEW.{safe_field}::text, '')")

        return ", ".join(extractions)
    
    def get_trigger_status_query(self, table_name: str, trigger_prefix: str = "rd_trigger_") -> str:
        """生成查询触发器状态的SQL"""
        trigger_name = f"{trigger_prefix}{table_name.replace('.', '_')}"
        
        sql = f"""
SELECT 
    t.trigger_name,
    t.event_manipulation,
    t.event_object_schema,
    t.event_object_table,
    t.action_timing,
    t.action_statement,
    CASE 
        WHEN t.trigger_name IS NOT NULL THEN 'EXISTS'
        ELSE 'NOT_EXISTS'
    END as status
FROM information_schema.triggers t
WHERE t.trigger_name = '{trigger_name}'
   OR t.trigger_name LIKE '{trigger_prefix}%'
ORDER BY t.event_object_schema, t.event_object_table;
"""
        return sql.strip()
    
    def get_all_triggers_query(self, trigger_prefix: str = "rd_trigger_") -> str:
        """生成查询所有资源发现触发器的SQL"""
        sql = f"""
SELECT 
    t.trigger_name,
    t.event_manipulation,
    t.event_object_schema || '.' || t.event_object_table as full_table_name,
    t.action_timing,
    t.action_statement,
    'EXISTS' as status
FROM information_schema.triggers t
WHERE t.trigger_name LIKE '{trigger_prefix}%'
ORDER BY t.event_object_schema, t.event_object_table;
"""
        return sql.strip()
    
    def validate_trigger_setup(self, config: TriggerConfig) -> List[str]:
        """验证触发器配置"""
        errors = []
        
        # 验证表名
        if not config.table_name:
            errors.append("表名不能为空")
        
        # 验证字段
        if not config.fields:
            errors.append("字段列表不能为空")
        
        # 验证操作类型
        valid_operations = {"INSERT", "UPDATE", "DELETE"}
        for op in config.operations:
            if op.upper() not in valid_operations:
                errors.append(f"无效的操作类型: {op}")
        
        # 验证前缀
        if not config.trigger_prefix:
            errors.append("触发器前缀不能为空")
        
        if not config.notify_channel_prefix:
            errors.append("通知通道前缀不能为空")
        
        return errors


def create_trigger_config_from_resource(resource_config, trigger_config) -> TriggerConfig:
    """从资源配置创建触发器配置"""
    return TriggerConfig(
        table_name=resource_config.table,
        fields=resource_config.fields,
        trigger_prefix=trigger_config.trigger_prefix,
        notify_channel_prefix=trigger_config.notify_channel_prefix,
        operations=["INSERT", "UPDATE", "DELETE"]
    )


# 使用示例
if __name__ == "__main__":
    # 创建生成器
    generator = TriggerSQLGenerator()
    
    # 创建配置
    config = TriggerConfig(
        table_name="api_tools.api_definitions",
        fields=["name", "description", "url"],
        trigger_prefix="rd_trigger_",
        notify_channel_prefix="rd_notify_"
    )
    
    # 生成SQL
    print("=== 触发器函数 ===")
    print(generator.generate_trigger_function(config))
    print("\n=== 创建触发器 ===")
    print(generator.generate_trigger_creation(config))
    print("\n=== 状态查询 ===")
    print(generator.get_trigger_status_query(config.table_name))
