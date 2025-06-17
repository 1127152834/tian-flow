// Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
// SPDX-License-Identifier: MIT

import { Database } from "lucide-react";

import { DatabaseDatasourceManager } from "~/components/database/database-datasource-manager";
import { useLanguage } from "~/contexts/language-context";

import type { Tab } from "./types";

export const DatabaseTab: Tab = () => {
  const { t } = useLanguage();

  return (
    <div className="flex flex-col gap-4">
      <header>
        <h1 className="text-lg font-medium">{t('settings.database.title')}</h1>
        <p className="text-sm text-muted-foreground">
          {t('settings.database.description')}
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
