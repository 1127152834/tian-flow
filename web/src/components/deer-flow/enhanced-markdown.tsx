"use client";

import React from "react";
import { Markdown } from "./markdown";
import ChartRenderer from "~/components/ui/chart-renderer";
import { cn } from "~/lib/utils";

interface EnhancedMarkdownProps {
  className?: string;
  children?: string | null;
  style?: React.CSSProperties;
  enableCopy?: boolean;
  animated?: boolean;
  checkLinkCredibility?: boolean;
}

// 检测文本中是否包含图表配置
function detectChartConfig(text: string): { hasChart: boolean; chartConfigs: string[]; textParts: string[] } {
  const chartConfigs: string[] = [];
  const textParts: string[] = [];

  // 匹配 chart 代码块中的图表配置（优先级更高）
  const chartBlockRegex = /```chart\s*\n([\s\S]*?)\n```/g;
  // 匹配 JSON 代码块中的图表配置
  const jsonBlockRegex = /```json\s*\n([\s\S]*?)\n```/g;

  let lastIndex = 0;
  let match;

  // 首先处理 chart 代码块
  while ((match = chartBlockRegex.exec(text)) !== null) {
    const jsonContent = match[1].trim();

    try {
      const parsed = JSON.parse(jsonContent);
      // chart 代码块中的内容直接认为是图表配置
      textParts.push(text.slice(lastIndex, match.index));
      chartConfigs.push(jsonContent);
      lastIndex = match.index + match[0].length;
    } catch (e) {
      // 不是有效的 JSON，忽略
    }
  }

  // 如果没有找到 chart 代码块，再检查 json 代码块
  if (chartConfigs.length === 0) {
    lastIndex = 0;
    while ((match = jsonBlockRegex.exec(text)) !== null) {
      const jsonContent = match[1].trim();

      try {
        const parsed = JSON.parse(jsonContent);
        // 检查是否是图表配置
        if (parsed.type && ['LineChart', 'BarChart', 'AreaChart', 'PieChart', 'ScatterChart', 'ComposedChart'].includes(parsed.type)) {
          // 添加前面的文本
          textParts.push(text.slice(lastIndex, match.index));
          chartConfigs.push(jsonContent);
          lastIndex = match.index + match[0].length;
        }
      } catch (e) {
        // 不是有效的 JSON，忽略
      }
    }
  }

  // 添加剩余的文本
  textParts.push(text.slice(lastIndex));

  return {
    hasChart: chartConfigs.length > 0,
    chartConfigs,
    textParts
  };
}

// 检测纯 JSON 图表配置（不在代码块中）
function detectInlineChartConfig(text: string): { hasChart: boolean; config?: any } {
  try {
    // 尝试解析整个文本作为 JSON
    const parsed = JSON.parse(text.trim());
    if (parsed.type && ['LineChart', 'BarChart', 'AreaChart', 'PieChart', 'ScatterChart', 'ComposedChart'].includes(parsed.type)) {
      return { hasChart: true, config: parsed };
    }
  } catch (e) {
    // 不是有效的 JSON
  }
  
  return { hasChart: false };
}

export function EnhancedMarkdown({
  className,
  children,
  style,
  enableCopy,
  animated = false,
  checkLinkCredibility = false,
}: EnhancedMarkdownProps) {
  if (!children) {
    return null;
  }

  // 首先检查是否是纯图表配置
  const inlineChart = detectInlineChartConfig(children);
  if (inlineChart.hasChart) {
    return (
      <div className={cn(className)} style={style}>
        <ChartRenderer config={inlineChart.config!} />
      </div>
    );
  }

  // 检查文本中是否包含图表配置
  const { hasChart, chartConfigs, textParts } = detectChartConfig(children);
  
  if (!hasChart) {
    // 没有图表，使用普通的 Markdown 渲染
    return (
      <Markdown
        className={className}
        style={style}
        enableCopy={enableCopy}
        animated={animated}
        checkLinkCredibility={checkLinkCredibility}
      >
        {children}
      </Markdown>
    );
  }

  // 有图表，需要混合渲染
  return (
    <div className={cn(className)} style={style}>
      {textParts.map((textPart, index) => (
        <React.Fragment key={index}>
          {/* 渲染文本部分 */}
          {textPart.trim() && (
            <Markdown
              enableCopy={enableCopy}
              animated={animated}
              checkLinkCredibility={checkLinkCredibility}
            >
              {textPart}
            </Markdown>
          )}
          
          {/* 渲染图表（如果有） */}
          {index < chartConfigs.length && (
            <div className="my-6">
              <ChartRenderer config={chartConfigs[index]} />
            </div>
          )}
        </React.Fragment>
      ))}
    </div>
  );
}

export default EnhancedMarkdown;
