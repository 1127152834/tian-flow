// Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
// SPDX-License-Identifier: MIT

"use client";

import { useState, useEffect } from "react";
import { 
  Loader2, 
  Table, 
  Columns, 
  Search,
  ChevronDown,
  ChevronRight,
  Database,
  RefreshCw
} from "lucide-react";

import { Button } from "~/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "~/components/ui/dialog";
import { Input } from "~/components/ui/input";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "~/components/ui/card";
import { Badge } from "~/components/ui/badge";
import { Skeleton } from "~/components/ui/skeleton";
import {
  Collapsible,
  CollapsibleContent,
  CollapsibleTrigger,
} from "~/components/ui/collapsible";
import { ScrollArea } from "~/components/ui/scroll-area";
import { useToast } from "~/hooks/use-toast";
import {
  type DatabaseDatasource,
  type DatabaseSchemaResponse,
  type DatabaseTable,
  getDatabaseSchema,
} from "~/core/api/database-datasource";

interface DatabaseSchemaDialogProps {
  open: boolean;
  onClose: () => void;
  datasource: DatabaseDatasource;
}

export function DatabaseSchemaDialog({
  open,
  onClose,
  datasource,
}: DatabaseSchemaDialogProps) {
  const [schema, setSchema] = useState<DatabaseSchemaResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [searchTerm, setSearchTerm] = useState("");
  const [expandedTables, setExpandedTables] = useState<Set<string>>(new Set());
  const { toast } = useToast();

  const loadSchema = async () => {
    try {
      setLoading(true);
      const schemaData = await getDatabaseSchema(datasource.id);
      setSchema(schemaData);
    } catch (error: any) {
      console.error("Failed to load schema:", error);
      toast({
        title: "Error",
        description: error.message || "Failed to load database schema",
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (open) {
      loadSchema();
      setSearchTerm("");
      setExpandedTables(new Set());
    }
  }, [open, datasource.id]);

  const toggleTable = (tableName: string) => {
    const newExpanded = new Set(expandedTables);
    if (newExpanded.has(tableName)) {
      newExpanded.delete(tableName);
    } else {
      newExpanded.add(tableName);
    }
    setExpandedTables(newExpanded);
  };

  const filteredTables = schema?.tables.filter(table =>
    table.table_name.toLowerCase().includes(searchTerm.toLowerCase())
  ) || [];

  const formatColumnType = (column: any) => {
    if (datasource.database_type === "MYSQL") {
      return column.Type || column.type || "unknown";
    } else {
      return column.data_type || "unknown";
    }
  };

  const isColumnNullable = (column: any) => {
    if (datasource.database_type === "MYSQL") {
      return column.Null === "YES";
    } else {
      return column.is_nullable === "YES";
    }
  };

  const getColumnName = (column: any) => {
    if (datasource.database_type === "MYSQL") {
      return column.Field || column.field || "unknown";
    } else {
      return column.column_name || "unknown";
    }
  };

  const getColumnDefault = (column: any) => {
    if (datasource.database_type === "MYSQL") {
      return column.Default;
    } else {
      return column.column_default;
    }
  };

  return (
    <Dialog open={open} onOpenChange={onClose}>
      <DialogContent className="max-w-6xl max-h-[95vh] w-[95vw]">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <Database className="h-5 w-5" />
            Database Schema - {datasource.name}
          </DialogTitle>
          <DialogDescription>
            View the structure and columns of all tables in {datasource.database_name}
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-4">
          {/* Header with search and refresh */}
          <div className="flex items-center gap-4">
            <div className="flex-1 relative">
              <Search className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
              <Input
                placeholder="Search tables..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-10"
              />
            </div>
            <Button
              variant="outline"
              size="sm"
              onClick={loadSchema}
              disabled={loading}
            >
              {loading ? (
                <Loader2 className="h-4 w-4 animate-spin" />
              ) : (
                <RefreshCw className="h-4 w-4" />
              )}
            </Button>
          </div>

          {/* Schema content */}
          <ScrollArea className="h-[60vh]">
            {loading ? (
              // Loading state
              <div className="space-y-4">
                {Array.from({ length: 5 }).map((_, i) => (
                  <Card key={i}>
                    <CardHeader>
                      <Skeleton className="h-4 w-1/3" />
                      <Skeleton className="h-3 w-1/2" />
                    </CardHeader>
                  </Card>
                ))}
              </div>
            ) : !schema ? (
              // Error state
              <Card>
                <CardContent className="flex flex-col items-center justify-center py-12">
                  <div className="text-center">
                    <h3 className="text-lg font-medium">Failed to load schema</h3>
                    <p className="text-muted-foreground mb-4">
                      Unable to retrieve database schema information
                    </p>
                    <Button onClick={loadSchema}>
                      <RefreshCw className="mr-2 h-4 w-4" />
                      Try Again
                    </Button>
                  </div>
                </CardContent>
              </Card>
            ) : filteredTables.length === 0 ? (
              // Empty state
              <Card>
                <CardContent className="flex flex-col items-center justify-center py-12">
                  <div className="text-center">
                    <h3 className="text-lg font-medium">No tables found</h3>
                    <p className="text-muted-foreground">
                      {searchTerm 
                        ? `No tables match "${searchTerm}"`
                        : "This database appears to be empty"
                      }
                    </p>
                  </div>
                </CardContent>
              </Card>
            ) : (
              // Tables list
              <div className="space-y-3">
                {/* Summary */}
                <div className="flex items-center gap-4 text-sm text-muted-foreground">
                  <span>
                    {filteredTables.length} of {schema.total_tables} tables
                  </span>
                  <span>•</span>
                  <span>
                    Schema extracted: {new Date(schema.schema_extracted_at).toLocaleString()}
                  </span>
                </div>

                {/* Tables */}
                {filteredTables.map((table) => (
                  <Card key={table.table_name}>
                    <Collapsible
                      open={expandedTables.has(table.table_name)}
                      onOpenChange={() => toggleTable(table.table_name)}
                    >
                      <CollapsibleTrigger asChild>
                        <CardHeader className="cursor-pointer hover:bg-muted/50 transition-colors">
                          <div className="flex items-center justify-between">
                            <div className="flex items-center gap-3">
                              {expandedTables.has(table.table_name) ? (
                                <ChevronDown className="h-4 w-4" />
                              ) : (
                                <ChevronRight className="h-4 w-4" />
                              )}
                              <Table className="h-4 w-4" />
                              <div>
                                <CardTitle className="text-base">
                                  {table.table_name}
                                </CardTitle>
                                <CardDescription>
                                  {table.column_count} columns
                                  {table.schema_name && table.schema_name !== 'public' && (
                                    <span className="ml-2 text-xs">
                                      • Schema: {table.schema_name}
                                    </span>
                                  )}
                                </CardDescription>
                              </div>
                            </div>
                            <Badge variant="outline">
                              <Columns className="mr-1 h-3 w-3" />
                              {table.column_count}
                            </Badge>
                          </div>
                        </CardHeader>
                      </CollapsibleTrigger>

                      <CollapsibleContent>
                        <CardContent className="pt-0">
                          <div className="space-y-2">
                            <h4 className="text-sm font-medium text-muted-foreground">Columns</h4>
                            <div className="grid gap-2">
                              {table.columns.map((column, index) => (
                                <div
                                  key={index}
                                  className="flex items-center justify-between p-2 rounded border bg-muted/20"
                                >
                                  <div className="flex items-center gap-3">
                                    <span className="font-mono text-sm font-medium">
                                      {getColumnName(column)}
                                    </span>
                                    <Badge variant="secondary" className="text-xs">
                                      {formatColumnType(column)}
                                    </Badge>
                                    {!isColumnNullable(column) && (
                                      <Badge variant="outline" className="text-xs">
                                        NOT NULL
                                      </Badge>
                                    )}
                                  </div>
                                  {getColumnDefault(column) && (
                                    <span className="text-xs text-muted-foreground font-mono">
                                      default: {getColumnDefault(column)}
                                    </span>
                                  )}
                                </div>
                              ))}
                            </div>
                          </div>
                        </CardContent>
                      </CollapsibleContent>
                    </Collapsible>
                  </Card>
                ))}
              </div>
            )}
          </ScrollArea>
        </div>
      </DialogContent>
    </Dialog>
  );
}
