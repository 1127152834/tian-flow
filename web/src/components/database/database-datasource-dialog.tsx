// Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
// SPDX-License-Identifier: MIT

"use client";

import { useState, useEffect } from "react";
import { zodResolver } from "@hookform/resolvers/zod";
import { useForm } from "react-hook-form";
import { z } from "zod";
import { Loader2, TestTube, Eye, EyeOff } from "lucide-react";

import { Button } from "~/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "~/components/ui/dialog";
import {
  Form,
  FormControl,
  FormDescription,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "~/components/ui/form";
import { Input } from "~/components/ui/input";
import { Textarea } from "~/components/ui/textarea";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "~/components/ui/select";
import { Switch } from "~/components/ui/switch";
import { Badge } from "~/components/ui/badge";
import { useToast } from "~/hooks/use-toast";
import {
  type DatabaseDatasource,
  type DatabaseDatasourceCreate,
  type DatabaseDatasourceUpdate,
  createDatabaseDatasource,
  updateDatabaseDatasource,
  testDatabaseConnection,
} from "~/core/api/database-datasource";

const datasourceSchema = z.object({
  name: z.string().min(1, "Name is required").max(256, "Name too long"),
  description: z.string().max(4096, "Description too long").optional(),
  database_type: z.enum(["MYSQL", "POSTGRESQL"]),
  host: z.string().min(1, "Host is required").max(256, "Host too long"),
  port: z.number().min(1, "Port must be at least 1").max(65535, "Port must be at most 65535"),
  database_name: z.string().min(1, "Database name is required").max(256, "Database name too long"),
  username: z.string().min(1, "Username is required").max(256, "Username too long"),
  password: z.string().min(1, "Password is required").max(512, "Password too long"),
  readonly_mode: z.boolean(),
  allowed_operations: z.array(z.string()).min(1, "At least one operation must be allowed"),
});

type DatasourceFormData = z.infer<typeof datasourceSchema>;

interface DatabaseDatasourceDialogProps {
  open: boolean;
  onClose: (shouldRefresh?: boolean) => void;
  datasource?: DatabaseDatasource | null;
}

const AVAILABLE_OPERATIONS = [
  "SELECT",
  "INSERT", 
  "UPDATE",
  "DELETE",
  "CREATE",
  "DROP",
  "ALTER",
  "SHOW",
  "DESCRIBE",
];

export function DatabaseDatasourceDialog({
  open,
  onClose,
  datasource,
}: DatabaseDatasourceDialogProps) {
  const [loading, setLoading] = useState(false);
  const [testing, setTesting] = useState(false);
  const [showPassword, setShowPassword] = useState(false);
  const { toast } = useToast();

  const isEditing = !!datasource;

  const form = useForm<DatasourceFormData>({
    resolver: zodResolver(datasourceSchema),
    defaultValues: {
      name: "",
      description: "",
      database_type: "MYSQL",
      host: "localhost",
      port: 3306,
      database_name: "",
      username: "",
      password: "",
      readonly_mode: true,
      allowed_operations: ["SELECT"],
    },
  });

  // Reset form when dialog opens/closes or datasource changes
  useEffect(() => {
    if (open) {
      if (datasource) {
        // Editing existing datasource
        form.reset({
          name: datasource.name,
          description: datasource.description || "",
          database_type: datasource.database_type,
          host: datasource.host,
          port: datasource.port,
          database_name: datasource.database_name,
          username: datasource.username,
          password: "", // Don't pre-fill password for security
          readonly_mode: datasource.readonly_mode,
          allowed_operations: datasource.allowed_operations,
        });
      } else {
        // Creating new datasource
        form.reset({
          name: "",
          description: "",
          database_type: "MYSQL",
          host: "localhost",
          port: 3306,
          database_name: "",
          username: "",
          password: "",
          readonly_mode: true,
          allowed_operations: ["SELECT"],
        });
      }
    }
  }, [open, datasource, form]);

  // Update default port when database type changes
  const watchedDatabaseType = form.watch("database_type");
  useEffect(() => {
    if (watchedDatabaseType === "MYSQL" && form.getValues("port") === 5432) {
      form.setValue("port", 3306);
    } else if (watchedDatabaseType === "POSTGRESQL" && form.getValues("port") === 3306) {
      form.setValue("port", 5432);
    }
  }, [watchedDatabaseType, form]);

  const onSubmit = async (data: DatasourceFormData) => {
    try {
      setLoading(true);
      
      if (isEditing && datasource) {
        // Update existing datasource
        const updateData: DatabaseDatasourceUpdate = { ...data };
        // Don't send password if it's empty (keep existing password)
        if (!data.password) {
          delete updateData.password;
        }
        
        await updateDatabaseDatasource(datasource.id, updateData);
        toast({
          title: "Success",
          description: "Datasource updated successfully",
        });
      } else {
        // Create new datasource
        const createData: DatabaseDatasourceCreate = data;
        await createDatabaseDatasource(createData);
        toast({
          title: "Success", 
          description: "Datasource created successfully",
        });
      }
      
      onClose(true); // Refresh the list
    } catch (error: any) {
      console.error("Failed to save datasource:", error);
      toast({
        title: "Error",
        description: error.message || "Failed to save datasource",
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  const handleTestConnection = async () => {
    const formData = form.getValues();
    
    // Validate required fields for testing
    if (!formData.host || !formData.port || !formData.database_name || 
        !formData.username || !formData.password) {
      toast({
        title: "Validation Error",
        description: "Please fill in all connection fields before testing",
        variant: "destructive",
      });
      return;
    }

    try {
      setTesting(true);
      
      // For testing, we need to create a temporary datasource or use existing one
      if (isEditing && datasource) {
        const result = await testDatabaseConnection(datasource.id, 10);
        if (result.success) {
          toast({
            title: "Connection Test Successful",
            description: "Database connection is working properly",
          });
        } else {
          toast({
            title: "Connection Test Failed",
            description: result.error || "Unknown error occurred",
            variant: "destructive",
          });
        }
      } else {
        toast({
          title: "Test Connection",
          description: "Please save the datasource first to test the connection",
          variant: "default",
        });
      }
    } catch (error: any) {
      console.error("Failed to test connection:", error);
      toast({
        title: "Error",
        description: error.message || "Failed to test database connection",
        variant: "destructive",
      });
    } finally {
      setTesting(false);
    }
  };

  const toggleOperation = (operation: string) => {
    const currentOps = form.getValues("allowed_operations");
    if (currentOps.includes(operation)) {
      form.setValue("allowed_operations", currentOps.filter(op => op !== operation));
    } else {
      form.setValue("allowed_operations", [...currentOps, operation]);
    }
  };

  return (
    <Dialog open={open} onOpenChange={() => onClose()}>
      <DialogContent className="max-w-4xl max-h-[95vh] w-[90vw] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>
            {isEditing ? "Edit Database Datasource" : "Create Database Datasource"}
          </DialogTitle>
          <DialogDescription>
            {isEditing 
              ? "Update the database connection settings."
              : "Add a new database connection for Text2SQL and data analysis."
            }
          </DialogDescription>
        </DialogHeader>

        <Form {...form}>
          <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-6">
            {/* Basic Information */}
            <div className="space-y-4">
              <h3 className="text-lg font-medium">Basic Information</h3>
              
              <FormField
                control={form.control}
                name="name"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Name *</FormLabel>
                    <FormControl>
                      <Input placeholder="My Database" {...field} />
                    </FormControl>
                    <FormDescription>
                      A friendly name for this database connection
                    </FormDescription>
                    <FormMessage />
                  </FormItem>
                )}
              />

              <FormField
                control={form.control}
                name="description"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Description</FormLabel>
                    <FormControl>
                      <Textarea 
                        placeholder="Optional description of this database..."
                        className="resize-none"
                        rows={3}
                        {...field}
                      />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
            </div>

            {/* Connection Settings */}
            <div className="space-y-4">
              <h3 className="text-lg font-medium">Connection Settings</h3>
              
              <FormField
                control={form.control}
                name="database_type"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Database Type *</FormLabel>
                    <Select onValueChange={field.onChange} defaultValue={field.value}>
                      <FormControl>
                        <SelectTrigger>
                          <SelectValue placeholder="Select database type" />
                        </SelectTrigger>
                      </FormControl>
                      <SelectContent>
                        <SelectItem value="MYSQL">MySQL</SelectItem>
                        <SelectItem value="POSTGRESQL">PostgreSQL</SelectItem>
                      </SelectContent>
                    </Select>
                    <FormMessage />
                  </FormItem>
                )}
              />

              <div className="grid grid-cols-2 gap-4">
                <FormField
                  control={form.control}
                  name="host"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Host *</FormLabel>
                      <FormControl>
                        <Input placeholder="localhost" {...field} />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />

                <FormField
                  control={form.control}
                  name="port"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Port *</FormLabel>
                      <FormControl>
                        <Input 
                          type="number"
                          min={1}
                          max={65535}
                          {...field}
                          onChange={(e) => field.onChange(parseInt(e.target.value) || 0)}
                        />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />
              </div>

              <FormField
                control={form.control}
                name="database_name"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Database Name *</FormLabel>
                    <FormControl>
                      <Input placeholder="my_database" {...field} />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />

              <div className="grid grid-cols-2 gap-4">
                <FormField
                  control={form.control}
                  name="username"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Username *</FormLabel>
                      <FormControl>
                        <Input placeholder="username" {...field} />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />

                <FormField
                  control={form.control}
                  name="password"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>
                        Password {isEditing && "*"}
                        {isEditing && (
                          <span className="text-xs text-muted-foreground ml-2">
                            (leave empty to keep current)
                          </span>
                        )}
                      </FormLabel>
                      <FormControl>
                        <div className="relative">
                          <Input 
                            type={showPassword ? "text" : "password"}
                            placeholder={isEditing ? "••••••••" : "password"}
                            {...field}
                          />
                          <Button
                            type="button"
                            variant="ghost"
                            size="sm"
                            className="absolute right-0 top-0 h-full px-3 py-2 hover:bg-transparent"
                            onClick={() => setShowPassword(!showPassword)}
                          >
                            {showPassword ? (
                              <EyeOff className="h-4 w-4" />
                            ) : (
                              <Eye className="h-4 w-4" />
                            )}
                          </Button>
                        </div>
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />
              </div>
            </div>

            {/* Security Settings */}
            <div className="space-y-4">
              <h3 className="text-lg font-medium">Security Settings</h3>
              
              <FormField
                control={form.control}
                name="readonly_mode"
                render={({ field }) => (
                  <FormItem className="flex flex-row items-center justify-between rounded-lg border p-4">
                    <div className="space-y-0.5">
                      <FormLabel className="text-base">Read-only Mode</FormLabel>
                      <FormDescription>
                        Restrict this connection to read-only operations for safety
                      </FormDescription>
                    </div>
                    <FormControl>
                      <Switch
                        checked={field.value}
                        onCheckedChange={field.onChange}
                      />
                    </FormControl>
                  </FormItem>
                )}
              />

              <FormField
                control={form.control}
                name="allowed_operations"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Allowed Operations</FormLabel>
                    <FormDescription>
                      Select which SQL operations are permitted for this connection
                    </FormDescription>
                    <FormControl>
                      <div className="flex flex-wrap gap-2">
                        {AVAILABLE_OPERATIONS.map((operation) => (
                          <Badge
                            key={operation}
                            variant={field.value.includes(operation) ? "default" : "outline"}
                            className="cursor-pointer"
                            onClick={() => toggleOperation(operation)}
                          >
                            {operation}
                          </Badge>
                        ))}
                      </div>
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
            </div>

            <DialogFooter className="gap-2">
              <Button
                type="button"
                variant="outline"
                onClick={handleTestConnection}
                disabled={testing || loading}
              >
                {testing ? (
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                ) : (
                  <TestTube className="mr-2 h-4 w-4" />
                )}
                Test Connection
              </Button>
              
              <Button type="button" variant="outline" onClick={() => onClose()}>
                Cancel
              </Button>
              
              <Button type="submit" disabled={loading}>
                {loading ? (
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                ) : null}
                {isEditing ? "Update" : "Create"}
              </Button>
            </DialogFooter>
          </form>
        </Form>
      </DialogContent>
    </Dialog>
  );
}
