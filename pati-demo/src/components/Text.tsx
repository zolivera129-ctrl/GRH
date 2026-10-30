import React from "react";
import { interpolate } from "remotion";
import { COLORS } from "../config";
import { EASE_OUT } from "../anim";

/** Texto com trechos marcados por um fundo suave que "pinta" da esquerda para a direita. */
export const MarkedText: React.FC<{
  readonly text: string;
  readonly marks: { phrase: string; start: number }[];
  readonly frame: number;
}> = ({ text, marks, frame }) => {
  const parts: React.ReactNode[] = [];
  let rest = text;
  let key = 0;
  for (const { phrase, start } of marks) {
    const i = rest.indexOf(phrase);
    if (i < 0) continue;
    parts.push(rest.slice(0, i));
    const p = interpolate(frame, [start, start + 12], [0, 100], {
      extrapolateLeft: "clamp",
      extrapolateRight: "clamp",
      easing: EASE_OUT,
    });
    parts.push(
      <span
        key={key++}
        style={{
          backgroundImage: `linear-gradient(${COLORS.mark}, ${COLORS.mark})`,
          backgroundRepeat: "no-repeat",
          backgroundSize: `${p}% 100%`,
          boxDecorationBreak: "clone",
          WebkitBoxDecorationBreak: "clone",
          borderRadius: 4,
          padding: "1px 3px",
          margin: "0 -3px",
          color: p > 0 ? COLORS.text : undefined,
        }}
      >
        {phrase}
      </span>,
    );
    rest = rest.slice(i + phrase.length);
  }
  parts.push(rest);
  return <>{parts}</>;
};

/** Destaca palavras na cor da PATI, em negrito. */
export const Emphasis: React.FC<{
  readonly text: string;
  readonly words: string[];
}> = ({ text, words }) => {
  const tokens = text.split(/(\s+)/);
  return (
    <>
      {tokens.map((t, i) =>
        words.includes(t) ? (
          <span key={i} style={{ color: COLORS.accent, fontWeight: 700 }}>
            {t}
          </span>
        ) : (
          t
        ),
      )}
    </>
  );
};
