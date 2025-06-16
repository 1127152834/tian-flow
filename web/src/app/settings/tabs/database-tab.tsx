// Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
// SPDX-License-Identifier: MIT

import { Database } from "lucide-react";

import { DatabaseDatasourceManager } from "~/components/database/database-datasource-manager";

import type { Tab } from "./types";

export const DatabaseTab: Tab = () => {
  return (
    <div className="flex flex-col gap-4">
      <header>
        <h1 className="text-lg font-medium">Database Management</h1>
        <p className="text-sm text-muted-foreground">
          Manage database connections and data sources for Text2SQL and other features.
        </p>
      </header>
      <main>
        <DatabaseDatasourceManager />
      </main>
    </div>
  );
};

DatabaseTab.displayName = "Database";
DatabaseTab.icon = Database;
