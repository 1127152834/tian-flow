#!/usr/bin/env python3
"""
测试图表生成功能 - Recharts 配置生成
"""

import json
from src.tools.chart_generator import generate_chart

def test_basic_chart_generation():
    """测试基本图表生成功能"""
    print("=== 测试 Recharts 配置生成功能 ===")

    # 测试数据
    test_data = [
        {"month": "January", "sales": 1000, "profit": 200},
        {"month": "February", "sales": 1200, "profit": 250},
        {"month": "March", "sales": 1100, "profit": 220},
        {"month": "April", "sales": 1300, "profit": 280},
        {"month": "May", "sales": 1500, "profit": 350},
        {"month": "June", "sales": 1400, "profit": 320}
    ]

    data_json = json.dumps(test_data)

    # 测试不同类型的图表
    chart_types = ["LineChart", "BarChart", "AreaChart", "PieChart"]
    
    for chart_type in chart_types:
        print(f"\n--- 测试 {chart_type} 配置 ---")
        try:
            result = generate_chart.invoke({
                "data": data_json,
                "chart_type": chart_type,
                "title": f"Sales Data - {chart_type} Chart",
                "x_column": "month",
                "y_column": "sales"
            })

            # 尝试解析JSON以验证格式
            try:
                config = json.loads(result)
                if "error" in config:
                    print(f"❌ {chart_type} 配置生成失败: {config['error']}")
                else:
                    print(f"✅ {chart_type} 配置生成成功")
                    print(f"   配置类型: {config.get('type', 'Unknown')}")
                    print(f"   数据条数: {len(config.get('data', []))}")

                    # 保存配置文件
                    with open(f"test_chart_{chart_type.lower()}_config.json", "w", encoding="utf-8") as f:
                        f.write(json.dumps(config, ensure_ascii=False, indent=2))
                    print(f"   配置已保存到: test_chart_{chart_type.lower()}_config.json")

            except json.JSONDecodeError:
                print(f"❌ {chart_type} 返回的不是有效的JSON: {result[:100]}...")

        except Exception as e:
            print(f"❌ {chart_type} 配置生成异常: {str(e)}")


def test_csv_data():
    """测试CSV格式数据"""
    print("\n=== 测试CSV格式数据 ===")

    csv_data = """name,age,salary
Alice,25,50000
Bob,30,60000
Charlie,35,70000
Diana,28,55000
Eve,32,65000"""

    try:
        result = generate_chart.invoke({
            "data": csv_data,
            "chart_type": "ScatterChart",
            "title": "Age vs Salary",
            "x_column": "age",
            "y_column": "salary"
        })

        try:
            config = json.loads(result)
            if "error" in config:
                print(f"❌ CSV数据配置生成失败: {config['error']}")
            else:
                print("✅ CSV数据配置生成成功")
                with open("test_chart_csv_config.json", "w", encoding="utf-8") as f:
                    f.write(json.dumps(config, ensure_ascii=False, indent=2))
                print("   配置已保存到: test_chart_csv_config.json")

        except json.JSONDecodeError:
            print(f"❌ CSV数据返回的不是有效的JSON: {result[:100]}...")

    except Exception as e:
        print(f"❌ CSV数据配置生成异常: {str(e)}")


def test_composed_chart():
    """测试组合图"""
    print("\n=== 测试组合图 ===")

    test_data = [
        {"category": "A", "value": 23, "line_value": 30},
        {"category": "B", "value": 45, "line_value": 40},
        {"category": "C", "value": 56, "line_value": 50},
        {"category": "D", "value": 78, "line_value": 60},
        {"category": "E", "value": 32, "line_value": 35}
    ]

    data_json = json.dumps(test_data)

    try:
        result = generate_chart.invoke({
            "data": data_json,
            "chart_type": "ComposedChart",
            "title": "Composed Chart",
            "x_column": "category",
            "y_column": "value"
        })

        try:
            config = json.loads(result)
            if "error" in config:
                print(f"❌ 组合图配置生成失败: {config['error']}")
            else:
                print("✅ 组合图配置生成成功")
                with open("test_chart_composed_config.json", "w", encoding="utf-8") as f:
                    f.write(json.dumps(config, ensure_ascii=False, indent=2))
                print("   配置已保存到: test_chart_composed_config.json")

        except json.JSONDecodeError:
            print(f"❌ 组合图返回的不是有效的JSON: {result[:100]}...")

    except Exception as e:
        print(f"❌ 组合图配置生成异常: {str(e)}")


if __name__ == "__main__":
    print("开始测试 Recharts 配置生成功能...")

    test_basic_chart_generation()
    test_csv_data()
    test_composed_chart()

    print("\n=== 测试完成 ===")
    print("请查看生成的 JSON 配置文件以验证图表配置")
