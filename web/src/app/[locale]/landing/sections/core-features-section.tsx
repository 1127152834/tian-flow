// Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
// SPDX-License-Identifier: MIT

'use client';

import { Bird, Microscope, Podcast, Usb, User } from "lucide-react";
import { useLanguage } from '~/contexts/language-context';

import { BentoCard, BentoGrid } from "~/components/magicui/bento-grid";

import { SectionHeader } from "../components/section-header";

export function CoreFeatureSection() {
  const { t } = useLanguage();

  const features = [
    {
      Icon: Microscope,
      name: t('landing.coreFeatures.features.deeperResearch.name'),
      description: t('landing.coreFeatures.features.deeperResearch.description'),
      href: "https://github.com/bytedance/deer-flow/blob/main/src/tools",
      cta: t('landing.coreFeatures.learnMore'),
      background: (
        <img alt="background" className="absolute -top-20 -right-20 opacity-60" />
      ),
      className: "lg:col-start-1 lg:col-end-2 lg:row-start-1 lg:row-end-3",
    },
    {
      Icon: User,
      name: t('landing.coreFeatures.features.humanInLoop.name'),
      description: t('landing.coreFeatures.features.humanInLoop.description'),
      href: "https://github.com/bytedance/deer-flow/blob/main/src/graph/nodes.py",
      cta: t('landing.coreFeatures.learnMore'),
      background: (
        <img alt="background" className="absolute -top-20 -right-20 opacity-60" />
      ),
      className: "lg:col-start-1 lg:col-end-2 lg:row-start-3 lg:row-end-4",
    },
    {
      Icon: Bird,
      name: t('landing.coreFeatures.features.langStack.name'),
      description: t('landing.coreFeatures.features.langStack.description'),
      href: "https://www.langchain.com/",
      cta: t('landing.coreFeatures.learnMore'),
      background: (
        <img alt="background" className="absolute -top-20 -right-20 opacity-60" />
      ),
      className: "lg:col-start-2 lg:col-end-3 lg:row-start-1 lg:row-end-2",
    },
    {
      Icon: Usb,
      name: t('landing.coreFeatures.features.mcpIntegrations.name'),
      description: t('landing.coreFeatures.features.mcpIntegrations.description'),
      href: "https://github.com/bytedance/deer-flow/blob/main/src/graph/nodes.py",
      cta: t('landing.coreFeatures.learnMore'),
      background: (
        <img alt="background" className="absolute -top-20 -right-20 opacity-60" />
      ),
      className: "lg:col-start-2 lg:col-end-3 lg:row-start-2 lg:row-end-3",
    },
    {
      Icon: Podcast,
      name: t('landing.coreFeatures.features.podcastGeneration.name'),
      description: t('landing.coreFeatures.features.podcastGeneration.description'),
      href: "https://github.com/bytedance/deer-flow/blob/main/src/podcast",
      cta: t('landing.coreFeatures.learnMore'),
      background: (
        <img alt="background" className="absolute -top-20 -right-20 opacity-60" />
      ),
      className: "lg:col-start-2 lg:col-end-3 lg:row-start-3 lg:row-end-4",
    },
  ];

  return (
    <section className="relative flex w-full flex-col content-around items-center justify-center">
      <SectionHeader
        anchor="core-features"
        title={t('landing.coreFeatures.title')}
        description={t('landing.coreFeatures.description')}
      />
      <BentoGrid className="w-3/4 lg:grid-cols-2 lg:grid-rows-3">
        {features.map((feature) => (
          <BentoCard key={feature.name} {...feature} />
        ))}
      </BentoGrid>
    </section>
  );
}
