import React from "react";
import { useCurrentFrame, useVideoConfig } from "remotion";
import { COLORS, TEXTS, TIMING } from "../config";
import { appear, fade, sec } from "../anim";

/** Legenda visual fixa (fora do zoom) que nomeia cada teste — o vídeo funciona sem áudio. */
export const ChapterCaption: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const chapters = [
    { ...TEXTS.test1, from: TIMING.test1.start, to: TIMING.test2.start },
    { ...TEXTS.test2, from: TIMING.test2.start, to: TIMING.test3.start },
    { ...TEXTS.test3, from: TIMING.test3.start, to: TIMING.closing.start },
  ];
  return (
    <>
      {chapters.map((c) => {
        const from = sec(c.from, fps) + 4;
        const to = sec(c.to, fps) - 6;
        if (frame < from || frame > to + 8) return null;
        const { opacity, translate } = appear(frame, from, 12, 12);
        return (
          <div
            key={c.chapter}
            style={{
              position: "absolute",
              left: 40,
              bottom: 36,
              display: "flex",
              alignItems: "center",
              gap: 14,
              padding: "14px 22px",
              borderRadius: 14,
              backgroundColor: "rgba(255,255,255,0.97)",
              border: `1px solid ${COLORS.line}`,
              boxShadow: "0 10px 30px rgba(0,0,0,0.10)",
              fontSize: 22,
              color: COLORS.text,
              opacity: Math.min(opacity, fade(frame, to, to + 8, 1, 0)),
              translate,
            }}
          >
            <span
              style={{
                fontWeight: 700,
                color: COLORS.accent,
                letterSpacing: 0.3,
              }}
            >
              {c.chapter}
            </span>
            <span
              style={{ width: 1, height: 22, backgroundColor: COLORS.line }}
            />
            <span style={{ fontWeight: 500 }}>{c.chapterTitle}</span>
          </div>
        );
      })}
    </>
  );
};
