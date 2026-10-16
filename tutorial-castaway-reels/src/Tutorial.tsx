import { TransitionSeries, linearTiming } from "@remotion/transitions";
import { fade } from "@remotion/transitions/fade";
import { Audio } from "@remotion/media";
import React from "react";
import { AbsoluteFill, staticFile, useVideoConfig } from "remotion";
import { HOOK_FRAMES, Hook } from "./scenes/Hook";
import { OUTRO_FRAMES, Outro } from "./scenes/Outro";
import { WALKTHROUGH_FRAMES, Walkthrough } from "./scenes/Walkthrough";

const T_IN = 12;
const T_OUT = 15;
export const TUTORIAL_FRAMES =
  HOOK_FRAMES + WALKTHROUGH_FRAMES + OUTRO_FRAMES - T_IN - T_OUT;

// Volume da trilha: fica abaixo dos toques e teclas, que contam a história.
const MUSIC_VOLUME = 0.32;

/** Reels completo: gancho → navegação no site → encerramento, com trilha original. */
export const Tutorial: React.FC = () => {
  const { fps } = useVideoConfig();
  return (
    <AbsoluteFill>
      <TransitionSeries>
        <TransitionSeries.Sequence
          name="Hook"
          durationInFrames={HOOK_FRAMES}
          premountFor={fps}
        >
          <Hook />
        </TransitionSeries.Sequence>
        <TransitionSeries.Transition
          presentation={fade()}
          timing={linearTiming({ durationInFrames: T_IN })}
        />
        <TransitionSeries.Sequence
          name="Walkthrough"
          durationInFrames={WALKTHROUGH_FRAMES}
          premountFor={fps}
        >
          <Walkthrough />
        </TransitionSeries.Sequence>
        <TransitionSeries.Transition
          presentation={fade()}
          timing={linearTiming({ durationInFrames: T_OUT })}
        />
        <TransitionSeries.Sequence
          name="Outro"
          durationInFrames={OUTRO_FRAMES}
          premountFor={fps}
        >
          <Outro />
        </TransitionSeries.Sequence>
      </TransitionSeries>
      {/* gerada por scripts/make_music.py, com compassos presos à linha do tempo */}
      <Audio
        name="Trilha"
        src={staticFile("music/castaway-tropical.m4a")}
        volume={MUSIC_VOLUME}
      />
    </AbsoluteFill>
  );
};
