// Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
// SPDX-License-Identifier: MIT

import { type Metadata } from "next";
import Script from "next/script";
import { NextIntlClientProvider } from 'next-intl';
import { getMessages, getTranslations } from 'next-intl/server';
import { notFound } from 'next/navigation';

import { ThemeProviderWrapper } from "~/components/deer-flow/theme-provider-wrapper";
import { loadConfig } from "~/core/api/config";
import { env } from "~/env";
import { locales } from "~/i18n";

import { Toaster } from "../../components/deer-flow/toaster";

export async function generateMetadata({
  params
}: {
  params: Promise<{ locale: string }>;
}): Promise<Metadata> {
  const { locale } = await params;
  const t = await getTranslations({ locale, namespace: 'landing.hero' });

  return {
    title: "💡 Olight",
    description: t('subtitle'),
    icons: [{ rel: "icon", url: "/favicon.ico" }],
  };
}

export default async function LocaleLayout({
  children,
  params
}: Readonly<{
  children: React.ReactNode;
  params: Promise<{ locale: string }>;
}>) {
  const { locale } = await params;

  // Ensure that the incoming `locale` is valid
  if (!locales.includes(locale as any)) {
    notFound();
  }

  // Providing all messages to the client
  // side is the easiest way to get started
  const messages = await getMessages();
  const conf = await loadConfig();

  return (
    <html lang={locale} suppressHydrationWarning>
      <head>
        <script>{`window.__olightConfig = ${JSON.stringify(conf)}`}</script>
        {/* Define isSpace function globally to fix markdown-it issues with Next.js + Turbopack
          https://github.com/markdown-it/markdown-it/issues/1082#issuecomment-2749656365 */}
        <Script id="markdown-it-fix" strategy="beforeInteractive">
          {`
            if (typeof window !== 'undefined' && typeof window.isSpace === 'undefined') {
              window.isSpace = function(code) {
                return code === 0x20 || code === 0x09 || code === 0x0A || code === 0x0B || code === 0x0C || code === 0x0D;
              };
            }
          `}
        </Script>
      </head>
      <body>
        <NextIntlClientProvider messages={messages}>
          <ThemeProviderWrapper>{children}</ThemeProviderWrapper>
          <Toaster />
          {
            // NO USER BEHAVIOR TRACKING OR PRIVATE DATA COLLECTION BY DEFAULT
            //
            // When `NEXT_PUBLIC_STATIC_WEBSITE_ONLY` is `true`, the script will be injected
            // into the page only when `AMPLITUDE_API_KEY` is provided in `.env`
          }
          {env.NEXT_PUBLIC_STATIC_WEBSITE_ONLY && env.AMPLITUDE_API_KEY && (
            <>
              <Script src="https://cdn.amplitude.com/script/d2197dd1df3f2959f26295bb0e7e849f.js"></Script>
              <Script id="amplitude-init" strategy="lazyOnload">
                {`window.amplitude.init('${env.AMPLITUDE_API_KEY}', {"fetchRemoteConfig":true,"autocapture":true});`}
              </Script>
            </>
          )}
        </NextIntlClientProvider>
      </body>
    </html>
  );
}
