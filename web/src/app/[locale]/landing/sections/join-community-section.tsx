// Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
// SPDX-License-Identifier: MIT

import { AuroraText } from "~/components/magicui/aurora-text";

import { SectionHeader } from "../components/section-header";

export function JoinCommunitySection() {
  return (
    <section className="flex w-full flex-col items-center justify-center pb-12">
      <SectionHeader
        anchor="join-community"
        title={
          <AuroraText colors={["#60A5FA", "#A5FA60", "#A560FA"]}>
            Join the Olight Community
          </AuroraText>
        }
        description="Contribute brilliant ideas to shape the future of Olight. Collaborate, innovate, and make impacts."
      />
    </section>
  );
}
