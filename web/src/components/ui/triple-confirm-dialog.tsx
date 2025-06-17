// Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
// SPDX-License-Identifier: MIT

"use client";

import React, { useState } from "react";
import { AlertTriangle, X, CheckCircle } from "lucide-react";
import {
  AlertDialog,
  AlertDialogContent,
  AlertDialogHeader,
  AlertDialogTitle,
  AlertDialogDescription,
  AlertDialogFooter,
} from "~/components/ui/alert-dialog";
import { Button } from "~/components/ui/button";
import { Input } from "~/components/ui/input";
import { Label } from "~/components/ui/label";
import { Separator } from "~/components/ui/separator";

interface TripleConfirmDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  title: string;
  description: string;
  warningText: string;
  confirmationText: string;
  onConfirm: () => void | Promise<void>;
  loading?: boolean;
}

export function TripleConfirmDialog({
  open,
  onOpenChange,
  title,
  description,
  warningText,
  confirmationText,
  onConfirm,
  loading = false,
}: TripleConfirmDialogProps) {
  const [step, setStep] = useState(1);
  const [inputValue, setInputValue] = useState("");
  const [isProcessing, setIsProcessing] = useState(false);

  // 重置状态
  const resetDialog = () => {
    setStep(1);
    setInputValue("");
    setIsProcessing(false);
  };

  // 处理对话框关闭
  const handleClose = () => {
    if (!isProcessing && !loading) {
      resetDialog();
      onOpenChange(false);
    }
  };

  // 处理下一步
  const handleNext = () => {
    if (step < 3) {
      setStep(step + 1);
    }
  };

  // 处理上一步
  const handlePrevious = () => {
    if (step > 1) {
      setStep(step - 1);
    }
  };

  // 处理最终确认
  const handleFinalConfirm = async () => {
    if (inputValue.trim() !== confirmationText) {
      return;
    }

    setIsProcessing(true);
    try {
      await onConfirm();
      resetDialog();
      onOpenChange(false);
    } catch (error) {
      console.error("确认操作失败:", error);
    } finally {
      setIsProcessing(false);
    }
  };

  const renderStep1 = () => (
    <div className="space-y-4">
      <div className="flex items-center gap-3">
        <AlertTriangle className="h-6 w-6 text-red-500" />
        <div>
          <h3 className="text-lg font-semibold text-red-700">危险操作警告</h3>
          <p className="text-sm text-red-600">此操作具有不可逆的风险</p>
        </div>
      </div>
      
      <div className="bg-red-50 border border-red-200 rounded-lg p-4">
        <p className="text-sm text-red-800 leading-relaxed">
          {warningText}
        </p>
      </div>

      <div className="flex items-center gap-2 text-sm text-muted-foreground">
        <span className="bg-red-100 text-red-700 px-2 py-1 rounded text-xs font-medium">
          第 1 步 / 共 3 步
        </span>
        <span>请仔细阅读上述警告信息</span>
      </div>
    </div>
  );

  const renderStep2 = () => (
    <div className="space-y-4">
      <div className="flex items-center gap-3">
        <AlertTriangle className="h-6 w-6 text-orange-500" />
        <div>
          <h3 className="text-lg font-semibold text-orange-700">二次确认</h3>
          <p className="text-sm text-orange-600">请确认您了解操作后果</p>
        </div>
      </div>

      <div className="bg-orange-50 border border-orange-200 rounded-lg p-4">
        <h4 className="font-medium text-orange-800 mb-2">操作后果：</h4>
        <ul className="text-sm text-orange-700 space-y-1 list-disc list-inside">
          <li>所有资源向量数据将被清空</li>
          <li>需要重新进行向量化处理</li>
          <li>在重新向量化完成前，资源匹配功能将不可用</li>
          <li>此过程可能需要较长时间完成</li>
        </ul>
      </div>

      <div className="flex items-center gap-2 text-sm text-muted-foreground">
        <span className="bg-orange-100 text-orange-700 px-2 py-1 rounded text-xs font-medium">
          第 2 步 / 共 3 步
        </span>
        <span>确认您理解上述后果</span>
      </div>
    </div>
  );

  const renderStep3 = () => (
    <div className="space-y-4">
      <div className="flex items-center gap-3">
        <CheckCircle className="h-6 w-6 text-blue-500" />
        <div>
          <h3 className="text-lg font-semibold text-blue-700">最终确认</h3>
          <p className="text-sm text-blue-600">输入确认文本以继续</p>
        </div>
      </div>

      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
        <Label htmlFor="confirmation-input" className="text-sm font-medium text-blue-800">
          请输入以下文本以确认操作：
        </Label>
        <div className="mt-2 p-2 bg-blue-100 rounded border font-mono text-sm text-blue-900">
          {confirmationText}
        </div>
        <Input
          id="confirmation-input"
          value={inputValue}
          onChange={(e) => setInputValue(e.target.value)}
          placeholder="在此输入确认文本"
          className="mt-3"
          disabled={isProcessing || loading}
        />
      </div>

      <div className="flex items-center gap-2 text-sm text-muted-foreground">
        <span className="bg-blue-100 text-blue-700 px-2 py-1 rounded text-xs font-medium">
          第 3 步 / 共 3 步
        </span>
        <span>输入确认文本以执行操作</span>
      </div>
    </div>
  );

  return (
    <AlertDialog open={open} onOpenChange={handleClose}>
      <AlertDialogContent className="max-w-md">
        <AlertDialogHeader>
          <AlertDialogTitle className="flex items-center justify-between">
            {title}
            <Button
              variant="ghost"
              size="sm"
              onClick={handleClose}
              disabled={isProcessing || loading}
              className="h-6 w-6 p-0"
            >
              <X className="h-4 w-4" />
            </Button>
          </AlertDialogTitle>
          <AlertDialogDescription>
            {description}
          </AlertDialogDescription>
        </AlertDialogHeader>

        <div className="py-4">
          {step === 1 && renderStep1()}
          {step === 2 && renderStep2()}
          {step === 3 && renderStep3()}
        </div>

        <Separator />

        <AlertDialogFooter className="flex justify-between">
          <div className="flex gap-2">
            {step > 1 && (
              <Button
                variant="outline"
                onClick={handlePrevious}
                disabled={isProcessing || loading}
                size="sm"
              >
                上一步
              </Button>
            )}
          </div>

          <div className="flex gap-2">
            <Button
              variant="outline"
              onClick={handleClose}
              disabled={isProcessing || loading}
              size="sm"
            >
              取消
            </Button>
            
            {step < 3 ? (
              <Button
                onClick={handleNext}
                disabled={isProcessing || loading}
                size="sm"
              >
                下一步
              </Button>
            ) : (
              <Button
                onClick={handleFinalConfirm}
                disabled={
                  inputValue.trim() !== confirmationText || 
                  isProcessing || 
                  loading
                }
                className="bg-red-600 hover:bg-red-700 text-white"
                size="sm"
              >
                {isProcessing || loading ? "执行中..." : "确认执行"}
              </Button>
            )}
          </div>
        </AlertDialogFooter>
      </AlertDialogContent>
    </AlertDialog>
  );
}
