// Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
// SPDX-License-Identifier: MIT

"use client";

import * as React from "react";
import { CheckCircle, Info, AlertTriangle, XCircle } from "lucide-react";
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from "~/components/ui/alert-dialog";
import { cn } from "~/lib/utils";

export type NotificationDialogType = "success" | "info" | "warning" | "error";

interface NotificationDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  title: string;
  description: string;
  type?: NotificationDialogType;
  confirmText?: string;
  autoClose?: boolean;
  autoCloseDelay?: number;
}

const typeConfig = {
  success: {
    icon: CheckCircle,
    iconColor: "text-green-500",
    bgColor: "bg-green-50",
    borderColor: "border-green-200",
  },
  info: {
    icon: Info,
    iconColor: "text-blue-500",
    bgColor: "bg-blue-50",
    borderColor: "border-blue-200",
  },
  warning: {
    icon: AlertTriangle,
    iconColor: "text-amber-500",
    bgColor: "bg-amber-50",
    borderColor: "border-amber-200",
  },
  error: {
    icon: XCircle,
    iconColor: "text-red-500",
    bgColor: "bg-red-50",
    borderColor: "border-red-200",
  },
};

export function NotificationDialog({
  open,
  onOpenChange,
  title,
  description,
  type = "success",
  confirmText = "确定",
  autoClose = false,
  autoCloseDelay = 3000,
}: NotificationDialogProps) {
  const config = typeConfig[type];
  const Icon = config.icon;

  // Auto close functionality
  React.useEffect(() => {
    if (open && autoClose) {
      const timer = setTimeout(() => {
        onOpenChange(false);
      }, autoCloseDelay);

      return () => clearTimeout(timer);
    }
  }, [open, autoClose, autoCloseDelay, onOpenChange]);

  return (
    <AlertDialog open={open} onOpenChange={onOpenChange}>
      <AlertDialogContent className="w-96">
        <AlertDialogHeader>
          <div className={cn("flex items-center gap-3 p-3 rounded-lg", config.bgColor, config.borderColor, "border")}>
            <Icon className={cn("h-6 w-6", config.iconColor)} />
            <div className="flex-1">
              <AlertDialogTitle className="text-left text-base">
                {title}
              </AlertDialogTitle>
              <AlertDialogDescription className="text-left text-sm mt-1">
                {description}
              </AlertDialogDescription>
            </div>
          </div>
        </AlertDialogHeader>
        <AlertDialogFooter>
          <AlertDialogAction
            onClick={() => onOpenChange(false)}
            className={cn(
              type === "success" ? "bg-green-600 hover:bg-green-700" :
              type === "info" ? "bg-blue-600 hover:bg-blue-700" :
              type === "warning" ? "bg-amber-600 hover:bg-amber-700" :
              "bg-red-600 hover:bg-red-700"
            )}
          >
            {confirmText}
          </AlertDialogAction>
        </AlertDialogFooter>
      </AlertDialogContent>
    </AlertDialog>
  );
}

// Hook for easier usage
export function useNotificationDialog() {
  const [dialogState, setDialogState] = React.useState<{
    open: boolean;
    title: string;
    description: string;
    type?: NotificationDialogType;
    confirmText?: string;
    autoClose?: boolean;
    autoCloseDelay?: number;
  }>({
    open: false,
    title: "",
    description: "",
  });

  const showNotification = React.useCallback((options: {
    title: string;
    description: string;
    type?: NotificationDialogType;
    confirmText?: string;
    autoClose?: boolean;
    autoCloseDelay?: number;
  }) => {
    setDialogState({
      open: true,
      ...options,
    });
  }, []);

  const hideNotification = React.useCallback(() => {
    setDialogState(prev => ({ ...prev, open: false }));
  }, []);

  const NotificationDialogComponent = React.useCallback(() => (
    <NotificationDialog
      {...dialogState}
      onOpenChange={hideNotification}
    />
  ), [dialogState, hideNotification]);

  return {
    showNotification,
    hideNotification,
    NotificationDialog: NotificationDialogComponent,
  };
}

// Convenience functions
export function useSuccessDialog() {
  const { showNotification, NotificationDialog } = useNotificationDialog();
  
  const showSuccess = React.useCallback((title: string, description: string, options?: {
    confirmText?: string;
    autoClose?: boolean;
    autoCloseDelay?: number;
  }) => {
    showNotification({
      title,
      description,
      type: "success",
      ...options,
    });
  }, [showNotification]);

  return { showSuccess, NotificationDialog };
}

export function useInfoDialog() {
  const { showNotification, NotificationDialog } = useNotificationDialog();
  
  const showInfo = React.useCallback((title: string, description: string, options?: {
    confirmText?: string;
    autoClose?: boolean;
    autoCloseDelay?: number;
  }) => {
    showNotification({
      title,
      description,
      type: "info",
      ...options,
    });
  }, [showNotification]);

  return { showInfo, NotificationDialog };
}
