import React from "react";
import { AbsoluteFill, interpolate, useCurrentFrame } from "remotion";
import { Background } from "../components/Background";
import { IconHeart } from "../components/Icons";
import { Porthole } from "../components/Logo";
import { Sfx } from "../components/Sfx";
import { backOut, lerp, out } from "../lib/anim";
import { C, F } from "../theme";
import "../fonts";

export const HOOK_FRAMES = 105;

// Comentários como os do post (sem os @ das pessoas).
const BUBBLES = [
  { text: "How to apply?", x: 90, y: 520, rot: -3, at: 0, color: "#f4a261" },
  { text: "How do I apply??", x: 300, y: 720, rot: 2.5, at: 7, color: "#2a9d8f" },
  { text: "I am interested!", x: 120, y: 920, rot: -2, at: 14, color: "#e76f51" },
  { text: "Where do I apply?", x: 260, y: 1120, rot: 3, at: 21, color: "#8a5cf6" },
  { text: "How to apply?", x: 110, y: 1320, rot: -2.5, at: 28, color: "#3a86ff" },
];

const clamp = { extrapolateLeft: "clamp", extrapolateRight: "clamp" } as const;

export const Hook: React.FC = () => {
  const frame = useCurrentFrame();
  const away = lerp(frame, [44, 58], [0, 1]);
  const titleWords = [
    { t: "HOW TO", size: 150, color: "#fff", at: 52 },
    { t: "APPLY", size: 250, color: C.yellow, at: 57 },
  ];

  return (
    <AbsoluteFill style={{ overflow: "hidden" }}>
      <Background />

      {/* "Vocês perguntaram:" */}
      <div
        style={{
          position: "absolute",
          left: 90,
          top: 300,
          fontFamily: F.raleway,
          fontWeight: 800,
          fontSize: 76,
          color: "#fff",
          opacity: lerp(frame, [0, 6], [0, 1]) * (1 - away),
          transform: `translateY(${-away * 60}px)`,
        }}
      >
        You asked:
      </div>

      {BUBBLES.map((b, i) => {
        const p = lerp(frame, [b.at, b.at + 10], [0, 1], backOut);
        const like = lerp(frame, [b.at + 10, b.at + 16], [0, 1], backOut);
        return (
          <div
            key={i}
            style={{
              position: "absolute",
              left: b.x,
              top: b.y,
              display: "flex",
              alignItems: "center",
              gap: 22,
              padding: "22px 34px 22px 22px",
              borderRadius: 60,
              background: "#fff",
              boxShadow: "0 18px 40px rgba(0,0,0,0.3)",
              opacity: Math.min(1, p * 1.6) * (1 - away),
              transform: `rotate(${b.rot}deg) scale(${(0.6 + 0.4 * p) * (1 - away * 0.4)}) translate(${away * (540 - b.x - 300) * 0.6}px, ${away * -80}px)`,
              filter: `blur(${away * 8}px)`,
              transformOrigin: "0% 50%",
            }}
          >
            <div
              style={{
                width: 76,
                height: 76,
                borderRadius: 76,
                background: `linear-gradient(135deg, ${b.color}, #1d3557)`,
                boxShadow: "0 0 0 4px #fff, 0 0 0 7px #ee2a7b",
              }}
            />
            <div style={{ fontFamily: F.ui, fontWeight: 600, fontSize: 52, color: "#111", whiteSpace: "nowrap" }}>{b.text}</div>
            <IconHeart size={40} color="#ff3040" filled style={{ transform: `scale(${like})` }} />
          </div>
        );
      })}

      {/* título */}
      <div style={{ position: "absolute", left: 0, right: 0, top: 470, display: "flex", flexDirection: "column", alignItems: "center" }}>
        <div
          style={{
            opacity: lerp(frame, [46, 54], [0, 1]),
            transform: `scale(${lerp(frame, [46, 62], [0.3, 1], backOut)}) rotate(${interpolate(frame, [46, 70], [-200, 0], { ...clamp, easing: out })}deg)`,
          }}
        >
          <Porthole size={250} />
        </div>
        {titleWords.map((w) => {
          const p = lerp(frame, [w.at, w.at + 14], [0, 1], out);
          return (
            <div key={w.t} style={{ overflow: "hidden", marginTop: w.t === "APPLY" ? -36 : 18 }}>
              <div
                style={{
                  fontFamily: F.oswald,
                  fontWeight: 700,
                  fontSize: w.size,
                  lineHeight: 1.05,
                  color: w.color,
                  letterSpacing: 4,
                  transform: `translateY(${(1 - p) * 110}%)`,
                  textShadow: "0 8px 30px rgba(0,0,0,0.35)",
                }}
              >
                {w.t}
              </div>
            </div>
          );
        })}
        <div
          style={{
            marginTop: 6,
            fontFamily: F.raleway,
            fontWeight: 700,
            fontSize: 64,
            color: "#fff",
            opacity: lerp(frame, [64, 76], [0, 1]),
            transform: `translateY(${lerp(frame, [64, 76], [30, 0], out)}px)`,
          }}
        >
          at Cast-A-Way
        </div>
        <div
          style={{
            marginTop: 40,
            padding: "16px 36px",
            borderRadius: 60,
            background: "rgba(255,255,255,0.14)",
            border: "2px solid rgba(255,255,255,0.35)",
            fontFamily: F.raleway,
            fontWeight: 700,
            fontSize: 46,
            color: "#fff",
            opacity: lerp(frame, [72, 84], [0, 1]),
            transform: `scale(${lerp(frame, [72, 84], [0.7, 1], backOut)})`,
          }}
        >
          6 easy steps · on your phone
        </div>
      </div>

      <Sfx
        events={[
          ...BUBBLES.map((b) => ({ f: b.at, src: "pop" as const, vol: 0.55 })),
          { f: 44, src: "whoosh", vol: 0.7 },
          { f: 57, src: "impact", vol: 0.55 },
          { f: 72, src: "pop", vol: 0.4 },
        ]}
      />
    </AbsoluteFill>
  );
};
