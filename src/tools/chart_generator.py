"""
图表生成工具

生成 Recharts 兼容的 JSON 配置，支持多种图表类型：
- 折线图 (LineChart)
- 柱状图 (BarChart)
- 面积图 (AreaChart)
- 饼图 (PieChart)
- 散点图 (ScatterChart)
- 组合图 (ComposedChart)
"""

import json
import logging
from typing import Dict, List, Any, Optional, Literal
import pandas as pd
from langchain_core.tools import tool
from src.services.websocket.progress_manager import progress_ws_manager

logger = logging.getLogger(__name__)

ChartType = Literal[
    "LineChart", "BarChart", "AreaChart", "PieChart",
    "ScatterChart", "ComposedChart"
]

# WebSocket 连接管理
active_connections = set()

async def send_chart_to_frontend(chart_config: Dict[str, Any], thread_id: str = None):
    """通过 WebSocket 发送图表配置到前端"""
    if not active_connections:
        logger.warning("没有活跃的 WebSocket 连接，无法发送图表")
        return False

    message = {
        "type": "chart",
        "data": {
            "chart_config": chart_config,
            "thread_id": thread_id,
            "timestamp": pd.Timestamp.now().isoformat()
        }
    }

    # 发送到所有活跃连接
    disconnected = set()
    for websocket in active_connections:
        try:
            await websocket.send(json.dumps(message))
            logger.info(f"图表配置已发送到前端: {chart_config.get('title', 'Unknown')}")
        except Exception as e:
            logger.error(f"发送图表配置失败: {e}")
            disconnected.add(websocket)

    # 清理断开的连接
    active_connections -= disconnected
    return len(active_connections) > 0

@tool
def generate_chart(
    data: str,
    chart_type: ChartType,
    title: str = "Chart",
    x_column: Optional[str] = None,
    y_column: Optional[str] = None,
    color_column: Optional[str] = None,
    width: int = 800,
    height: int = 400
) -> str:
    """
    生成 Recharts 兼容的图表配置 JSON

    Args:
        data: JSON格式的数据字符串，或CSV格式的数据
        chart_type: 图表类型 (LineChart, BarChart, AreaChart, PieChart, ScatterChart, ComposedChart)
        title: 图表标题
        x_column: X轴列名
        y_column: Y轴列名
        color_column: 颜色分组列名
        width: 图表宽度
        height: 图表高度

    Returns:
        Recharts 配置的 JSON 字符串
    """
    try:
        # 解析数据
        df = _parse_data(data)
        if df is None or df.empty:
            return json.dumps({"error": "无法解析数据或数据为空"})

        logger.info(f"生成图表配置: {chart_type}, 数据形状: {df.shape}")

        # 生成 Recharts 配置
        chart_config = _generate_recharts_config(
            df, chart_type, title, x_column, y_column, color_column, width, height
        )

        # 通过 WebSocket 推送图表配置到前端
        try:
            # 使用新的图表推送方法
            import asyncio
            asyncio.create_task(progress_ws_manager.send_chart_data(chart_config))

            logger.info(f"图表配置已通过WebSocket推送: {chart_config.get('title', 'Unknown')}")

            # 只返回简单的成功消息给智能体
            return f"✅ 图表生成成功！已生成包含 {len(chart_config.get('data', []))} 个数据点的{chart_config.get('title', '数据图表')}，图表已推送到前端显示。"

        except Exception as e:
            logger.error(f"WebSocket推送图表失败: {e}")
            # 如果WebSocket推送失败，回退到原来的方式
            chart_json = json.dumps(chart_config, ensure_ascii=False, indent=2)
            return f"""📊 **图表已生成**（WebSocket推送失败，使用备用方式）

```chart
{chart_json}
```

图表配置已生成完成，包含 {len(chart_config.get('data', []))} 个数据点。"""

    except Exception as e:
        logger.error(f"生成图表配置时出错: {str(e)}")
        return json.dumps({"error": f"生成图表配置时出错: {str(e)}"}, ensure_ascii=False)


def _parse_data(data: str) -> Optional[pd.DataFrame]:
    """解析输入数据"""
    try:
        import io
        # 尝试解析JSON
        if data.strip().startswith('[') or data.strip().startswith('{'):
            json_data = json.loads(data)
            if isinstance(json_data, list):
                return pd.DataFrame(json_data)
            elif isinstance(json_data, dict):
                return pd.DataFrame([json_data])

        # 尝试解析CSV
        return pd.read_csv(io.StringIO(data))

    except Exception as e:
        logger.error(f"解析数据时出错: {str(e)}")
        return None


