import React from "react";
import { interpolate, useCurrentFrame } from "remotion";
import { out, backOut } from "../lib/anim";
import { C, F } from "../theme";
import { IconWarn } from "./Icons";

const clamp = { extrapolateLeft: "clamp", extrapolateRight: "clamp" } as const;

type Sub = { from: number; text: string };

/**
 * Legenda de passo (fora do celular, no topo do quadro).
 * `subs` troca a linha de apoio ao longo do passo.
 */
export const StepCaption: React.FC<{
  step: number;
  total?: number;
  title: string;
  subs: Sub[];
  duration: number;
  alert?: boolean;
}> = ({ step, total = 6, title, subs, duration, alert = false }) => {
  const frame = useCurrentFrame();
  const enter = interpolate(frame, [0, 14], [0, 1], { ...clamp, easing: out });
  const exit = interpolate(frame, [duration - 8, duration], [0, 1], clamp);
  const words = title.split(" ");
  const accent = alert ? C.yellow : "#7fd0ff";

  const subIndex = subs.reduce((acc, s, i) => (frame >= s.from ? i : acc), 0);
  const sub = subs[subIndex];
  const subIn = interpolate(frame, [sub.from + 2, sub.from + 12], [0, 1], { ...clamp, easing: out });

  return (
    <div
      style={{
        position: "absolute",
        left: 0,
        top: 0,
        width: 1080,
        height: 700,
        opacity: 1 - exit,
        transform: `translateY(${-30 * exit}px)`,
        zIndex: 20,
      }}
    >
      {/* véu para manter a legenda legível quando o celular está em zoom */}
      <div
        style={{
          position: "absolute",
          inset: 0,
          background: `linear-gradient(180deg, rgba(7,31,58,0.97) 0px, rgba(9,36,66,0.95) 560px, rgba(9,36,66,0) 700px)`,
          opacity: enter,
        }}
      />
      <div style={{ position: "absolute", left: 80, right: 80, top: 170, display: "flex", flexDirection: "column", alignItems: "flex-start" }}>
        <div
          style={{
            display: "flex",
            alignItems: "center",
            gap: 14,
            padding: "10px 26px 10px 18px",
            borderRadius: 40,
            background: alert ? C.yellow : "rgba(255,255,255,0.14)",
            border: alert ? "none" : "2px solid rgba(255,255,255,0.28)",
            color: alert ? "#1b1b1b" : "#fff",
            fontFamily: F.oswald,
            fontWeight: 600,
            fontSize: 38,
            letterSpacing: 2,
            opacity: enter,
            transform: `translateX(${(1 - enter) * -60}px) scale(${interpolate(frame, [0, 12], [0.7, 1], { ...clamp, easing: backOut })})`,
            transformOrigin: "0% 50%",
          }}
        >
          {alert ? (
            <IconWarn size={34} color="#1b1b1b" style={{ marginLeft: 4 }} />
          ) : (
            <div
              style={{
                width: 46,
                height: 46,
                borderRadius: 46,
                background: accent,
                color: C.oceanTop,
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                fontSize: 30,
                fontWeight: 700,
                letterSpacing: 0,
              }}
            >
              {step}
            </div>
          )}
          <span>{alert ? `STEP ${step} · DON'T SKIP IT` : `STEP ${step} OF ${total}`}</span>
        </div>
        <div style={{ marginTop: 22, display: "flex", flexWrap: "wrap", columnGap: 24, rowGap: 0 }}>
          {words.map((w, i) => {
            const p = interpolate(frame, [4 + i * 3, 18 + i * 3], [0, 1], { ...clamp, easing: out });
            return (
              <div key={i} style={{ overflow: "hidden", paddingBottom: 6 }}>
                <div
                  style={{
                    fontFamily: F.raleway,
                    fontWeight: 800,
                    fontSize: 92,
                    lineHeight: 1.04,
                    letterSpacing: -1.5,
                    color: alert && i === words.length - 1 ? C.yellow : alert && i === words.length - 2 ? C.yellow : "#fff",
                    transform: `translateY(${(1 - p) * 110}%)`,
                  }}
                >
                  {w}
                </div>
              </div>
            );
          })}
        </div>
        <div
          key={subIndex}
          style={{
            marginTop: 14,
            fontFamily: F.raleway,
            fontWeight: 600,
            fontSize: 46,
            lineHeight: 1.2,
            color: "rgba(255,255,255,0.92)",
            opacity: subIn,
            transform: `translateY(${(1 - subIn) * 16}px)`,
          }}
          dangerouslySetInnerHTML={{ __html: sub.text.replace(/\*(.+?)\*/g, `<span style="color:${accent}">$1</span>`) }}
        />
      </div>
      {/* progresso dos 6 passos */}
      <div style={{ position: "absolute", left: 80, top: 120, display: "flex", gap: 10, opacity: enter }}>
        {new Array(total).fill(0).map((_, i) => (
          <div
            key={i}
            style={{
              width: i + 1 === step ? 64 : 22,
              height: 8,
              borderRadius: 8,
              background: i + 1 <= step ? accent : "rgba(255,255,255,0.25)",
            }}
          />
        ))}
      </div>
    </div>
  );
};
