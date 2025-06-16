// Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
// SPDX-License-Identifier: MIT

"use client";

import { useState, useEffect } from "react";
import { Plus, Search, Filter, RefreshCw } from "lucide-react";

import { Button } from "~/components/ui/button";
import { Input } from "~/components/ui/input";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "~/components/ui/card";
import { Badge } from "~/components/ui/badge";
import { Skeleton } from "~/components/ui/skeleton";
import { useToast } from "~/hooks/use-toast";
import {
  listDatabaseDatasources,
  type DatabaseDatasource,
  formatConnectionStatus,
  getConnectionStatusColor,
  formatDatabaseType,
} from "~/core/api/database-datasource";

import { DatabaseDatasourceDialog } from "./database-datasource-dialog";
import { DatabaseDatasourceCard } from "./database-datasource-card";

export function DatabaseDatasourceManager() {
  const [datasources, setDatasources] = useState<DatabaseDatasource[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState("");
  const [filterType, setFilterType] = useState<string>("");
  const [filterStatus, setFilterStatus] = useState<string>("");
  const [dialogOpen, setDialogOpen] = useState(false);
  const [editingDatasource, setEditingDatasource] = useState<DatabaseDatasource | null>(null);
  const { toast } = useToast();

  const loadDatasources = async () => {
    try {
      setLoading(true);
      const response = await listDatabaseDatasources({
        search: searchTerm || undefined,
        database_type: filterType || undefined,
        connection_status: filterStatus || undefined,
        limit: 50,
        offset: 0,
      });
      setDatasources(response.datasources);
    } catch (error) {
      console.error("Failed to load datasources:", error);
      toast({
        title: "Error",
        description: "Failed to load database datasources",
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadDatasources();
  }, [searchTerm, filterType, filterStatus]);

  const handleCreateDatasource = () => {
    setEditingDatasource(null);
    setDialogOpen(true);
  };

  const handleEditDatasource = (datasource: DatabaseDatasource) => {
    setEditingDatasource(datasource);
    setDialogOpen(true);
  };

  const handleDialogClose = (shouldRefresh?: boolean) => {
    setDialogOpen(false);
    setEditingDatasource(null);
    if (shouldRefresh) {
      loadDatasources();
    }
  };

  const handleDeleteDatasource = () => {
    // Refresh the list after deletion
    loadDatasources();
  };

  const handleRefreshDatasources = () => {
    // Refresh the list after connection test or other operations
    loadDatasources();
  };

  const filteredDatasources = datasources.filter((ds) => {
    const matchesSearch = !searchTerm || 
      ds.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      (ds.description && ds.description.toLowerCase().includes(searchTerm.toLowerCase()));
    
    const matchesType = !filterType || ds.database_type === filterType;
    const matchesStatus = !filterStatus || ds.connection_status === filterStatus;
    
    return matchesSearch && matchesType && matchesStatus;
  });

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold tracking-tight">Database Datasources</h2>
          <p className="text-muted-foreground">
            Manage your database connections for Text2SQL and data analysis.
          </p>
        </div>
        <Button onClick={handleCreateDatasource}>
          <Plus className="mr-2 h-4 w-4" />
          Add Datasource
        </Button>
      </div>

      {/* Search and Filters */}
      <Card>
        <CardHeader>
          <CardTitle className="text-lg">Search & Filter</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex flex-col gap-4 md:flex-row md:items-center">
            <div className="flex-1">
              <div className="relative">
                <Search className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
                <Input
                  placeholder="Search datasources..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="pl-10"
                />
              </div>
            </div>
            
            <div className="flex gap-2">
              <select
                value={filterType}
                onChange={(e) => setFilterType(e.target.value)}
                className="rounded-md border border-input bg-background px-3 py-2 text-sm"
              >
                <option value="">All Types</option>
                <option value="MYSQL">MySQL</option>
                <option value="POSTGRESQL">PostgreSQL</option>
              </select>
              
              <select
                value={filterStatus}
                onChange={(e) => setFilterStatus(e.target.value)}
                className="rounded-md border border-input bg-background px-3 py-2 text-sm"
              >
                <option value="">All Status</option>
                <option value="CONNECTED">Connected</option>
                <option value="DISCONNECTED">Disconnected</option>
                <option value="ERROR">Error</option>
              </select>
              
              <Button variant="outline" size="sm" onClick={loadDatasources}>
                <RefreshCw className="h-4 w-4" />
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Datasources List */}
      <div className="space-y-4">
        {loading ? (
          // Loading skeletons
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
            {Array.from({ length: 6 }).map((_, i) => (
              <Card key={i}>
                <CardHeader>
                  <Skeleton className="h-4 w-3/4" />
                  <Skeleton className="h-3 w-1/2" />
                </CardHeader>
                <CardContent>
                  <div className="space-y-2">
                    <Skeleton className="h-3 w-full" />
                    <Skeleton className="h-3 w-2/3" />
                    <div className="flex gap-2">
                      <Skeleton className="h-6 w-16" />
                      <Skeleton className="h-6 w-20" />
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        ) : filteredDatasources.length === 0 ? (
          // Empty state
          <Card>
            <CardContent className="flex flex-col items-center justify-center py-12">
              <div className="text-center">
                <h3 className="text-lg font-medium">No datasources found</h3>
                <p className="text-muted-foreground mb-4">
                  {searchTerm || filterType || filterStatus
                    ? "Try adjusting your search or filters"
                    : "Get started by creating your first database datasource"}
                </p>
                {!searchTerm && !filterType && !filterStatus && (
                  <Button onClick={handleCreateDatasource}>
                    <Plus className="mr-2 h-4 w-4" />
                    Add Your First Datasource
                  </Button>
                )}
              </div>
            </CardContent>
          </Card>
        ) : (
          // Datasources grid
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 2xl:grid-cols-5">
            {filteredDatasources.map((datasource) => (
              <DatabaseDatasourceCard
                key={datasource.id}
                datasource={datasource}
                onEdit={handleEditDatasource}
                onDelete={handleDeleteDatasource}
                onRefresh={handleRefreshDatasources}
              />
            ))}
          </div>
        )}
      </div>

      {/* Create/Edit Dialog */}
      <DatabaseDatasourceDialog
        open={dialogOpen}
        onClose={handleDialogClose}
        datasource={editingDatasource}
      />
    </div>
  );
}