def _generate_recharts_config(
    df: pd.DataFrame,
    chart_type: ChartType,
    title: str,
    x_column: Optional[str],
    y_column: Optional[str],
    color_column: Optional[str],
    width: int,
    height: int
) -> Dict[str, Any]:
    """生成 Recharts 配置"""

    # 自动选择列名
    if not x_column and len(df.columns) > 0:
        # 优先选择非数值列作为X轴
        non_numeric_cols = df.select_dtypes(exclude=['number']).columns
        if len(non_numeric_cols) > 0:
            x_column = non_numeric_cols[0]
        else:
            x_column = df.columns[0]

    if not y_column and len(df.columns) > 1:
        # 优先选择数值列作为Y轴
        numeric_cols = df.select_dtypes(include=['number']).columns
        if len(numeric_cols) > 0:
            y_column = numeric_cols[0]
        else:
            y_column = df.columns[1]

    # 转换数据为字典列表
    data_list = df.to_dict('records')

    # 基础配置
    config = {
        "type": chart_type,
        "title": title,
        "width": width,
        "height": height,
        "data": data_list,
        "margin": {"top": 20, "right": 30, "left": 20, "bottom": 5}
    }

    # 根据图表类型生成特定配置
    if chart_type == "LineChart":
        config.update(_get_line_chart_config(x_column, y_column, color_column))
    elif chart_type == "BarChart":
        config.update(_get_bar_chart_config(x_column, y_column, color_column))
    elif chart_type == "AreaChart":
        config.update(_get_area_chart_config(x_column, y_column, color_column))
    elif chart_type == "PieChart":
        config.update(_get_pie_chart_config(df, x_column, y_column))
    elif chart_type == "ScatterChart":
        config.update(_get_scatter_chart_config(x_column, y_column, color_column))
    elif chart_type == "ComposedChart":
        config.update(_get_composed_chart_config(x_column, y_column, color_column))

    return config


def _get_line_chart_config(x_column: str, y_column: str, color_column: Optional[str]) -> Dict[str, Any]:
    """生成折线图配置"""
    config = {
        "xAxis": {"dataKey": x_column, "type": "category"},
        "yAxis": {"type": "number"},
        "lines": [
            {
                "type": "monotone",
                "dataKey": y_column,
                "stroke": "#8884d8",
                "strokeWidth": 2,
                "dot": {"fill": "#8884d8", "strokeWidth": 2, "r": 4}
            }
        ],
        "tooltip": {"active": True},
        "legend": {"verticalAlign": "top", "height": 36}
    }

    if color_column:
        # 如果有颜色分组，需要处理多条线
        config["lines"][0]["stroke"] = "#8884d8"

    return config


def _get_bar_chart_config(x_column: str, y_column: str, color_column: Optional[str]) -> Dict[str, Any]:
    """生成柱状图配置"""
    config = {
        "xAxis": {"dataKey": x_column, "type": "category"},
        "yAxis": {"type": "number"},
        "bars": [
            {
                "dataKey": y_column,
                "fill": "#8884d8"
            }
        ],
        "tooltip": {"active": True},
        "legend": {"verticalAlign": "top", "height": 36}
    }

    if color_column:
        config["bars"][0]["fill"] = "#82ca9d"

    return config


def _get_area_chart_config(x_column: str, y_column: str, color_column: Optional[str]) -> Dict[str, Any]:
    """生成面积图配置"""
    config = {
        "xAxis": {"dataKey": x_column, "type": "category"},
        "yAxis": {"type": "number"},
        "areas": [
            {
                "type": "monotone",
                "dataKey": y_column,
                "stroke": "#8884d8",
                "fill": "#8884d8",
                "fillOpacity": 0.6
            }
        ],
        "tooltip": {"active": True},
        "legend": {"verticalAlign": "top", "height": 36}
    }

    return config


def _get_pie_chart_config(df: pd.DataFrame, x_column: str, y_column: str) -> Dict[str, Any]:
    """生成饼图配置"""
    # 饼图需要特殊的数据格式
    values_col = y_column or df.select_dtypes(include=['number']).columns[0]
    names_col = x_column or df.select_dtypes(include=['object']).columns[0]

    config = {
        "pie": {
            "dataKey": values_col,
            "nameKey": names_col,
            "cx": "50%",
            "cy": "50%",
            "outerRadius": 80,
            "fill": "#8884d8",
            "label": True
        },
        "tooltip": {"active": True},
        "legend": {"verticalAlign": "bottom", "height": 36}
    }

    return config


def _get_scatter_chart_config(x_column: str, y_column: str, color_column: Optional[str]) -> Dict[str, Any]:
    """生成散点图配置"""
    config = {
        "xAxis": {"dataKey": x_column, "type": "number", "name": x_column},
        "yAxis": {"dataKey": y_column, "type": "number", "name": y_column},
        "scatter": {
            "dataKey": y_column,
            "fill": "#8884d8"
        },
        "tooltip": {"active": True},
        "legend": {"verticalAlign": "top", "height": 36}
    }

    return config


def _get_composed_chart_config(x_column: str, y_column: str, color_column: Optional[str]) -> Dict[str, Any]:
    """生成组合图配置"""
    config = {
        "xAxis": {"dataKey": x_column, "type": "category"},
        "yAxis": {"type": "number"},
        "bars": [
            {
                "dataKey": y_column,
                "fill": "#8884d8"
            }
        ],
        "lines": [
            {
                "type": "monotone",
                "dataKey": y_column,
                "stroke": "#ff7300"
            }
        ],
        "tooltip": {"active": True},
        "legend": {"verticalAlign": "top", "height": 36}
    }

    return config



