"use client";

import React from "react";
import ChartRenderer from "~/components/ui/chart-renderer";
import { Card, CardContent, CardHeader, CardTitle } from "~/components/ui/card";

const TestChartsPage = () => {
  // 测试数据
  const testData = [
    { month: "January", sales: 1000, profit: 200 },
    { month: "February", sales: 1200, profit: 250 },
    { month: "March", sales: 1100, profit: 220 },
    { month: "April", sales: 1300, profit: 280 },
    { month: "May", sales: 1500, profit: 350 },
    { month: "June", sales: 1400, profit: 320 }
  ];

  // 折线图配置
  const lineChartConfig = {
    type: "LineChart" as const,
    title: "Sales Trend - Line Chart",
    width: 800,
    height: 400,
    data: testData,
    margin: { top: 20, right: 30, left: 20, bottom: 5 },
    xAxis: { dataKey: "month", type: "category" },
    yAxis: { type: "number" },
    lines: [
      {
        type: "monotone",
        dataKey: "sales",
        stroke: "#8884d8",
        strokeWidth: 2,
        dot: { fill: "#8884d8", strokeWidth: 2, r: 4 }
      }
    ],
    tooltip: { active: true },
    legend: { verticalAlign: "top", height: 36 }
  };

  // 柱状图配置
  const barChartConfig = {
    type: "BarChart" as const,
    title: "Sales Data - Bar Chart",
    width: 800,
    height: 400,
    data: testData,
    margin: { top: 20, right: 30, left: 20, bottom: 5 },
    xAxis: { dataKey: "month", type: "category" },
    yAxis: { type: "number" },
    bars: [
      { dataKey: "sales", fill: "#8884d8" }
    ],
    tooltip: { active: true },
    legend: { verticalAlign: "top", height: 36 }
  };

  // 面积图配置
  const areaChartConfig = {
    type: "AreaChart" as const,
    title: "Sales Data - Area Chart",
    width: 800,
    height: 400,
    data: testData,
    margin: { top: 20, right: 30, left: 20, bottom: 5 },
    xAxis: { dataKey: "month", type: "category" },
    yAxis: { type: "number" },
    areas: [
      {
        type: "monotone",
        dataKey: "sales",
        stroke: "#8884d8",
        fill: "#8884d8",
        fillOpacity: 0.6
      }
    ],
    tooltip: { active: true },
    legend: { verticalAlign: "top", height: 36 }
  };

  // 饼图配置
  const pieChartConfig = {
    type: "PieChart" as const,
    title: "Sales Distribution - Pie Chart",
    width: 800,
    height: 400,
    data: testData,
    margin: { top: 20, right: 30, left: 20, bottom: 5 },
    pie: {
      dataKey: "sales",
      nameKey: "month",
      cx: "50%",
      cy: "50%",
      outerRadius: 80,
      fill: "#8884d8",
      label: true
    },
    tooltip: { active: true },
    legend: { verticalAlign: "bottom", height: 36 }
  };

  // 散点图数据
  const scatterData = [
    { age: 25, salary: 50000 },
    { age: 30, salary: 60000 },
    { age: 35, salary: 70000 },
    { age: 28, salary: 55000 },
    { age: 32, salary: 65000 }
  ];

  const scatterChartConfig = {
    type: "ScatterChart" as const,
    title: "Age vs Salary - Scatter Chart",
    width: 800,
    height: 400,
    data: scatterData,
    margin: { top: 20, right: 30, left: 20, bottom: 5 },
    xAxis: { dataKey: "age", type: "number", name: "Age" },
    yAxis: { dataKey: "salary", type: "number", name: "Salary" },
    scatter: {
      dataKey: "salary",
      fill: "#8884d8"
    },
    tooltip: { active: true },
    legend: { verticalAlign: "top", height: 36 }
  };

  // 组合图配置
  const composedChartConfig = {
    type: "ComposedChart" as const,
    title: "Sales & Profit - Composed Chart",
    width: 800,
    height: 400,
    data: testData,
    margin: { top: 20, right: 30, left: 20, bottom: 5 },
    xAxis: { dataKey: "month", type: "category" },
    yAxis: { type: "number" },
    bars: [
      { dataKey: "sales", fill: "#8884d8" }
    ],
    lines: [
      {
        type: "monotone",
        dataKey: "profit",
        stroke: "#ff7300",
        strokeWidth: 2
      }
    ],
    tooltip: { active: true },
    legend: { verticalAlign: "top", height: 36 }
  };

  return (
    <div className="container mx-auto p-6 space-y-8">
      <div className="text-center mb-8">
        <h1 className="text-3xl font-bold mb-2">图表渲染测试</h1>
        <p className="text-gray-600">测试 Recharts 图表渲染组件的各种图表类型</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle>折线图</CardTitle>
          </CardHeader>
          <CardContent>
            <ChartRenderer config={lineChartConfig} />
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>柱状图</CardTitle>
          </CardHeader>
          <CardContent>
            <ChartRenderer config={barChartConfig} />
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>面积图</CardTitle>
          </CardHeader>
          <CardContent>
            <ChartRenderer config={areaChartConfig} />
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>饼图</CardTitle>
          </CardHeader>
          <CardContent>
            <ChartRenderer config={pieChartConfig} />
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>散点图</CardTitle>
          </CardHeader>
          <CardContent>
            <ChartRenderer config={scatterChartConfig} />
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>组合图</CardTitle>
          </CardHeader>
          <CardContent>
            <ChartRenderer config={composedChartConfig} />
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>JSON 配置测试</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="mb-4 text-sm text-gray-600">
            测试从 JSON 字符串解析图表配置（模拟从后端接收的数据）
          </p>
          <ChartRenderer config={JSON.stringify(lineChartConfig)} />
        </CardContent>
      </Card>
    </div>
  );
};

export default TestChartsPage;
