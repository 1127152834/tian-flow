"use client";

import { useState, useRef } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "~/components/ui/card";
import { Button } from "~/components/ui/button";
import { Textarea } from "~/components/ui/textarea";
import { Badge } from "~/components/ui/badge";
import { Alert, AlertDescription } from "~/components/ui/alert";
import { Separator } from "~/components/ui/separator";
import { ScrollArea } from "~/components/ui/scroll-area";
import { 
  MessageSquare, 
  Play, 
  Copy, 
  Download, 
  Loader2, 
  CheckCircle, 
  XCircle, 
  Clock,
  Lightbulb,
  Database,
  Code
} from "lucide-react";
import { text2sqlApi, type SQLGenerationResponse, type SQLExecutionResponse, type QuestionAnswerRequest, type QuestionAnswerResponse } from "~/core/api/text2sql";
import DataVisualization from "./DataVisualization";

interface SQLQueryInterfaceProps {
  datasourceId: number;
  datasourceName: string;
}

export default function SQLQueryInterface({ datasourceId, datasourceName }: SQLQueryInterfaceProps) {
  const [question, setQuestion] = useState("");
  const [generatedSQL, setGeneratedSQL] = useState<SQLGenerationResponse | null>(null);
  const [executionResult, setExecutionResult] = useState<SQLExecutionResponse | null>(null);
  const [isGenerating, setIsGenerating] = useState(false);
  const [isExecuting, setIsExecuting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [includeExplanation, setIncludeExplanation] = useState(true);
  const [mode, setMode] = useState<'generate' | 'answer'>('answer');
  const [formattedAnswer, setFormattedAnswer] = useState<string>("");
  const [autoExecute, setAutoExecute] = useState(true);

  const questionRef = useRef<HTMLTextAreaElement>(null);

  const handleGenerateSQL = async () => {
    if (!question.trim()) return;

    try {
      setIsGenerating(true);
      setError(null);
      setExecutionResult(null);
      setFormattedAnswer("");

      if (mode === 'answer') {
        // Use question-answer mode
        const response = await text2sqlApi.answerQuestion({
          question: question.trim(),
          datasource_id: datasourceId,
          execute_sql: autoExecute,
          format_result: true,
          include_explanation: includeExplanation,
        });

        // Create a compatible SQLGenerationResponse object
        setGeneratedSQL({
          query_id: 0, // Will be set if execution happens
          question: response.question,
          generated_sql: response.generated_sql,
          explanation: response.explanation,
          confidence_score: response.confidence_score,
          similar_examples: [],
          generation_time_ms: response.generation_time_ms
        });

        if (response.execution_result) {
          setExecutionResult(response.execution_result);
        }

        if (response.formatted_answer) {
          setFormattedAnswer(response.formatted_answer);
        }
      } else {
        // Use traditional generate mode
        const response = await text2sqlApi.generateSQL({
          datasource_id: datasourceId,
          question: question.trim(),
          include_explanation: includeExplanation,
        });

        setGeneratedSQL(response);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to generate SQL');
    } finally {
      setIsGenerating(false);
    }
  };

  const handleExecuteSQL = async () => {
    if (!generatedSQL) return;

    try {
      setIsExecuting(true);
      setError(null);

      const response = await text2sqlApi.executeSQL({
        query_id: generatedSQL.query_id,
        limit: 100,
      });

      setExecutionResult(response);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to execute SQL');
    } finally {
      setIsExecuting(false);
    }
  };

  const handleCopySQL = () => {
    if (generatedSQL) {
      navigator.clipboard.writeText(generatedSQL.generated_sql);
    }
  };

  const handleDownloadResults = () => {
    if (!executionResult?.result_data) return;

    const csv = convertToCSV(executionResult.result_data);
    const blob = new Blob([csv], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `query_results_${new Date().toISOString().split('T')[0]}.csv`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  const convertToCSV = (data: Array<Record<string, any>>): string => {
    if (data.length === 0) return '';

    const firstRow = data[0];
    if (!firstRow) return '';
    const headers = Object.keys(firstRow);
    const csvHeaders = headers.join(',');
    const csvRows = data.map(row => 
      headers.map(header => {
        const value = row[header];
        // Escape quotes and wrap in quotes if contains comma
        const stringValue = String(value || '');
        return stringValue.includes(',') || stringValue.includes('"') 
          ? `"${stringValue.replace(/"/g, '""')}"` 
          : stringValue;
      }).join(',')
    );

    return [csvHeaders, ...csvRows].join('\n');
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'SUCCESS':
        return <CheckCircle className="h-4 w-4 text-green-500" />;
      case 'FAILED':
        return <XCircle className="h-4 w-4 text-red-500" />;
      case 'PENDING':
        return <Clock className="h-4 w-4 text-yellow-500" />;
      default:
        return <Clock className="h-4 w-4 text-gray-500" />;
    }
  };

  const getConfidenceColor = (confidence: number) => {
    if (confidence >= 0.8) return 'bg-green-100 text-green-800';
    if (confidence >= 0.6) return 'bg-yellow-100 text-yellow-800';
    return 'bg-red-100 text-red-800';
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-lg font-semibold flex items-center gap-2">
            <MessageSquare className="h-5 w-5" />
            SQL Query Interface
          </h3>
          <p className="text-sm text-muted-foreground">
            Connected to: <Badge variant="outline">{datasourceName}</Badge>
          </p>
        </div>
      </div>

      {/* Error Alert */}
      {error && (
        <Alert variant="destructive">
          <XCircle className="h-4 w-4" />
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      {/* Question Input */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Lightbulb className="h-5 w-5" />
            Natural Language Question
          </CardTitle>
          <CardDescription>
            Ask a question about your data in plain English
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <Textarea
            ref={questionRef}
            placeholder="e.g., Show me all active users from the last 30 days..."
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            className="min-h-[100px] resize-none"
            onKeyDown={(e) => {
              if (e.key === 'Enter' && (e.ctrlKey || e.metaKey)) {
                e.preventDefault();
                handleGenerateSQL();
              }
            }}
          />
          
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              {/* Mode Selection */}
              <div className="flex items-center gap-2">
                <label className="text-sm font-medium">Mode:</label>
                <select
                  value={mode}
                  onChange={(e) => setMode(e.target.value as 'generate' | 'answer')}
                  className="text-sm border rounded px-2 py-1"
                >
                  <option value="answer">Answer Question</option>
                  <option value="generate">Generate SQL Only</option>
                </select>
              </div>

              {/* Options */}
              <div className="flex items-center gap-4">
                <div className="flex items-center gap-2">
                  <input
                    type="checkbox"
                    id="include-explanation"
                    checked={includeExplanation}
                    onChange={(e) => setIncludeExplanation(e.target.checked)}
                    className="rounded"
                  />
                  <label htmlFor="include-explanation" className="text-sm">
                    Include explanation
                  </label>
                </div>

                {mode === 'answer' && (
                  <div className="flex items-center gap-2">
                    <input
                      type="checkbox"
                      id="auto-execute"
                      checked={autoExecute}
                      onChange={(e) => setAutoExecute(e.target.checked)}
                      className="rounded"
                    />
                    <label htmlFor="auto-execute" className="text-sm">
                      Auto execute
                    </label>
                  </div>
                )}
              </div>
            </div>

            <Button
              onClick={handleGenerateSQL}
              disabled={!question.trim() || isGenerating}
              className="flex items-center gap-2"
            >
              {isGenerating ? (
                <Loader2 className="h-4 w-4 animate-spin" />
              ) : (
                <Code className="h-4 w-4" />
              )}
              {mode === 'answer' ? 'Answer Question' : 'Generate SQL'}
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Generated SQL */}
      {generatedSQL && (
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <CardTitle className="flex items-center gap-2">
                <Database className="h-5 w-5" />
                Generated SQL
              </CardTitle>
              <div className="flex items-center gap-2">
                <Badge className={getConfidenceColor(generatedSQL.confidence_score)}>
                  {Math.round(generatedSQL.confidence_score * 100)}% confidence
                </Badge>
                <Button variant="outline" size="sm" onClick={handleCopySQL}>
                  <Copy className="h-4 w-4" />
                </Button>
              </div>
            </div>
            <CardDescription>
              Generated in {generatedSQL.generation_time_ms}ms
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            {/* SQL Code */}
            <div className="relative">
              <pre className="bg-muted p-4 rounded-lg overflow-x-auto text-sm">
                <code>{generatedSQL.generated_sql}</code>
              </pre>
            </div>

            {/* Explanation */}
            {generatedSQL.explanation && (
              <div className="bg-blue-50 p-4 rounded-lg border border-blue-200">
                <h4 className="font-medium text-blue-900 mb-2">Explanation</h4>
                <p className="text-blue-800 text-sm">{generatedSQL.explanation}</p>
              </div>
            )}

            {/* Similar Examples */}
            {generatedSQL.similar_examples && generatedSQL.similar_examples.length > 0 && (
              <div className="bg-gray-50 p-4 rounded-lg border">
                <h4 className="font-medium text-gray-900 mb-2">Similar Queries</h4>
                <div className="space-y-2">
                  {generatedSQL.similar_examples.map((example, index) => (
                    <div key={index} className="text-sm text-gray-700 flex items-center justify-between">
                      <span className="font-mono">{example.query}</span>
                      <Badge variant="outline" className="text-xs">
                        Used {example.usage_count} times
                      </Badge>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Execute Button */}
            <div className="flex justify-center pt-2">
              <Button 
                onClick={handleExecuteSQL}
                disabled={isExecuting}
                className="flex items-center gap-2"
                size="lg"
              >
                {isExecuting ? (
                  <Loader2 className="h-4 w-4 animate-spin" />
                ) : (
                  <Play className="h-4 w-4" />
                )}
                Execute Query
              </Button>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Formatted Answer (Question-Answer Mode) */}
      {formattedAnswer && mode === 'answer' && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <MessageSquare className="h-5 w-5" />
              Answer
            </CardTitle>
            <CardDescription>
              Natural language response to your question
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="bg-blue-50 p-4 rounded-lg border border-blue-200">
              <p className="text-blue-900">{formattedAnswer}</p>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Execution Results */}
      {executionResult && (
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <CardTitle className="flex items-center gap-2">
                {getStatusIcon(executionResult.status)}
                Query Results
              </CardTitle>
              {executionResult.status === 'SUCCESS' && executionResult.result_data && (
                <Button variant="outline" size="sm" onClick={handleDownloadResults}>
                  <Download className="h-4 w-4" />
                </Button>
              )}
            </div>
            <CardDescription>
              {executionResult.status === 'SUCCESS' ? (
                <>
                  {executionResult.result_rows} rows returned in {executionResult.execution_time_ms}ms
                </>
              ) : (
                <>Query execution failed</>
              )}
            </CardDescription>
          </CardHeader>
          <CardContent>
            {executionResult.status === 'SUCCESS' && executionResult.result_data ? (
              <div className="space-y-4">
                {/* Results Table */}
                <ScrollArea className="h-[400px] w-full border rounded-lg">
                  <div className="p-4">
                    {executionResult.result_data.length > 0 ? (
                      <table className="w-full text-sm">
                        <thead>
                          <tr className="border-b">
                            {executionResult.result_data[0] && Object.keys(executionResult.result_data[0]).map((header) => (
                              <th key={header} className="text-left p-2 font-medium">
                                {header}
                              </th>
                            ))}
                          </tr>
                        </thead>
                        <tbody>
                          {executionResult.result_data.map((row, index) => (
                            <tr key={index} className="border-b hover:bg-muted/50">
                              {Object.values(row).map((value, cellIndex) => (
                                <td key={cellIndex} className="p-2">
                                  {String(value || '')}
                                </td>
                              ))}
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    ) : (
                      <div className="text-center py-8 text-muted-foreground">
                        No data returned
                      </div>
                    )}
                  </div>
                </ScrollArea>

                {/* Results Summary */}
                <div className="flex items-center justify-between text-sm text-muted-foreground">
                  <span>
                    Showing {executionResult.result_data.length} of {executionResult.result_rows} rows
                  </span>
                  <span>
                    Execution time: {executionResult.execution_time_ms}ms
                  </span>
                </div>
              </div>
            ) : (
              <Alert variant="destructive">
                <XCircle className="h-4 w-4" />
                <AlertDescription>
                  {executionResult.error_message || 'Query execution failed'}
                </AlertDescription>
              </Alert>
            )}
          </CardContent>
        </Card>
      )}

      {/* Data Visualization */}
      {executionResult && executionResult.status === 'SUCCESS' && executionResult.result_data && (
        <DataVisualization
          data={executionResult.result_data}
          sql={generatedSQL?.generated_sql || ""}
          onExport={(format) => {
            // Handle export functionality
            if (format === 'csv') {
              handleDownloadResults();
            } else if (format === 'json') {
              const json = JSON.stringify(executionResult.result_data, null, 2);
              const blob = new Blob([json], { type: 'application/json' });
              const url = URL.createObjectURL(blob);
              const a = document.createElement('a');
              a.href = url;
              a.download = `query_results_${new Date().toISOString().split('T')[0]}.json`;
              document.body.appendChild(a);
              a.click();
              document.body.removeChild(a);
              URL.revokeObjectURL(url);
            }
          }}
        />
      )}
    </div>
  );
}
