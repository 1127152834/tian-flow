// Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
// SPDX-License-Identifier: MIT

"use client";

import * as React from "react";
import { AlertTriangle, Info, HelpCircle, CheckCircle } from "lucide-react";
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
import { Button } from "~/components/ui/button";
import { cn } from "~/lib/utils";

export type ConfirmDialogType = "warning" | "danger" | "info" | "success";

interface ConfirmDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  title: string;
  description: string;
  confirmText?: string;
  cancelText?: string;
  type?: ConfirmDialogType;
  onConfirm: () => void | Promise<void>;
  loading?: boolean;
  destructive?: boolean;
}

const typeConfig = {
  warning: {
    icon: AlertTriangle,
    iconColor: "text-amber-500",
    confirmVariant: "default" as const,
  },
  danger: {
    icon: AlertTriangle,
    iconColor: "text-red-500",
    confirmVariant: "destructive" as const,
  },
  info: {
    icon: Info,
    iconColor: "text-blue-500",
    confirmVariant: "default" as const,
  },
  success: {
    icon: CheckCircle,
    iconColor: "text-green-500",
    confirmVariant: "default" as const,
  },
};

export function ConfirmDialog({
  open,
  onOpenChange,
  title,
  description,
  confirmText = "确认",
  cancelText = "取消",
  type = "warning",
  onConfirm,
  loading = false,
  destructive = false,
}: ConfirmDialogProps) {
  const config = typeConfig[type];
  const Icon = config.icon;
  
  const handleConfirm = async () => {
    try {
      await onConfirm();
      onOpenChange(false);
    } catch (error) {
      // Error handling should be done by the parent component
      console.error("Confirm action failed:", error);
    }
  };

  return (
    <AlertDialog open={open} onOpenChange={onOpenChange}>
      <AlertDialogContent className="w-96">
        <AlertDialogHeader>
          <div className="flex items-center gap-3">
            <Icon className={cn("h-5 w-5", config.iconColor)} />
            <AlertDialogTitle className="text-left">{title}</AlertDialogTitle>
          </div>
          <AlertDialogDescription className="text-left">
            {description}
          </AlertDialogDescription>
        </AlertDialogHeader>
        <AlertDialogFooter>
          <AlertDialogCancel disabled={loading}>
            {cancelText}
          </AlertDialogCancel>
          <AlertDialogAction
            onClick={handleConfirm}
            disabled={loading}
            className={cn(
              destructive || type === "danger"
                ? "bg-red-600 hover:bg-red-700 focus:ring-red-600"
                : ""
            )}
          >
            {loading ? "处理中..." : confirmText}
          </AlertDialogAction>
        </AlertDialogFooter>
      </AlertDialogContent>
    </AlertDialog>
  );
}

// Hook for easier usage
export function useConfirmDialog() {
  const [dialogState, setDialogState] = React.useState<{
    open: boolean;
    title: string;
    description: string;
    confirmText?: string;
    cancelText?: string;
    type?: ConfirmDialogType;
    onConfirm: () => void | Promise<void>;
    loading?: boolean;
    destructive?: boolean;
  }>({
    open: false,
    title: "",
    description: "",
    onConfirm: () => {},
  });

  const showConfirm = React.useCallback((options: {
    title: string;
    description: string;
    confirmText?: string;
    cancelText?: string;
    type?: ConfirmDialogType;
    onConfirm: () => void | Promise<void>;
    destructive?: boolean;
  }) => {
    setDialogState({
      open: true,
      loading: false,
      ...options,
    });
  }, []);

  const hideConfirm = React.useCallback(() => {
    setDialogState(prev => ({ ...prev, open: false }));
  }, []);

  const setLoading = React.useCallback((loading: boolean) => {
    setDialogState(prev => ({ ...prev, loading }));
  }, []);

  const ConfirmDialogComponent = React.useCallback(() => (
    <ConfirmDialog
      {...dialogState}
      onOpenChange={hideConfirm}
    />
  ), [dialogState, hideConfirm]);

  return {
    showConfirm,
    hideConfirm,
    setLoading,
    ConfirmDialog: ConfirmDialogComponent,
  };
}
