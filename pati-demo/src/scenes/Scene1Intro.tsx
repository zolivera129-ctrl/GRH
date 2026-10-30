import React from "react";
import { interpolate, useCurrentFrame, useVideoConfig } from "remotion";
import { COLORS, TEXTS, TIMING } from "../config";
import { appear, EASE_IN_OUT, fade, GEO, sec } from "../anim";
import { Avatar } from "../components/Messages";

/** Cena 1 (0–3 s): chat vazio com "Conheça a PATI"; o título sobe e se integra ao cabeçalho. */
export const Scene1Intro: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const title = sec(TIMING.introTitle, fps);
  const subtitle = sec(TIMING.introSubtitle, fps);
  const toHeader = sec(TIMING.introToHeader, fps);
  // distância do centro da área de conversa até o centro do cabeçalho
  const lift = GEO.viewportHeight / 2 + 32;

  return (
    <div
      style={{
        position: "absolute",
        inset: 0,
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "center",
        gap: 18,
        translate: `0px ${interpolate(
          frame,
          [toHeader, toHeader + 20],
          [0, -lift],
          {
            extrapolateLeft: "clamp",
            extrapolateRight: "clamp",
            easing: EASE_IN_OUT,
          },
        )}px`,
        scale: interpolate(frame, [toHeader, toHeader + 20], [1, 0.4], {
          extrapolateLeft: "clamp",
          extrapolateRight: "clamp",
          easing: EASE_IN_OUT,
        }),
        opacity: fade(frame, toHeader + 6, toHeader + 18, 1, 0),
      }}
    >
      <div style={{ ...appear(frame, title - 4, 14, 14) }}>
        <Avatar size={76} />
      </div>
      <div
        style={{
          fontSize: 68,
          fontWeight: 700,
          color: COLORS.text,
          letterSpacing: -1.2,
          ...appear(frame, title, 16, 18),
        }}
      >
        {TEXTS.intro.title}
      </div>
      <div
        style={{
          fontSize: 30,
          fontWeight: 500,
          color: COLORS.textSoft,
          ...appear(frame, subtitle, 16, 14),
        }}
      >
        {TEXTS.intro.subtitle}
      </div>
    </div>
  );
};
