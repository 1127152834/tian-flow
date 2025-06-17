// Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
// SPDX-License-Identifier: MIT

"use client";

import { useState } from "react";
import { 
  MoreHorizontal, 
  Edit, 
  Trash2, 
  TestTube, 
  Database, 
  Eye,
  Clock,
  AlertCircle,
  CheckCircle,
  Loader2
} from "lucide-react";

import { Button } from "~/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "~/components/ui/card";
import { Badge } from "~/components/ui/badge";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "~/components/ui/dropdown-menu";
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from "~/components/ui/alert-dialog";
import { useToast } from "~/hooks/use-toast";
import { useLanguage } from "~/contexts/language-context";
import {
  type DatabaseDatasource,
  deleteDatabaseDatasource,
  testDatabaseConnection,
  formatConnectionStatus,
  getConnectionStatusColor,
  formatDatabaseType,
} from "~/core/api/database-datasource";

import { DatabaseSchemaDialog } from "./database-schema-dialog";

interface DatabaseDatasourceCardProps {
  datasource: DatabaseDatasource;
  onEdit: (datasource: DatabaseDatasource) => void;
  onDelete: () => void;
  onRefresh?: () => void; // Add refresh callback
}

export function DatabaseDatasourceCard({
  datasource,
  onEdit,
  onDelete,
  onRefresh
}: DatabaseDatasourceCardProps) {
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [schemaDialogOpen, setSchemaDialogOpen] = useState(false);
  const [testing, setTesting] = useState(false);
  const { toast } = useToast();
  const { t } = useLanguage();

  const handleEdit = () => {
    onEdit(datasource);
  };

  const handleDelete = async () => {
    try {
      await deleteDatabaseDatasource(datasource.id);
      toast({
        title: t('settings.database.card.messages.deleteSuccess'),
        description: t('settings.database.card.messages.deleteSuccessDescription'),
      });
      onDelete();
    } catch (error) {
      console.error("Failed to delete datasource:", error);
      toast({
        title: t('settings.database.card.messages.deleteFailed'),
        description: t('settings.database.card.messages.deleteFailedDescription'),
        variant: "destructive",
      });
    } finally {
      setDeleteDialogOpen(false);
    }
  };

  const handleTestConnection = async () => {
    try {
      setTesting(true);
      const result = await testDatabaseConnection(datasource.id, 10);

      if (result.success) {
        toast({
          title: t('settings.database.card.messages.testSuccess'),
          description: t('settings.database.card.messages.testSuccessDescription'),
        });
        // Refresh the datasource list to show updated status
        if (onRefresh) {
          onRefresh();
        }
      } else {
        toast({
          title: t('settings.database.card.messages.testFailed'),
          description: t('settings.database.card.messages.testFailedDescription', { error: result.error || "Unknown error occurred" }),
          variant: "destructive",
        });
        // Also refresh on failure to show updated error status
        if (onRefresh) {
          onRefresh();
        }
      }
    } catch (error) {
      console.error("Failed to test connection:", error);
      toast({
        title: t('settings.database.card.messages.testError'),
        description: t('settings.database.card.messages.testErrorDescription'),
        variant: "destructive",
      });
      // Refresh even on error to show any status changes
      if (onRefresh) {
        onRefresh();
      }
    } finally {
      setTesting(false);
    }
  };

  const handleViewSchema = () => {
    setSchemaDialogOpen(true);
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case "CONNECTED":
        return <CheckCircle className="h-4 w-4 text-green-500" />;
      case "ERROR":
        return <AlertCircle className="h-4 w-4 text-red-500" />;
      case "TESTING":
        return <Loader2 className="h-4 w-4 text-blue-500 animate-spin" />;
      default:
        return <Clock className="h-4 w-4 text-gray-500" />;
    }
  };

  const formatLastTested = (dateString?: string) => {
    if (!dateString) return t('settings.database.card.neverTested');

    const date = new Date(dateString);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / (1000 * 60));
    const diffHours = Math.floor(diffMins / 60);
    const diffDays = Math.floor(diffHours / 24);

    if (diffMins < 1) return t('settings.database.card.justNow');
    if (diffMins < 60) return t('settings.database.card.minutesAgo', { minutes: diffMins });
    if (diffHours < 24) return t('settings.database.card.hoursAgo', { hours: diffHours });
    if (diffDays < 7) return t('settings.database.card.daysAgo', { days: diffDays });

    return date.toLocaleDateString();
  };

  return (
    <>
      <Card className="hover:shadow-md transition-shadow">
        <CardHeader className="pb-3">
          <div className="flex items-start justify-between">
            <div className="space-y-1">
              <CardTitle className="text-lg">{datasource.name}</CardTitle>
              <CardDescription className="line-clamp-2">
                {datasource.description || t('settings.database.card.noDescription')}
              </CardDescription>
            </div>
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button variant="ghost" size="sm">
                  <MoreHorizontal className="h-4 w-4" />
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end">
                <DropdownMenuItem onClick={handleEdit}>
                  <Edit className="mr-2 h-4 w-4" />
                  {t('settings.database.card.actions.edit')}
                </DropdownMenuItem>
                <DropdownMenuItem onClick={handleTestConnection} disabled={testing}>
                  {testing ? (
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  ) : (
                    <TestTube className="mr-2 h-4 w-4" />
                  )}
                  {t('settings.database.card.actions.testConnection')}
                </DropdownMenuItem>
                <DropdownMenuItem onClick={handleViewSchema}>
                  <Eye className="mr-2 h-4 w-4" />
                  {t('settings.database.card.actions.viewSchema')}
                </DropdownMenuItem>
                <DropdownMenuSeparator />
                <DropdownMenuItem
                  onClick={() => setDeleteDialogOpen(true)}
                  className="text-red-600"
                >
                  <Trash2 className="mr-2 h-4 w-4" />
                  {t('settings.database.card.actions.delete')}
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
          </div>
        </CardHeader>
        
        <CardContent className="space-y-4">
          {/* Connection Info */}
          <div className="space-y-2">
            <div className="flex items-center gap-2 text-sm">
              <Database className="h-4 w-4 text-muted-foreground" />
              <span className="font-medium">{formatDatabaseType(datasource.database_type)}</span>
              <span className="text-muted-foreground">•</span>
              <span className="text-muted-foreground">
                {datasource.host}:{datasource.port}
              </span>
            </div>
            
            <div className="flex items-center gap-2 text-sm">
              <span className="text-muted-foreground">{t('settings.database.card.database')}:</span>
              <span className="font-mono">{datasource.database_name}</span>
            </div>

            <div className="flex items-center gap-2 text-sm">
              <span className="text-muted-foreground">{t('settings.database.card.user')}:</span>
              <span className="font-mono">{datasource.username}</span>
            </div>
          </div>

          {/* Status and Badges */}
          <div className="flex flex-wrap gap-2">
            <Badge
              variant="outline"
              className={`border-${getConnectionStatusColor(testing ? "TESTING" : datasource.connection_status)}-200 text-${getConnectionStatusColor(testing ? "TESTING" : datasource.connection_status)}-700`}
            >
              {getStatusIcon(testing ? "TESTING" : datasource.connection_status)}
              <span className="ml-1">{formatConnectionStatus(testing ? "TESTING" : datasource.connection_status)}</span>
            </Badge>
            
            {datasource.readonly_mode && (
              <Badge variant="secondary">{t('settings.database.card.readOnly')}</Badge>
            )}

            <Badge variant="outline">
              {t('settings.database.card.operations', { count: datasource.allowed_operations.length })}
            </Badge>
          </div>

          {/* Last Tested */}
          <div className="text-xs text-muted-foreground">
            {t('settings.database.card.lastTested', { time: formatLastTested(datasource.last_tested_at) })}
          </div>

          {/* Connection Error */}
          {datasource.connection_error && (
            <div className="text-xs text-red-600 bg-red-50 p-2 rounded border">
              <AlertCircle className="h-3 w-3 inline mr-1" />
              {datasource.connection_error}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Delete Confirmation Dialog */}
      <AlertDialog open={deleteDialogOpen} onOpenChange={setDeleteDialogOpen}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>{t('settings.database.card.deleteDialog.title')}</AlertDialogTitle>
            <AlertDialogDescription>
              {t('settings.database.card.deleteDialog.description', { name: datasource.name })}
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>{t('settings.database.card.deleteDialog.cancel')}</AlertDialogCancel>
            <AlertDialogAction onClick={handleDelete} className="bg-red-600 hover:bg-red-700">
              {t('settings.database.card.deleteDialog.delete')}
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>

      {/* Schema Dialog */}
      <DatabaseSchemaDialog
        open={schemaDialogOpen}
        onClose={() => setSchemaDialogOpen(false)}
        datasource={datasource}
      />
    </>
  );
}
