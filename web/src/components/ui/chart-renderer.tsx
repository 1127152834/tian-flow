"use client";

import React from "react";
import {
  LineChart,
  Line,
  BarChart,
  Bar,
  AreaChart,
  Area,
  PieChart,
  Pie,
  Cell,
  ScatterChart,
  Scatter,
  ComposedChart,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from "recharts";

interface ChartConfig {
  type: "LineChart" | "BarChart" | "AreaChart" | "PieChart" | "ScatterChart" | "ComposedChart";
  title: string;
  width: number;
  height: number;
  data: Array<Record<string, any>>;
  margin?: {
    top: number;
    right: number;
    left: number;
    bottom: number;
  };
  xAxis?: {
    dataKey: string;
    type: string;
    name?: string;
  };
  yAxis?: {
    type: string;
    name?: string;
  };
  lines?: Array<{
    type: string;
    dataKey: string;
    stroke: string;
    strokeWidth?: number;
    dot?: {
      fill: string;
      strokeWidth: number;
      r: number;
    };
  }>;
  bars?: Array<{
    dataKey: string;
    fill: string;
  }>;
  areas?: Array<{
    type: string;
    dataKey: string;
    stroke: string;
    fill: string;
    fillOpacity?: number;
  }>;
  pie?: {
    dataKey: string;
    nameKey: string;
    cx: string;
    cy: string;
    outerRadius: number;
    fill: string;
    label: boolean;
  };
  scatter?: {
    dataKey: string;
    fill: string;
  };
  tooltip?: {
    active: boolean;
  };
  legend?: {
    verticalAlign: string;
    height: number;
  };
  error?: string;
}

interface ChartRendererProps {
  config: ChartConfig | string;
  className?: string;
}

// 预定义的颜色方案
const COLORS = [
  "#8884d8",
  "#82ca9d", 
  "#ffc658",
  "#ff7300",
  "#00ff00",
  "#0088fe",
  "#00c49f",
  "#ffbb28",
  "#ff8042",
  "#8dd1e1"
];

const ChartRenderer: React.FC<ChartRendererProps> = ({ config, className = "" }) => {
  // 解析配置
  let chartConfig: ChartConfig;
  
  if (typeof config === "string") {
    try {
      chartConfig = JSON.parse(config);
    } catch (error) {
      return (
        <div className={`p-4 border border-red-200 rounded-lg bg-red-50 ${className}`}>
          <p className="text-red-600">图表配置解析错误: {error instanceof Error ? error.message : "未知错误"}</p>
        </div>
      );
    }
  } else {
    chartConfig = config;
  }

  // 检查错误
  if (chartConfig.error) {
    return (
      <div className={`p-4 border border-red-200 rounded-lg bg-red-50 ${className}`}>
        <p className="text-red-600">图表生成错误: {chartConfig.error}</p>
      </div>
    );
  }

  // 检查数据
  if (!chartConfig.data || chartConfig.data.length === 0) {
    return (
      <div className={`p-4 border border-gray-200 rounded-lg bg-gray-50 ${className}`}>
        <p className="text-gray-600">没有数据可显示</p>
      </div>
    );
  }

  const renderChart = () => {
    const commonProps = {
      width: chartConfig.width,
      height: chartConfig.height,
      data: chartConfig.data,
      margin: chartConfig.margin || { top: 20, right: 30, left: 20, bottom: 5 },
    };

    switch (chartConfig.type) {
      case "LineChart":
        return (
          <LineChart {...commonProps}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis 
              dataKey={chartConfig.xAxis?.dataKey} 
              type={chartConfig.xAxis?.type as any}
              name={chartConfig.xAxis?.name}
            />
            <YAxis 
              type={chartConfig.yAxis?.type as any}
              name={chartConfig.yAxis?.name}
            />
            {chartConfig.tooltip?.active && <Tooltip />}
            {chartConfig.legend && <Legend {...chartConfig.legend} />}
            {chartConfig.lines?.map((line, index) => (
              <Line
                key={index}
                type={line.type as any}
                dataKey={line.dataKey}
                stroke={line.stroke}
                strokeWidth={line.strokeWidth}
                dot={line.dot}
              />
            ))}
          </LineChart>
        );

      case "BarChart":
        return (
          <BarChart {...commonProps}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis 
              dataKey={chartConfig.xAxis?.dataKey} 
              type={chartConfig.xAxis?.type as any}
            />
            <YAxis type={chartConfig.yAxis?.type as any} />
            {chartConfig.tooltip?.active && <Tooltip />}
            {chartConfig.legend && <Legend {...chartConfig.legend} />}
            {chartConfig.bars?.map((bar, index) => (
              <Bar
                key={index}
                dataKey={bar.dataKey}
                fill={bar.fill}
              />
            ))}
          </BarChart>
        );

      case "AreaChart":
        return (
          <AreaChart {...commonProps}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis 
              dataKey={chartConfig.xAxis?.dataKey} 
              type={chartConfig.xAxis?.type as any}
            />
            <YAxis type={chartConfig.yAxis?.type as any} />
            {chartConfig.tooltip?.active && <Tooltip />}
            {chartConfig.legend && <Legend {...chartConfig.legend} />}
            {chartConfig.areas?.map((area, index) => (
              <Area
                key={index}
                type={area.type as any}
                dataKey={area.dataKey}
                stroke={area.stroke}
                fill={area.fill}
                fillOpacity={area.fillOpacity}
              />
            ))}
          </AreaChart>
        );

      case "PieChart":
        return (
          <PieChart {...commonProps}>
            {chartConfig.tooltip?.active && <Tooltip />}
            {chartConfig.legend && <Legend {...chartConfig.legend} />}
            {chartConfig.pie && (
              <Pie
                data={chartConfig.data}
                dataKey={chartConfig.pie.dataKey}
                nameKey={chartConfig.pie.nameKey}
                cx={chartConfig.pie.cx}
                cy={chartConfig.pie.cy}
                outerRadius={chartConfig.pie.outerRadius}
                fill={chartConfig.pie.fill}
                label={chartConfig.pie.label}
              >
                {chartConfig.data.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                ))}
              </Pie>
            )}
          </PieChart>
        );

      case "ScatterChart":
        return (
          <ScatterChart {...commonProps}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis 
              dataKey={chartConfig.xAxis?.dataKey} 
              type={chartConfig.xAxis?.type as any}
              name={chartConfig.xAxis?.name}
            />
            <YAxis 
              dataKey={chartConfig.yAxis?.dataKey}
              type={chartConfig.yAxis?.type as any}
              name={chartConfig.yAxis?.name}
            />
            {chartConfig.tooltip?.active && <Tooltip />}
            {chartConfig.legend && <Legend {...chartConfig.legend} />}
            {chartConfig.scatter && (
              <Scatter
                dataKey={chartConfig.scatter.dataKey}
                fill={chartConfig.scatter.fill}
              />
            )}
          </ScatterChart>
        );

      case "ComposedChart":
        return (
          <ComposedChart {...commonProps}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis 
              dataKey={chartConfig.xAxis?.dataKey} 
              type={chartConfig.xAxis?.type as any}
            />
            <YAxis type={chartConfig.yAxis?.type as any} />
            {chartConfig.tooltip?.active && <Tooltip />}
            {chartConfig.legend && <Legend {...chartConfig.legend} />}
            {chartConfig.bars?.map((bar, index) => (
              <Bar
                key={`bar-${index}`}
                dataKey={bar.dataKey}
                fill={bar.fill}
              />
            ))}
            {chartConfig.lines?.map((line, index) => (
              <Line
                key={`line-${index}`}
                type={line.type as any}
                dataKey={line.dataKey}
                stroke={line.stroke}
                strokeWidth={line.strokeWidth}
              />
            ))}
          </ComposedChart>
        );

      default:
        return (
          <div className="p-4 border border-yellow-200 rounded-lg bg-yellow-50">
            <p className="text-yellow-600">不支持的图表类型: {chartConfig.type}</p>
          </div>
        );
    }
  };

  return (
    <div className={`w-full ${className}`}>
      {chartConfig.title && (
        <h3 className="text-lg font-semibold mb-4 text-center">{chartConfig.title}</h3>
      )}
      <ResponsiveContainer width="100%" height={chartConfig.height || 400}>
        {renderChart()}
      </ResponsiveContainer>
    </div>
  );
};

export default ChartRenderer;
