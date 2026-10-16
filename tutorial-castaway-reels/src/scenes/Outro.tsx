import React from "react";
import { AbsoluteFill, interpolate, useCurrentFrame } from "remotion";
import { Background } from "../components/Background";
import { IconBookmark, IconSend, IconWarn } from "../components/Icons";
import { Porthole, Wordmark } from "../components/Logo";
import { Sfx } from "../components/Sfx";
import { backOut, lerp, out } from "../lib/anim";
import { C, COPY, F } from "../theme";
import "../fonts";

export const OUTRO_FRAMES = 120;

const clamp = { extrapolateLeft: "clamp", extrapolateRight: "clamp" } as const;

export const Outro: React.FC = () => {
  const frame = useCurrentFrame();
  const logo = lerp(frame, [0, 18], [0, 1], backOut);
  const fadeOut = lerp(frame, [OUTRO_FRAMES - 10, OUTRO_FRAMES], [0, 1]);

  const rise = (at: number) => ({
    opacity: lerp(frame, [at, at + 10], [0, 1]),
    transform: `translateY(${lerp(frame, [at, at + 14], [40, 0], out)}px)`,
  });

  return (
    <AbsoluteFill style={{ overflow: "hidden" }}>
      <Background />
      <AbsoluteFill style={{ alignItems: "center", opacity: 1 - fadeOut }}>
        <div style={{ marginTop: 360, transform: `scale(${logo})` }}>
          <Porthole size={300} spin={interpolate(frame, [0, 30], [-90, 0], { ...clamp, easing: out })} />
        </div>
        <div style={{ marginTop: 30, ...rise(8) }}>
          <Wordmark height={120} />
        </div>

        <div style={{ marginTop: 90, fontFamily: F.raleway, fontWeight: 700, fontSize: 52, color: "rgba(255,255,255,0.9)", ...rise(18) }}>Apply now at</div>
        <div
          style={{
            marginTop: 20,
            padding: "22px 48px",
            borderRadius: 80,
            background: "#fff",
            color: C.brand,
            fontFamily: F.ui,
            fontWeight: 700,
            fontSize: 72,
            boxShadow: "0 18px 50px rgba(0,0,0,0.35)",
            ...rise(24),
          }}
        >
          {COPY.site}
        </div>

        <div
          style={{
            marginTop: 70,
            display: "flex",
            alignItems: "center",
            gap: 22,
            padding: "24px 40px",
            borderRadius: 28,
            background: C.yellow,
            color: "#1b1b1b",
            fontFamily: F.raleway,
            fontWeight: 800,
            fontSize: 46,
            boxShadow: "0 18px 40px rgba(0,0,0,0.3)",
            opacity: lerp(frame, [36, 46], [0, 1]),
            transform: `scale(${lerp(frame, [36, 50], [0.6, 1], backOut)}) rotate(-1.5deg)`,
          }}
        >
          <IconWarn size={50} color="#1b1b1b" />
          Don&apos;t forget the campaign code!
        </div>

        <div style={{ marginTop: 80, display: "flex", gap: 60, ...rise(54) }}>
          {[
            { icon: <IconBookmark size={52} color="#fff" />, label: "Save this video" },
            { icon: <IconSend size={52} color="#fff" />, label: "Send it to a friend" },
          ].map((b) => (
            <div key={b.label} style={{ display: "flex", alignItems: "center", gap: 18, fontFamily: F.raleway, fontWeight: 700, fontSize: 40, color: "#fff" }}>
              {b.icon}
              {b.label}
            </div>
          ))}
        </div>
      </AbsoluteFill>
      <Sfx
        events={[
          { f: 0, src: "whoosh", vol: 0.6 },
          { f: 6, src: "pop", vol: 0.5 },
          { f: 36, src: "impact", vol: 0.45 },
        ]}
      />
    </AbsoluteFill>
  );
};
