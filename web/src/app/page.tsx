// Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
// SPDX-License-Identifier: MIT

'use client';

import { useMemo } from "react";
import { useLanguage } from '~/contexts/language-context';

import { SiteHeader } from "./[locale]/chat/components/site-header";
import { Jumbotron } from "./[locale]/landing/components/jumbotron";
import { Ray } from "./[locale]/landing/components/ray";
import { CaseStudySection } from "./[locale]/landing/sections/case-study-section";
import { CoreFeatureSection } from "./[locale]/landing/sections/core-features-section";
import { JoinCommunitySection } from "./[locale]/landing/sections/join-community-section";
import { MultiAgentSection } from "./[locale]/landing/sections/multi-agent-section";

export default function HomePage() {
  return (
    <div className="flex flex-col items-center">
      <SiteHeader />
      <main className="container flex flex-col items-center justify-center gap-56">
        <Jumbotron />
        <CaseStudySection />
        <MultiAgentSection />
        <CoreFeatureSection />
        <JoinCommunitySection />
      </main>
      <Footer />
      <Ray />
    </div>
  );
}

function Footer() {
  const { t } = useLanguage();
  const year = useMemo(() => new Date().getFullYear(), []);

  return (
    <footer className="container mt-32 flex flex-col items-center justify-center">
      <hr className="from-border/0 via-border/70 to-border/0 m-0 h-px w-full border-none bg-gradient-to-r" />
      <div className="text-muted-foreground container flex h-20 flex-col items-center justify-center text-sm">
        <p className="text-center font-serif text-lg md:text-xl">
          &quot;{t('landing.footer.quote')}&quot;
        </p>
      </div>
      <div className="text-muted-foreground container mb-8 flex flex-col items-center justify-center text-xs">
        <p>{t('landing.footer.license')}</p>
        <p>{t('landing.footer.copyright', { year })}</p>
      </div>
    </footer>
  );
}
