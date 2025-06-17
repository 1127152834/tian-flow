// Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
// SPDX-License-Identifier: MIT

import "~/styles/globals.css";

import { Geist } from "next/font/google";
import { ClientProviders } from "~/components/providers/client-providers";

const geist = Geist({
  subsets: ["latin"],
  variable: "--font-geist-sans",
});

export const metadata = {
  title: "DeerFlow - Deep Research at Your Fingertips",
  description: "Meet DeerFlow, your personal Deep Research assistant",
};

export default function RootLayout({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  return (
    <html className={`${geist.variable}`} suppressHydrationWarning>
      <body className="bg-app">
        <ClientProviders>
          {children}
        </ClientProviders>
      </body>
    </html>
  );
}
