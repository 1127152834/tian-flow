// Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
// SPDX-License-Identifier: MIT

"use client";


import dynamic from "next/dynamic";
import { Suspense } from "react";

import { Logo } from "~/components/deer-flow/logo";
import { ThemeToggle } from "~/components/deer-flow/theme-toggle";
import { LanguageSwitcher } from "~/components/deer-flow/language-switcher";
import { SettingsDialog } from "../[locale]/settings/dialogs/settings-dialog";
import { WebSocketStatus } from "~/components/websocket-status";

const Main = dynamic(() => import("../[locale]/chat/main"), {
  ssr: false,
  loading: () => (
    <div className="flex h-full w-full items-center justify-center">
      Loading Olight...
    </div>
  ),
});

export default function ChatPage() {
  return (
    <div className="flex h-screen w-screen justify-center overscroll-none">
      <header className="fixed top-0 left-0 flex h-12 w-full items-center justify-between px-4">
        <Logo />
        <div className="flex items-center gap-2">
          <WebSocketStatus />
          <LanguageSwitcher />
          <ThemeToggle />
          <Suspense>
            <SettingsDialog />
          </Suspense>
        </div>
      </header>
      <Main />
    </div>
  );
}
