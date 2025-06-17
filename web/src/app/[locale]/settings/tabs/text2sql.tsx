"use client";

import { useState, useEffect } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "~/components/ui/card";
import { useLanguage } from "~/contexts/language-context";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "~/components/ui/tabs";
import { Badge } from "~/components/ui/badge";
import { Button } from "~/components/ui/button";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "~/components/ui/select";
import { Alert, AlertDescription } from "~/components/ui/alert";
import {
  Brain,
  Database,
  FileText,
  BarChart3,
  Settings,
  Play,
  BookOpen,
  Code,
  TestTube,
  CheckCircle,
  XCircle,
  Loader2
} from "lucide-react";
import { text2sqlApi, type Text2SQLStatistics } from "~/core/api/text2sql";
import { databaseApi } from "~/core/api/database";

// Import training components (following ti-flow structure)
import { TrainingOverviewComponent } from "~/components/text2sql/TrainingOverviewComponent";
import { TrainingDataManager } from "~/components/text2sql/TrainingDataManager";
import { DDLTrainingComponent } from "~/components/text2sql/DDLTrainingComponent";
import { DocumentationTrainingComponent } from "~/components/text2sql/DocumentationTrainingComponent";
import { SQLTrainingComponent } from "~/components/text2sql/SQLTrainingComponent";
import { ModelTestComponent } from "~/components/text2sql/ModelTestComponent";
import type { Tab } from "./types";

interface DatabaseDatasource {
  id: number;
  name: string;
  database_type: string;
  host: string;
  port: number;
  database_name: string;
  connection_status: string;
}

