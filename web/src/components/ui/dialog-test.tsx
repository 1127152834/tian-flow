// Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
// SPDX-License-Identifier: MIT

"use client";

import React from "react";
import { Button } from "~/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "~/components/ui/card";
import { useConfirmDialog } from "~/components/ui/confirm-dialog";
import { useSuccessDialog, useInfoDialog, useNotificationDialog } from "~/components/ui/success-dialog";

/**
 * Test component for dialog components
 * This component demonstrates the usage of various dialog types
 */
export function DialogTest() {
  const { showConfirm, ConfirmDialog } = useConfirmDialog();
  const { showSuccess, NotificationDialog: SuccessDialog } = useSuccessDialog();
  const { showInfo, NotificationDialog: InfoDialog } = useInfoDialog();
  const { showNotification, NotificationDialog } = useNotificationDialog();

  const handleDeleteTest = () => {
    showConfirm({
      title: "删除确认",
      description: "确定要删除这个测试项目吗？此操作不可撤销。",
      confirmText: "删除",
      cancelText: "取消",
      type: "danger",
      destructive: true,
      onConfirm: async () => {
        // Simulate async operation
        await new Promise(resolve => setTimeout(resolve, 1000));
        showSuccess(
          "删除成功",
          "测试项目已成功删除。",
          { autoClose: true, autoCloseDelay: 3000 }
        );
      }
    });
  };

  const handleWarningTest = () => {
    showConfirm({
      title: "重要操作",
      description: "这个操作将会影响系统性能，确定要继续吗？",
      confirmText: "继续",
      cancelText: "取消",
      type: "warning",
      onConfirm: () => {
        showInfo(
          "操作完成",
          "系统正在后台处理您的请求，请稍候。"
        );
      }
    });
  };

  const handleInfoTest = () => {
    showInfo(
      "系统信息",
      "当前系统运行正常，所有服务都在线。"
    );
  };

  const handleErrorTest = () => {
    showNotification({
      title: "操作失败",
      description: "网络连接超时，请检查您的网络设置后重试。",
      type: "error",
      confirmText: "知道了"
    });
  };

  const handleAutoCloseTest = () => {
    showSuccess(
      "自动关闭测试",
      "这个对话框将在3秒后自动关闭。",
      { autoClose: true, autoCloseDelay: 3000 }
    );
  };

  return (
    <div className="p-6 space-y-6">
      <Card>
        <CardHeader>
          <CardTitle>对话框组件测试</CardTitle>
          <CardDescription>
            测试各种类型的对话框组件，包括确认对话框、成功通知、信息提示等。
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <Button onClick={handleDeleteTest} variant="destructive">
              测试删除确认
            </Button>
            
            <Button onClick={handleWarningTest} variant="outline">
              测试警告确认
            </Button>
            
            <Button onClick={handleInfoTest} variant="default">
              测试信息提示
            </Button>
            
            <Button onClick={handleErrorTest} variant="secondary">
              测试错误提示
            </Button>
            
            <Button onClick={handleAutoCloseTest} variant="outline" className="col-span-2">
              测试自动关闭
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* All dialog components */}
      <ConfirmDialog />
      <SuccessDialog />
      <InfoDialog />
      <NotificationDialog />
    </div>
  );
}
