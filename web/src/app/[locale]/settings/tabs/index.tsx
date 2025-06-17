// Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
// SPDX-License-Identifier: MIT

import { Settings, type LucideIcon } from "lucide-react";

import { DatabaseTab } from "./database-tab";
import { GeneralTab } from "./general-tab";
import { MCPTab } from "./mcp-tab";
import Text2SQLTab from "./text2sql";
import { APIManagementTab } from "./api-management-tab";

// 创建一个函数来生成标签页配置，接受翻译函数作为参数
export const createSettingsTabs = (t: (key: string) => string) => [
  {
    id: "general",
    label: t('settings.tabs.general'),
    icon: GeneralTab.icon ?? Settings,
    component: GeneralTab,
  },
  {
    id: "database",
    label: t('settings.tabs.database'),
    icon: DatabaseTab.icon ?? Settings,
    component: DatabaseTab,
  },
  {
    id: "text2sql",
    label: t('settings.tabs.text2sql'),
    icon: Text2SQLTab.icon ?? Settings,
    component: Text2SQLTab,
  },
  {
    id: "apimanagement",
    label: t('settings.tabs.apiManagement'),
    icon: APIManagementTab.icon ?? Settings,
    component: APIManagementTab,
  },
  {
    id: "mcp",
    label: t('settings.tabs.mcp'),
    icon: MCPTab.icon ?? Settings,
    component: MCPTab,
  },
];

// 保持向后兼容的默认导出（使用英文标签）
export const SETTINGS_TABS = [GeneralTab, DatabaseTab, Text2SQLTab, APIManagementTab, MCPTab].map((tab) => {
  const name = tab.name ?? tab.displayName;
  return {
    ...tab,
    id: name.replace(/Tab$/, "").toLocaleLowerCase(),
    label: name.replace(/Tab$/, ""),
    icon: (tab.icon ?? <Settings />) as LucideIcon,
    component: tab,
  };
});
