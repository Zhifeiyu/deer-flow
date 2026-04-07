"use client";

import { ChevronRightIcon } from "lucide-react";
import Link from "next/link";

import { Button } from "@/components/ui/button";
import { FlickeringGrid } from "@/components/ui/flickering-grid";
import Galaxy from "@/components/ui/galaxy";
import { WordRotate } from "@/components/ui/word-rotate";
import { useI18n } from "@/core/i18n/hooks";
import { cn } from "@/lib/utils";

export function Hero({ className }: { className?: string }) {
  const { t } = useI18n();
  return (
    <div
      className={cn(
        "flex size-full flex-col items-center justify-center",
        className,
      )}
    >
      <div className="absolute inset-0 z-0 bg-black/40">
        <Galaxy
          mouseRepulsion={false}
          starSpeed={0.2}
          density={0.6}
          glowIntensity={0.35}
          twinkleIntensity={0.3}
          speed={0.5}
        />
      </div>
      <FlickeringGrid
        className="absolute inset-0 z-0 translate-y-8 mask-[url(/images/deer.svg)] mask-size-[100vw] mask-center mask-no-repeat md:mask-size-[72vh]"
        squareSize={4}
        gridGap={4}
        color={"white"}
        maxOpacity={0.3}
        flickerChance={0.25}
      />
      <div className="container-md relative z-10 mx-auto flex h-screen flex-col items-center justify-center">
        <h1 className="flex items-center gap-2 text-4xl font-bold md:text-6xl">
          <WordRotate words={t.landing.heroWords} />{" "}
          <div>{t.landing.heroWithDeerFlow}</div>
        </h1>
        <p
          className="mt-8 scale-105 text-center text-2xl text-shadow-sm"
          style={{ color: "rgb(184,184,192)" }}
        >
          {t.landing.heroDescription.split("\n").map((line, i, arr) => (
            <span key={i}>
              {line}
              {i < arr.length - 1 && <br />}
            </span>
          ))}
        </p>
        <Link href="/workspace">
          <Button className="size-lg mt-8 scale-108" size="lg">
            <span className="text-md">{t.landing.heroGetStarted}</span>
            <ChevronRightIcon className="size-4" />
          </Button>
        </Link>
      </div>
    </div>
  );
}
