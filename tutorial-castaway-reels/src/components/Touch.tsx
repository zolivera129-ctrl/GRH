import React from "react";
import { interpolate } from "remotion";

const clamp = { extrapolateLeft: "clamp", extrapolateRight: "clamp" } as const;

/** Indicador de toque: o "dedo" aparece, pressiona e solta uma onda. Coordenadas da tela. */
export const Touch: React.FC<{ frame: number; at: number; x: number; y: number; size?: number }> = ({
  frame,
  at,
  x,
  y,
  size = 44,
}) => {
  const f = frame - at;
  if (f < -8 || f > 12) return null;
  const appear = interpolate(f, [-8, -2], [0, 1], clamp);
  const press = interpolate(f, [-2, 0, 3], [1, 0.78, 1], clamp);
  const fade = interpolate(f, [3, 10], [1, 0], clamp);
  const ripple = interpolate(f, [0, 12], [0, 1], clamp);
  return (
    <>
      <div
        style={{
          position: "absolute",
          left: x - size,
          top: y - size,
          width: size * 2,
          height: size * 2,
          borderRadius: size * 2,
          border: "2.5px solid rgba(255,255,255,0.95)",
          boxShadow: "0 0 0 2px rgba(20,90,160,0.35)",
          opacity: f >= 0 ? (1 - ripple) * 0.9 : 0,
          transform: `scale(${0.5 + ripple})`,
          zIndex: 90,
        }}
      />
      <div
        style={{
          position: "absolute",
          left: x - size / 2,
          top: y - size / 2,
          width: size,
          height: size,
          borderRadius: size,
          background: "rgba(255,255,255,0.55)",
          border: "2px solid rgba(255,255,255,0.95)",
          boxShadow: "0 4px 14px rgba(0,0,0,0.35), 0 0 0 3px rgba(44,130,200,0.45)",
          opacity: appear * fade,
          transform: `scale(${(0.6 + 0.4 * appear) * press})`,
          zIndex: 91,
        }}
      />
    </>
  );
};
