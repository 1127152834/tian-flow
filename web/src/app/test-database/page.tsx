// Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
// SPDX-License-Identifier: MIT

"use client";

import { DatabaseDatasourceManager } from "~/components/database/database-datasource-manager";

export default function TestDatabasePage() {
  return (
    <div className="container mx-auto py-8">
      <h1 className="text-3xl font-bold mb-8">Database Management Test</h1>
      <DatabaseDatasourceManager />
    </div>
  );
}
