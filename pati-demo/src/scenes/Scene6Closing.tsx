import React from "react";
import { useCurrentFrame, useVideoConfig } from "remotion";
import { COLORS, TEXTS, TIMING } from "../config";
import { appear, fade, sec } from "../anim";

/**
 * Cena 6 (42–45 s): o chat se afasta e fica atrás de um véu leve, ainda legível como histórico
 * (lista de análises com check na lateral). A mensagem final entra num cartão sobre a interface.
 */
export const Scene6Closing: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const t = TIMING.closing;
  const start = sec(t.start, fps);
  if (frame < start) return null;
  const line1 = sec(t.line1, fps);
  const line2 = sec(t.line2, fps);
  return (
    <div style={{ position: "absolute", inset: 0 }}>
      <div
        style={{
          position: "absolute",
          inset: 0,
          backgroundColor: COLORS.veil,
          opacity: fade(frame, start, start + 14),
        }}
      />
      <div
        style={{
          position: "absolute",
          inset: 0,
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
        }}
      >
        <div
          style={{
            width: 1120,
            padding: "52px 64px 56px",
            borderRadius: 28,
            backgroundColor: "white",
            boxShadow:
              "0 30px 90px rgba(30, 28, 24, 0.18), 0 2px 10px rgba(30, 28, 24, 0.06)",
            display: "flex",
            flexDirection: "column",
            alignItems: "center",
            gap: 30,
            textAlign: "center",
            ...appear(frame, line1 - 4, 16, 20),
          }}
        >
          <div
            style={{
              fontSize: 58,
              fontWeight: 700,
              color: COLORS.text,
              letterSpacing: -1.2,
              lineHeight: 1.15,
              textWrap: "balance",
              ...appear(frame, line1, 14, 14),
            }}
          >
            {TEXTS.closing.line1}
          </div>
          <div
            style={{
              display: "flex",
              flexWrap: "wrap",
              justifyContent: "center",
              columnGap: 22,
              fontSize: 34,
              fontWeight: 600,
              color: COLORS.accent,
            }}
          >
            {TEXTS.closing.line2.map((part, i) => (
              <span
                key={part}
                style={{ ...appear(frame, line2 + i * 6, 12, 12) }}
              >
                {part}
              </span>
            ))}
          </div>
        </div>
      </div>
      <div
        style={{
          position: "absolute",
          right: 64,
          bottom: 40,
          fontSize: 22,
          fontWeight: 600,
          color: COLORS.textSoft,
          letterSpacing: 0.3,
          ...appear(frame, sec(t.signature, fps), 12, 8),
        }}
      >
        {TEXTS.closing.signature}
      </div>
    </div>
  );
};
