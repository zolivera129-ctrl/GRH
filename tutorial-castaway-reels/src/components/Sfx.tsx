import { Audio } from "@remotion/media";
import React from "react";
import { staticFile, useVideoConfig } from "remotion";

export type SfxName = "tap" | "key" | "pop" | "whoosh" | "success" | "impact" | "ding";
export type SfxEvent = { f: number; src: SfxName; vol?: number };

const LENGTH: Record<SfxName, number> = { tap: 0.2, key: 0.2, pop: 0.3, whoosh: 0.7, success: 1.4, impact: 1.2, ding: 0.6 };

/** Efeitos sonoros sintetizados (public/sfx), disparados nos frames da linha do tempo. */
export const Sfx: React.FC<{ events: SfxEvent[] }> = ({ events }) => {
  const { fps } = useVideoConfig();
  return (
    <>
      {events.map((e, i) => (
        <Audio
          key={`${e.src}-${e.f}-${i}`}
          name={`sfx ${e.src}`}
          src={staticFile(`sfx/${e.src}.wav`)}
          from={e.f}
          durationInFrames={Math.ceil(LENGTH[e.src] * fps)}
          volume={e.vol ?? 1}
          premountFor={fps}
        />
      ))}
    </>
  );
};

/** Um clique por caractere digitado (espaços não fazem som). */
export const keyClicks = (start: number, text: string, per: number, vol = 0.5): SfxEvent[] =>
  text
    .split("")
    .map((ch, i) => ({ ch, f: Math.round(start + i * per) }))
    .filter(({ ch }) => ch !== " ")
    .map(({ f }) => ({ f, src: "key" as const, vol }));
