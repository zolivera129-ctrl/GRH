import React from "react";
import { useCurrentFrame, useVideoConfig } from "remotion";
import { COLORS, TEXTS, TIMING } from "../config";
import { appear, fade, sec } from "../anim";

/** Cena 2 (3–9 s): o que a PATI faz + os três critérios perto do campo de conversa. */
export const Scene2WhatSheDoes: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const l1 = sec(TIMING.whatLine1, fps);
  const l2 = sec(TIMING.whatLine2, fps);
  const criteria = sec(TIMING.criteria, fps);
  const out = sec(TIMING.scrollToTest1, fps);

  return (
    <div
      style={{
        position: "absolute",
        inset: 0,
        opacity: fade(frame, out, out + 18, 1, 0),
      }}
    >
      <div
        style={{
          position: "absolute",
          inset: 0,
          paddingBottom: 60,
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          justifyContent: "center",
          gap: 22,
          textAlign: "center",
        }}
      >
        <div
          style={{
            fontSize: 44,
            fontWeight: 600,
            color: COLORS.text,
            letterSpacing: -0.6,
            ...appear(frame, l1, 16, 18),
          }}
        >
          {TEXTS.whatSheDoes.line1}
        </div>
        <div
          style={{
            fontSize: 44,
            fontWeight: 600,
            color: COLORS.accent,
            letterSpacing: -0.6,
            ...appear(frame, l2, 16, 18),
          }}
        >
          {TEXTS.whatSheDoes.line2}
        </div>
      </div>
      <div
        style={{
          position: "absolute",
          left: 0,
          right: 0,
          bottom: 18,
          display: "flex",
          justifyContent: "center",
          gap: 14,
        }}
      >
        {TEXTS.whatSheDoes.criteria.map((word, i) => (
          <div
            key={word}
            style={{
              padding: "10px 22px",
              borderRadius: 999,
              border: `1px solid ${COLORS.line}`,
              backgroundColor: COLORS.sidebar,
              fontSize: 24,
              fontWeight: 600,
              color: COLORS.accent,
              ...appear(frame, criteria + i * 12, 12, 12),
            }}
          >
            {word}
          </div>
        ))}
      </div>
    </div>
  );
};
