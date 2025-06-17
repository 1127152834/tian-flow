# Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
# SPDX-License-Identifier: MIT

"""
Result Processor
结果处理器 - 严格按照ti-flow实现
"""

import json
import xml.etree.ElementTree as ET
from typing import Any, Dict, Optional, Union
from pydantic import BaseModel

from src.models.api_tools import APIDefinition, ResponseConfig, ResponseType


class ProcessedResult(BaseModel):
    """处理后的结果"""
    
    success: bool
    status_code: Optional[int] = None
    headers: Dict[str, str] = {}
    raw_content: Optional[str] = None
    parsed_data: Optional[Any] = None
    extracted_data: Optional[Any] = None
    error_message: Optional[str] = None
    execution_time_ms: Optional[int] = None


class ResultProcessor:
    """结果处理器"""
    
    def __init__(self):
        pass
    
    def process_response(
        self,
        api_def: APIDefinition,
        status_code: int,
        headers: Dict[str, str],
        content: Union[str, bytes],
        execution_time_ms: int
    ) -> ProcessedResult:
        """
        处理API响应
        
        Args:
            api_def: API定义
            status_code: HTTP状态码
            headers: 响应头
            content: 响应内容
            execution_time_ms: 执行时间（毫秒）
            
        Returns:
            ProcessedResult: 处理后的结果
        """
        result = ProcessedResult(
            success=False,
            status_code=status_code,
            headers=headers,
            execution_time_ms=execution_time_ms
        )
        
        try:
            # 转换内容为字符串
            if isinstance(content, bytes):
                # 尝试从响应头获取编码
                encoding = self._get_encoding_from_headers(headers)
                try:
                    content_str = content.decode(encoding)
                except UnicodeDecodeError:
                    # 如果解码失败，尝试其他编码
                    for fallback_encoding in ['utf-8', 'latin-1', 'gbk']:
                        try:
                            content_str = content.decode(fallback_encoding)
                            break
                        except UnicodeDecodeError:
                            continue
                    else:
                        content_str = content.decode('utf-8', errors='ignore')
            else:
                content_str = str(content)
            
            result.raw_content = content_str
            
            # 解析响应内容
            parsed_data = self._parse_content(content_str, api_def.response_config)
            result.parsed_data = parsed_data
            
            # 提取数据
            if isinstance(api_def.response_config, ResponseConfig):
                extracted_data = self._extract_data(parsed_data, api_def.response_config)
                result.extracted_data = extracted_data
                
                # 判断是否成功
                result.success = api_def.response_config.is_success_response(parsed_data, status_code)
                
                # 提取错误信息
                if not result.success:
                    error_msg = api_def.response_config.extract_message(parsed_data)
                    if error_msg:
                        result.error_message = error_msg
                    elif status_code >= 400:
                        result.error_message = f"HTTP {status_code} 错误"
            else:
                # 如果没有响应配置，基于状态码判断成功
                result.success = 200 <= status_code < 300
                result.extracted_data = parsed_data
                
                if not result.success:
                    result.error_message = f"HTTP {status_code} 错误"
        
        except Exception as e:
            result.success = False
            result.error_message = f"响应处理失败: {str(e)}"
        
        return result
    
    def process_exception(self, exception: Exception, execution_time_ms: int) -> ProcessedResult:
        """
        处理异常
        
        Args:
            exception: 异常对象
            execution_time_ms: 执行时间（毫秒）
            
        Returns:
            ProcessedResult: 处理后的结果
        """
        return ProcessedResult(
            success=False,
            error_message=str(exception),
            execution_time_ms=execution_time_ms
        )
    
    def _get_encoding_from_headers(self, headers: Dict[str, str]) -> str:
        """从响应头获取编码"""
        content_type = headers.get('content-type', '').lower()
        
        # 查找charset参数
        if 'charset=' in content_type:
            try:
                charset_part = content_type.split('charset=')[1]
                encoding = charset_part.split(';')[0].strip()
                return encoding
            except (IndexError, AttributeError):
                pass
        
        # 默认编码
        return 'utf-8'
    
    def _parse_content(self, content: str, response_config: ResponseConfig) -> Any:
        """解析响应内容"""
        if not content.strip():
            return None
        
        try:
            if isinstance(response_config, ResponseConfig):
                if response_config.response_type == ResponseType.JSON:
                    return json.loads(content)
                elif response_config.response_type == ResponseType.XML:
                    return self._parse_xml(content)
                elif response_config.response_type == ResponseType.TEXT:
                    return content
                elif response_config.response_type == ResponseType.HTML:
                    return content
                else:
                    # 默认尝试JSON解析
                    try:
                        return json.loads(content)
                    except json.JSONDecodeError:
                        return content
            else:
                # 没有响应配置，尝试自动检测
                return self._auto_parse_content(content)
        
        except Exception as e:
            # 解析失败，返回原始内容
            return content
    
    def _auto_parse_content(self, content: str) -> Any:
        """自动解析内容"""
        content = content.strip()
        
        # 尝试JSON
        if content.startswith(('{', '[')):
            try:
                return json.loads(content)
            except json.JSONDecodeError:
                pass
        
        # 尝试XML
        if content.startswith('<'):
            try:
                return self._parse_xml(content)
            except ET.ParseError:
                pass
        
        # 返回原始文本
        return content
    
    def _parse_xml(self, content: str) -> Dict[str, Any]:
        """解析XML内容"""
        try:
            root = ET.fromstring(content)
            return self._xml_to_dict(root)
        except ET.ParseError as e:
            raise ValueError(f"XML解析失败: {str(e)}")
    
    def _xml_to_dict(self, element: ET.Element) -> Dict[str, Any]:
        """将XML元素转换为字典"""
        result = {}
        
        # 添加属性
        if element.attrib:
            result['@attributes'] = element.attrib
        
        # 处理子元素
        children = list(element)
        if children:
            child_dict = {}
            for child in children:
                child_data = self._xml_to_dict(child)
                if child.tag in child_dict:
                    # 如果已存在同名标签，转换为列表
                    if not isinstance(child_dict[child.tag], list):
                        child_dict[child.tag] = [child_dict[child.tag]]
                    child_dict[child.tag].append(child_data)
                else:
                    child_dict[child.tag] = child_data
            result.update(child_dict)
        
        # 添加文本内容
        if element.text and element.text.strip():
            if result:
                result['#text'] = element.text.strip()
            else:
                return element.text.strip()
        
        return result
    
    def _extract_data(self, parsed_data: Any, response_config: ResponseConfig) -> Any:
        """根据响应配置提取数据"""
        if not parsed_data or not isinstance(response_config, ResponseConfig):
            return parsed_data
        
        try:
            # 提取主要数据
            extracted_data = response_config.extract_primary_data(parsed_data)
            
            # 如果没有配置主数据字段，返回解析后的数据
            if extracted_data is None:
                return parsed_data
            
            return extracted_data
        
        except Exception:
            # 提取失败，返回原始解析数据
            return parsed_data
    
    def format_result_for_display(self, result: ProcessedResult) -> Dict[str, Any]:
        """格式化结果用于显示"""
        display_result = {
            "success": result.success,
            "status_code": result.status_code,
            "execution_time_ms": result.execution_time_ms,
        }
        
        if result.success:
            display_result["data"] = result.extracted_data or result.parsed_data
        else:
            display_result["error"] = result.error_message
        
        # 添加原始响应（用于调试）
        if result.raw_content:
            display_result["raw_response"] = result.raw_content[:1000]  # 限制长度
        
        return display_result
