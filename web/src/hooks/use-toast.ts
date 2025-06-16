// Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
// SPDX-License-Identifier: MIT

"use client";

import { toast as sonnerToast } from "sonner";

interface ToastProps {
  title?: string;
  description?: string;
  variant?: "default" | "destructive";
  duration?: number;
}

export function useToast() {
  const toast = ({ title, description, variant = "default", duration }: ToastProps) => {
    const message = title || description || "";
    const desc = title && description ? description : undefined;

    if (variant === "destructive") {
      sonnerToast.error(message, {
        description: desc,
        duration,
      });
    } else {
      sonnerToast.success(message, {
        description: desc,
        duration,
      });
    }
  };

  return { toast };
}
