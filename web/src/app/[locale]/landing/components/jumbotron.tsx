// Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
// SPDX-License-Identifier: MIT

'use client';


import { ChevronRight } from "lucide-react";
import Link from "next/link";
import { useLanguage } from '~/contexts/language-context';

import { AuroraText } from "~/components/magicui/aurora-text";
import { FlickeringGrid } from "~/components/magicui/flickering-grid";
import { Button } from "~/components/ui/button";
import { env } from "~/env";

export function Jumbotron() {
  const { t } = useLanguage();

  return (
    <section className="flex h-[95vh] w-full flex-col items-center justify-center pb-15">
      <FlickeringGrid
        id="deer-hero-bg"
        className={`absolute inset-0 z-0 [mask-image:radial-gradient(800px_circle_at_center,white,transparent)]`}
        squareSize={4}
        gridGap={4}
        color="#60A5FA"
        maxOpacity={0.133}
        flickerChance={0.1}
      />
      <FlickeringGrid
        id="deer-hero"
        className="absolute inset-0 z-0 translate-y-[2vh] mask-[url(/images/deer-hero.svg)] mask-size-[100vw] mask-center mask-no-repeat md:mask-size-[72vh]"
        squareSize={3}
        gridGap={6}
        color="#60A5FA"
        maxOpacity={0.64}
        flickerChance={0.12}
      />
      <div className="relative z-10 flex flex-col items-center justify-center gap-12">
        <h1 className="text-center text-4xl font-bold md:text-6xl">
          <AuroraText>{t('landing.hero.title')}</AuroraText>
        </h1>
        <p className="max-w-4xl p-2 text-center text-sm opacity-85 md:text-2xl">
          {t('landing.hero.subtitle')}
        </p>
        <div className="flex gap-6">
          <Button className="text-lg md:w-42" size="lg" asChild>
            <Link href="/chat">
              {t('landing.hero.getStarted')} <ChevronRight />
            </Link>
          </Button>
        </div>
      </div>
      <div className="absolute bottom-8 flex text-xs opacity-50">
        <p>{t('landing.hero.deerStandsFor')}</p>
      </div>
    </section>
  );
}
