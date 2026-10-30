import "./fonts";
import React from "react";
import {
  AbsoluteFill,
  interpolate,
  staticFile,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import { Audio } from "@remotion/media";
import {
  ASSETS,
  CAMERA,
  COLORS,
  FONT_FAMILY,
  LAYOUT,
  TIMING,
  VOLUME,
} from "./config";
import { EASE_IN_OUT, EASE_OUT, fade, GEO, piecewise, sec } from "./anim";
import { BrowserWindow, Composer, Header, Sidebar } from "./components/Browser";
import { ChatLayout, ChatViewport } from "./components/ChatViewport";
import { Cursor } from "./components/Cursor";
import { ChapterCaption } from "./components/ChapterCaption";
import { Scene1Intro } from "./scenes/Scene1Intro";
import { Scene2WhatSheDoes } from "./scenes/Scene2WhatSheDoes";
import { Scene3Palestra } from "./scenes/Scene3Palestra";
import { Scene4Email } from "./scenes/Scene4Email";
import { Scene5Arte } from "./scenes/Scene5Arte";
import { Scene6Closing } from "./scenes/Scene6Closing";

/** Keyframes de scroll calculados a partir das posições medidas das mensagens. */
const makeScroll = (fps: number) => (layout: ChatLayout, frame: number) => {
  const pad = 28;
  const top = (id: string) => layout[id]?.top ?? 0;
  const bottom = (id: string) => top(id) + (layout[id]?.height ?? 0);
  const keys: [number, number][] = [[0, 0]];
  let current = 0;
  const go = (from: number, to: number, value: number) => {
    keys.push([sec(from, fps), current]);
    current = value;
    keys.push([sec(to, fps), current]);
  };
  // rola só o necessário para o bloco caber acima do composer
  const follow = (at: number, id: string) => {
    const target = bottom(id) - GEO.viewportHeight + 36;
    if (target > current + 1) go(at - 0.05, at + 0.55, target);
  };
  const t1 = TIMING.test1;
  const t2 = TIMING.test2;
  const t3 = TIMING.test3;

  go(TIMING.scrollToTest1, TIMING.scrollToTest1 + 1, top("t1") - pad);
  follow(t1.thinking, "t1-r1");
  follow(t1.reply2, "t1-r2");
  follow(t1.reco, "t1-reco");

  go(t2.start - 0.25, t2.start + 0.3, top("t2") - pad);
  follow(t2.thinking, "t2-r1");
  follow(t2.reply2, "t2-r2");
  follow(t2.solution, "t2-sol");

  go(t3.start - 0.25, t3.start + 0.3, top("t3") - pad);
  follow(t3.thinking, "t3-r1");
  follow(t3.reply2, "t3-r2");
  follow(t3.reco, "t3-reco");

  return piecewise(frame, keys, EASE_IN_OUT);
};

const W = LAYOUT.window;

export const PatiDemo: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps, width, height } = useVideoConfig();

  // câmera: zoom suave com foco limitado à janela do navegador
  const camKeys = (i: 1 | 2 | 3) =>
    CAMERA.map(([t, ...v]) => [sec(t, fps), v[i - 1]] as [number, number]);
  const s = piecewise(frame, camKeys(1));
  const limit = (v: number, lo: number, hi: number) =>
    lo > hi ? (lo + hi) / 2 : Math.min(hi, Math.max(lo, v));
  const fx = limit(
    piecewise(frame, camKeys(2)),
    W.x + width / 2 / s,
    W.x + W.width - width / 2 / s,
  );
  const fy = limit(
    piecewise(frame, camKeys(3)),
    W.y + height / 2 / s,
    W.y + W.height - height / 2 / s,
  );

  return (
    <AbsoluteFill
      style={{
        backgroundColor: COLORS.desk,
        fontFamily: FONT_FAMILY,
        color: COLORS.text,
      }}
    >
      <AbsoluteFill
        style={{
          transformOrigin: "0 0",
          translate: `${width / 2 - fx * s}px ${height / 2 - fy * s}px`,
          scale: String(s),
        }}
      >
        <BrowserWindow
          style={{
            opacity: fade(frame, 0, 16),
            translate: `0px ${(1 - EASE_OUT(Math.min(1, frame / 22))) * 40}px`,
          }}
        >
          <Sidebar />
          <div style={{ position: "relative", flex: 1 }}>
            <Header />
            <ChatViewport scrollAt={makeScroll(fps)}>
              <div
                data-anchor="intro"
                style={{ position: "relative", height: GEO.viewportHeight }}
              >
                <Scene1Intro />
                <Scene2WhatSheDoes />
              </div>
              <Scene3Palestra />
              <Scene4Email />
              <Scene5Arte />
            </ChatViewport>
            <Composer />
          </div>
        </BrowserWindow>
        <Cursor />
      </AbsoluteFill>

      <ChapterCaption />
      <Scene6Closing />

      {/* Áudio: trilha instrumental sintetizada + sons suaves de interface */}
      <Audio
        src={staticFile(ASSETS.music)}
        durationInFrames={sec(TIMING.closing.start + 0.6, fps)}
        volume={(f) =>
          VOLUME.music *
          interpolate(
            f,
            [
              0,
              sec(1.5, fps),
              sec(TIMING.test1.start, fps),
              sec(TIMING.closing.start - 0.4, fps),
              sec(TIMING.closing.start + 0.6, fps),
            ],
            [0, 0.75, 0.8, 1, 0],
            { extrapolateLeft: "clamp", extrapolateRight: "clamp" },
          )
        }
        premountFor={fps}
      />
      <Audio
        src={staticFile(ASSETS.musicEnd)}
        from={sec(TIMING.closing.start - 0.2, fps)}
        volume={VOLUME.music}
        premountFor={fps}
      />
      <Audio
        src={staticFile(ASSETS.sfxClick)}
        from={sec(TIMING.test1.attachClick, fps)}
        volume={VOLUME.click}
        premountFor={fps}
      />
      <Audio
        src={staticFile(ASSETS.sfxClick)}
        from={sec(TIMING.test1.sendClick, fps)}
        volume={VOLUME.click}
        premountFor={fps}
      />
      <Audio
        src={staticFile(ASSETS.sfxSend)}
        from={sec(TIMING.test1.send, fps)}
        volume={VOLUME.send}
        premountFor={fps}
      />
      <Audio
        src={staticFile(ASSETS.sfxReveal)}
        from={sec(TIMING.test1.reco, fps)}
        volume={VOLUME.reveal}
        premountFor={fps}
      />
      <Audio
        src={staticFile(ASSETS.sfxClick)}
        from={sec(TIMING.test2.sendClick, fps)}
        volume={VOLUME.click}
        premountFor={fps}
      />
      <Audio
        src={staticFile(ASSETS.sfxSend)}
        from={sec(TIMING.test2.send, fps)}
        volume={VOLUME.send}
        premountFor={fps}
      />
      <Audio
        src={staticFile(ASSETS.sfxReveal)}
        from={sec(TIMING.test2.solution, fps)}
        volume={VOLUME.reveal}
        premountFor={fps}
      />
      <Audio
        src={staticFile(ASSETS.sfxClick)}
        from={sec(TIMING.test3.attachClick, fps)}
        volume={VOLUME.click}
        premountFor={fps}
      />
      <Audio
        src={staticFile(ASSETS.sfxClick)}
        from={sec(TIMING.test3.sendClick, fps)}
        volume={VOLUME.click}
        premountFor={fps}
      />
      <Audio
        src={staticFile(ASSETS.sfxSend)}
        from={sec(TIMING.test3.send, fps)}
        volume={VOLUME.send}
        premountFor={fps}
      />
      <Audio
        src={staticFile(ASSETS.sfxReveal)}
        from={sec(TIMING.test3.reco, fps)}
        volume={VOLUME.reveal}
        premountFor={fps}
      />
    </AbsoluteFill>
  );
};