const Text2SQLTab: Tab = () => {
  const { t } = useLanguage();
  const [selectedDatasource, setSelectedDatasource] = useState<number | null>(null);
  const [datasources, setDatasources] = useState<DatabaseDatasource[]>([]);
  const [statistics, setStatistics] = useState<Text2SQLStatistics | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState('overview');

  // Load datasources on component mount
  useEffect(() => {
    loadDatasources();
  }, []);

  // Load statistics when datasource is selected
  useEffect(() => {
    if (selectedDatasource) {
      loadStatistics();
    }
  }, [selectedDatasource]);

  const loadDatasources = async () => {
    try {
      setLoading(true);
      const response = await databaseApi.getDatasources();
      setDatasources(response.datasources || []);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load datasources');
    } finally {
      setLoading(false);
    }
  };



  const loadStatistics = async () => {
    if (!selectedDatasource) return;

    try {
      const stats = await text2sqlApi.getStatistics(selectedDatasource);
      setStatistics(stats);
      setError(null);
    } catch (err) {
      console.error('Failed to load statistics:', err);
      setError(err instanceof Error ? err.message : 'Failed to load statistics');
      // Set empty statistics to show zero values instead of hiding the UI
      setStatistics({
        total_queries: 0,
        successful_queries: 0,
        failed_queries: 0,
        average_confidence: 0,
        total_training_data: 0,
        training_data_by_type: {
          DDL: 0,
          DOCUMENTATION: 0,
          SQL: 0,
          SCHEMA: 0
        },
        last_query_time: null,
        last_training_time: null
      });
    }
  };

  const getSelectedDatasource = () => {
    return datasources.find(ds => ds.id === selectedDatasource);
  };

  const getStatusIcon = (status: string) => {
    switch (status.toLowerCase()) {
      case 'connected':
        return <CheckCircle className="h-4 w-4 text-green-500" />;
      case 'disconnected':
      case 'error':
        return <XCircle className="h-4 w-4 text-red-500" />;
      default:
        return <XCircle className="h-4 w-4 text-gray-500" />;
    }
  };

  const selectedDatasourceData = getSelectedDatasource();

  return (
    <div className="container mx-auto p-6 space-y-6 max-w-6xl">
      {/* Breadcrumb-style Header (following ti-flow pattern) */}
      <div className="space-y-2">
        <div className="flex items-center gap-2 text-sm text-muted-foreground">
          <span>{t('settings.text2sql.breadcrumb.settings')}</span>
          <span>/</span>
          <span>{t('settings.text2sql.breadcrumb.text2sql')}</span>
          {selectedDatasourceData && (
            <>
              <span>/</span>
              <span>{selectedDatasourceData.name}</span>
            </>
          )}
        </div>
        <h1 className="text-3xl font-bold tracking-tight flex items-center gap-2">
          <Brain className="h-8 w-8" />
          {t('settings.text2sql.title')}
        </h1>
        <p className="text-muted-foreground">
          {t('settings.text2sql.description')}
        </p>
      </div>

      {/* Error Alert */}
      {error && (
        <Alert variant="destructive">
          <XCircle className="h-4 w-4" />
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      {/* Datasource Selection */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Database className="h-5 w-5" />
            {t('settings.text2sql.datasource.title')}
          </CardTitle>
          <CardDescription>
            {t('settings.text2sql.datasource.description')}
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex items-center gap-4">
            <div className="flex-1 max-w-md">
              <Select
                value={selectedDatasource?.toString() || ""}
                onValueChange={(value) => setSelectedDatasource(parseInt(value))}
              >
                <SelectTrigger>
                  <SelectValue placeholder={t('settings.text2sql.datasource.placeholder')} />
                </SelectTrigger>
                <SelectContent>
                  {datasources.map((ds) => (
                    <SelectItem key={ds.id} value={ds.id.toString()}>
                      <div className="flex items-center gap-2">
                        <span>{ds.name}</span>
                        <Badge variant="outline" className="text-xs">
                          {ds.database_type}
                        </Badge>
                        {getStatusIcon(ds.connection_status)}
                      </div>
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            {selectedDatasourceData && (
              <div className="flex items-center gap-2 text-sm text-muted-foreground">
                <span>{selectedDatasourceData.host}:{selectedDatasourceData.port}</span>
                <span>/</span>
                <span>{selectedDatasourceData.database_name}</span>
              </div>
            )}
          </div>

          {datasources.length === 0 && (
            <Alert className="mt-4">
              <Database className="h-4 w-4" />
              <AlertDescription>
                {t('settings.text2sql.datasource.noDataSources')}
              </AlertDescription>
            </Alert>
          )}
        </CardContent>
      </Card>

      {/* Main Training Interface - Only show when datasource is selected */}
      {selectedDatasource && (
        <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
          <TabsList className="grid w-full grid-cols-6">
            <TabsTrigger value="overview" className="flex items-center gap-2">
              <BarChart3 className="h-4 w-4" />
              {t('settings.text2sql.tabs.overview')}
            </TabsTrigger>
            <TabsTrigger value="data-management" className="flex items-center gap-2">
              <FileText className="h-4 w-4" />
              {t('settings.text2sql.tabs.dataManagement')}
            </TabsTrigger>
            <TabsTrigger value="ddl" className="flex items-center gap-2">
              <Database className="h-4 w-4" />
              {t('settings.text2sql.tabs.ddlTraining')}
            </TabsTrigger>
            <TabsTrigger value="documentation" className="flex items-center gap-2">
              <BookOpen className="h-4 w-4" />
              {t('settings.text2sql.tabs.documentationTraining')}
            </TabsTrigger>
            <TabsTrigger value="sql" className="flex items-center gap-2">
              <Brain className="h-4 w-4" />
              {t('settings.text2sql.tabs.sqlTraining')}
            </TabsTrigger>
            <TabsTrigger value="test" className="flex items-center gap-2">
              <TestTube className="h-4 w-4" />
              {t('settings.text2sql.tabs.modelTest')}
            </TabsTrigger>
          </TabsList>

          {/* 训练概览 */}
          <TabsContent value="overview" className="space-y-6">
            <TrainingOverviewComponent
              datasourceId={selectedDatasource}
              statistics={statistics}
              onTabChange={setActiveTab}
            />
          </TabsContent>

          {/* 数据管理 */}
          <TabsContent value="data-management" className="space-y-6">
            <TrainingDataManager
              datasourceId={selectedDatasource}
              datasourceName={selectedDatasourceData?.name || 'Unknown'}
            />
          </TabsContent>

          {/* DDL训练 */}
          <TabsContent value="ddl" className="space-y-6">
            <DDLTrainingComponent
              datasourceId={selectedDatasource}
            />
          </TabsContent>

          {/* 文档训练 */}
          <TabsContent value="documentation" className="space-y-6">
            <DocumentationTrainingComponent
              datasourceId={selectedDatasource}
            />
          </TabsContent>

          {/* SQL训练 */}
          <TabsContent value="sql" className="space-y-6">
            <SQLTrainingComponent
              datasourceId={selectedDatasource}
            />
          </TabsContent>

          {/* 模型测试 */}
          <TabsContent value="test" className="space-y-6">
            <ModelTestComponent
              datasourceId={selectedDatasource}
            />
          </TabsContent>

        </Tabs>
      )}
    </div>
  );
};

Text2SQLTab.displayName = "Text2SQL";
Text2SQLTab.icon = Brain;

export { Text2SQLTab };
export default Text2SQLTab;
