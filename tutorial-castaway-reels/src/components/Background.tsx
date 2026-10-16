import React from "react";
import { AbsoluteFill, random, useCurrentFrame, useVideoConfig } from "remotion";
import { C } from "../theme";

const wavePath = (w: number, baseY: number, amp: number, len: number, phase: number, h: number) => {
  let d = `M 0 ${h} L 0 ${baseY}`;
  for (let x = 0; x <= w; x += 20) {
    const y = baseY + Math.sin((x / len) * Math.PI * 2 + phase) * amp + Math.sin((x / (len * 0.53)) * Math.PI * 2 - phase * 1.3) * amp * 0.35;
    d += ` L ${x} ${y.toFixed(1)}`;
  }
  return `${d} L ${w} ${h} Z`;
};

/** Fundo "oceano": degradê da marca, luz suave, partículas e ondas no rodapé (motivo do site). */
export const Background: React.FC<{ warm?: number }> = ({ warm = 0 }) => {
  const frame = useCurrentFrame();
  const { width, height } = useVideoConfig();
  const t = frame / 30;

  return (
    <AbsoluteFill style={{ background: `linear-gradient(180deg, ${C.oceanTop} 0%, ${C.oceanMid} 45%, ${C.oceanBottom} 100%)` }}>
      {/* luz que "respira" no alto */}
      <AbsoluteFill
        style={{
          background: `radial-gradient(ellipse 70% 38% at ${50 + Math.sin(t * 0.6) * 8}% 18%, rgba(91,182,232,0.42), rgba(91,182,232,0) 70%)`,
        }}
      />
      {/* tom quente para o momento do código de campanha */}
      <AbsoluteFill
        style={{
          opacity: warm,
          background: "radial-gradient(ellipse 80% 45% at 50% 40%, rgba(255,190,50,0.38), rgba(255,190,50,0) 70%)",
        }}
      />
      {/* partículas / bolhas */}
      {new Array(26).fill(0).map((_, i) => {
        const x = random(`bx${i}`) * width;
        const speed = 18 + random(`bs${i}`) * 40;
        const size = 4 + random(`bz${i}`) * 10;
        const y = height + 40 - ((t * speed + random(`by${i}`) * height * 1.2) % (height * 1.2));
        return (
          <div
            key={i}
            style={{
              position: "absolute",
              left: x + Math.sin(t * 1.3 + i) * 14,
              top: y,
              width: size,
              height: size,
              borderRadius: size,
              background: "rgba(255,255,255,0.9)",
              opacity: 0.08 + random(`bo${i}`) * 0.16,
            }}
          />
        );
      })}
      <svg width={width} height={height} style={{ position: "absolute", inset: 0 }}>
        <path d={wavePath(width, height - 250, 22, 620, t * 1.1, height)} fill="rgba(91,182,232,0.18)" />
        <path d={wavePath(width, height - 190, 18, 480, -t * 1.4 + 1, height)} fill="rgba(255,255,255,0.10)" />
        <path d={wavePath(width, height - 130, 14, 560, t * 1.7 + 2, height)} fill="rgba(255,255,255,0.10)" />
      </svg>
    </AbsoluteFill>
  );
};
