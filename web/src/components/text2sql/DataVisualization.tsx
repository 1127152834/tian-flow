// Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
// SPDX-License-Identifier: MIT

"use client";

import React, { useState, useMemo } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "~/components/ui/card";
import { Button } from "~/components/ui/button";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "~/components/ui/select";
import { Badge } from "~/components/ui/badge";
import { Separator } from "~/components/ui/separator";
import { 
  BarChart3, 
  PieChart, 
  LineChart, 
  Table as TableIcon,
  Download,
  Eye,
  TrendingUp,
  Hash
} from "lucide-react";

interface DataVisualizationProps {
  data: Array<Record<string, any>>;
  sql: string;
  onExport?: (format: 'csv' | 'json' | 'excel') => void;
}

type ChartType = 'table' | 'bar' | 'pie' | 'line' | 'summary';

const DataVisualization: React.FC<DataVisualizationProps> = ({
  data,
  sql,
  onExport
}) => {
  const [chartType, setChartType] = useState<ChartType>('table');
  const [selectedColumns, setSelectedColumns] = useState<string[]>([]);

  // Analyze data structure
  const dataAnalysis = useMemo(() => {
    if (!data || data.length === 0) {
      return { columns: [], numericColumns: [], textColumns: [], rowCount: 0 };
    }

    const firstRow = data[0];
    const columns = Object.keys(firstRow);
    const numericColumns: string[] = [];
    const textColumns: string[] = [];

    columns.forEach(col => {
      const sampleValues = data.slice(0, 10).map(row => row[col]);
      const numericValues = sampleValues.filter(val => 
        typeof val === 'number' || (!isNaN(Number(val)) && val !== null && val !== '')
      );
      
      if (numericValues.length > sampleValues.length * 0.7) {
        numericColumns.push(col);
      } else {
        textColumns.push(col);
      }
    });

    return {
      columns,
      numericColumns,
      textColumns,
      rowCount: data.length
    };
  }, [data]);

  // Generate summary statistics
  const summaryStats = useMemo(() => {
    if (!data || data.length === 0) return {};

    const stats: Record<string, any> = {};
    
    dataAnalysis.numericColumns.forEach(col => {
      const values = data.map(row => Number(row[col])).filter(val => !isNaN(val));
      if (values.length > 0) {
        stats[col] = {
          count: values.length,
          sum: values.reduce((a, b) => a + b, 0),
          avg: values.reduce((a, b) => a + b, 0) / values.length,
          min: Math.min(...values),
          max: Math.max(...values)
        };
      }
    });

    dataAnalysis.textColumns.forEach(col => {
      const values = data.map(row => row[col]).filter(val => val !== null && val !== '');
      const uniqueValues = new Set(values);
      stats[col] = {
        count: values.length,
        unique: uniqueValues.size,
        mostCommon: values.length > 0 ? values[0] : null // Simplified
      };
    });

    return stats;
  }, [data, dataAnalysis]);

  const renderTable = () => (
    <div className="overflow-x-auto">
      <table className="w-full border-collapse border border-gray-300">
        <thead>
          <tr className="bg-gray-50">
            {dataAnalysis.columns.map(col => (
              <th key={col} className="border border-gray-300 px-4 py-2 text-left font-medium">
                {col}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {data.slice(0, 100).map((row, idx) => (
            <tr key={idx} className={idx % 2 === 0 ? "bg-white" : "bg-gray-50"}>
              {dataAnalysis.columns.map(col => (
                <td key={col} className="border border-gray-300 px-4 py-2">
                  {row[col]?.toString() || ''}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
      {data.length > 100 && (
        <div className="mt-4 text-sm text-gray-600 text-center">
          Showing first 100 rows of {data.length} total rows
        </div>
      )}
    </div>
  );

  const renderSummary = () => (
    <div className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Total Rows</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{dataAnalysis.rowCount}</div>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Columns</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{dataAnalysis.columns.length}</div>
            <div className="text-xs text-gray-600">
              {dataAnalysis.numericColumns.length} numeric, {dataAnalysis.textColumns.length} text
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Data Types</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex flex-wrap gap-1">
              {dataAnalysis.numericColumns.length > 0 && (
                <Badge variant="secondary">
                  <Hash className="w-3 h-3 mr-1" />
                  Numbers
                </Badge>
              )}
              {dataAnalysis.textColumns.length > 0 && (
                <Badge variant="outline">Text</Badge>
              )}
            </div>
          </CardContent>
        </Card>
      </div>

      <div className="space-y-4">
        <h3 className="text-lg font-semibold">Column Statistics</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {Object.entries(summaryStats).map(([col, stats]) => (
            <Card key={col}>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-medium">{col}</CardTitle>
                <CardDescription>
                  {dataAnalysis.numericColumns.includes(col) ? 'Numeric' : 'Text'} column
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-1 text-sm">
                  <div>Count: {stats.count}</div>
                  {stats.avg !== undefined && (
                    <>
                      <div>Average: {stats.avg.toFixed(2)}</div>
                      <div>Min: {stats.min} | Max: {stats.max}</div>
                    </>
                  )}
                  {stats.unique !== undefined && (
                    <div>Unique values: {stats.unique}</div>
                  )}
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    </div>
  );

  const renderSimpleChart = () => (
    <div className="space-y-4">
      <div className="text-center text-gray-600">
        <BarChart3 className="w-16 h-16 mx-auto mb-4 text-gray-400" />
        <p>Advanced charting features coming soon!</p>
        <p className="text-sm">For now, use the table view to explore your data.</p>
      </div>
    </div>
  );

  if (!data || data.length === 0) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Eye className="w-5 h-5" />
            Data Visualization
          </CardTitle>
          <CardDescription>No data to visualize</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="text-center text-gray-500 py-8">
            Execute a query to see data visualization options
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <div>
            <CardTitle className="flex items-center gap-2">
              <TrendingUp className="w-5 h-5" />
              Data Visualization
            </CardTitle>
            <CardDescription>
              {dataAnalysis.rowCount} rows × {dataAnalysis.columns.length} columns
            </CardDescription>
          </div>
          
          <div className="flex items-center gap-2">
            <Select value={chartType} onValueChange={(value: ChartType) => setChartType(value)}>
              <SelectTrigger className="w-32">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="table">
                  <div className="flex items-center gap-2">
                    <TableIcon className="w-4 h-4" />
                    Table
                  </div>
                </SelectItem>
                <SelectItem value="summary">
                  <div className="flex items-center gap-2">
                    <Hash className="w-4 h-4" />
                    Summary
                  </div>
                </SelectItem>
                <SelectItem value="bar">
                  <div className="flex items-center gap-2">
                    <BarChart3 className="w-4 h-4" />
                    Bar Chart
                  </div>
                </SelectItem>
                <SelectItem value="pie">
                  <div className="flex items-center gap-2">
                    <PieChart className="w-4 h-4" />
                    Pie Chart
                  </div>
                </SelectItem>
                <SelectItem value="line">
                  <div className="flex items-center gap-2">
                    <LineChart className="w-4 h-4" />
                    Line Chart
                  </div>
                </SelectItem>
              </SelectContent>
            </Select>

            {onExport && (
              <Select onValueChange={(format: 'csv' | 'json' | 'excel') => onExport(format)}>
                <SelectTrigger className="w-32">
                  <SelectValue placeholder="Export" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="csv">
                    <div className="flex items-center gap-2">
                      <Download className="w-4 h-4" />
                      CSV
                    </div>
                  </SelectItem>
                  <SelectItem value="json">
                    <div className="flex items-center gap-2">
                      <Download className="w-4 h-4" />
                      JSON
                    </div>
                  </SelectItem>
                  <SelectItem value="excel">
                    <div className="flex items-center gap-2">
                      <Download className="w-4 h-4" />
                      Excel
                    </div>
                  </SelectItem>
                </SelectContent>
              </Select>
            )}
          </div>
        </div>
      </CardHeader>
      
      <CardContent>
        {chartType === 'table' && renderTable()}
        {chartType === 'summary' && renderSummary()}
        {(chartType === 'bar' || chartType === 'pie' || chartType === 'line') && renderSimpleChart()}
      </CardContent>
    </Card>
  );
};

export default DataVisualization;
