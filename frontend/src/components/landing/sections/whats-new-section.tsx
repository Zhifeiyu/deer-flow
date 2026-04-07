"use client";

import MagicBento, { type BentoCardProps } from "@/components/ui/magic-bento";
import { useI18n } from "@/core/i18n/hooks";
import { cn } from "@/lib/utils";

import { Section } from "../section";

const COLOR = "#0a0a0a";

export function WhatsNewSection({ className }: { className?: string }) {
  const { t } = useI18n();

  const features: BentoCardProps[] = [
    {
      color: COLOR,
      label: t.landing.whatsNewContextEngineering,
      title: t.landing.whatsNewMemory,
      description: t.landing.whatsNewMemoryDescription,
    },
    {
      color: COLOR,
      label: t.landing.whatsNewLongTask,
      title: t.landing.whatsNewPlanning,
      description: t.landing.whatsNewPlanningDescription,
    },
    {
      color: COLOR,
      label: t.landing.whatsNewExtensible,
      title: t.landing.whatsNewSkillsTools,
      description: t.landing.whatsNewSkillsToolsDescription,
    },
    {
      color: COLOR,
      label: t.landing.whatsNewPersistent,
      title: t.landing.whatsNewSandbox,
      description: t.landing.whatsNewSandboxDescription,
    },
    {
      color: COLOR,
      label: t.landing.whatsNewFlexible,
      title: t.landing.whatsNewMultiModel,
      description: t.landing.whatsNewMultiModelDescription,
    },
    {
      color: COLOR,
      label: t.landing.whatsNewFree,
      title: t.landing.whatsNewOpenSource,
      description: t.landing.whatsNewOpenSourceDescription,
    },
  ];

  return (
    <Section
      className={cn("", className)}
      title={t.landing.whatsNewTitle}
      subtitle={t.landing.whatsNewSubtitle}
    >
      <div className="flex w-full items-center justify-center">
        <MagicBento data={features} />
      </div>
    </Section>
  );
}
