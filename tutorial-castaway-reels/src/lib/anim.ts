import { Easing, interpolate } from "remotion";

export const smooth = Easing.bezier(0.45, 0, 0.2, 1);
export const out = Easing.bezier(0.16, 1, 0.3, 1);
export const backOut = Easing.bezier(0.34, 1.56, 0.64, 1);

const clampOpts = { extrapolateLeft: "clamp", extrapolateRight: "clamp" } as const;

/** Interpolação com clamp nas duas pontas. */
export const lerp = (
  frame: number,
  input: [number, number],
  output: [number, number],
  easing: (t: number) => number = smooth,
) => interpolate(frame, input, output, { ...clampOpts, easing });

/**
 * Trilha de keyframes: [[frame, valor], ...]. Entre dois keyframes usa a curva
 * informada; antes do primeiro e depois do último, segura o valor.
 */
export const track = (
  frame: number,
  keys: [number, number][],
  easing: (t: number) => number = smooth,
) => {
  if (frame <= keys[0][0]) return keys[0][1];
  for (let i = 1; i < keys.length; i++) {
    const [f1, v1] = keys[i];
    const [f0, v0] = keys[i - 1];
    if (frame <= f1) {
      if (f1 === f0) return v1;
      return interpolate(frame, [f0, f1], [v0, v1], { ...clampOpts, easing });
    }
  }
  return keys[keys.length - 1][1];
};

/** Quantos caracteres já foram "digitados" a partir de `start`, com `perChar` frames por letra. */
export const typed = (frame: number, start: number, text: string, perChar = 3) => {
  if (frame < start) return "";
  const n = Math.min(text.length, Math.floor((frame - start) / perChar) + 1);
  return text.slice(0, n);
};

/** Frames em que cada letra é digitada (para o som e o destaque das teclas). */
export const typeFrames = (start: number, text: string, perChar = 3) =>
  text.split("").map((ch, i) => ({ ch, f: start + i * perChar }));

export const pulse = (frame: number, start: number, period = 30) =>
  frame < start ? 0 : 0.5 - 0.5 * Math.cos(((frame - start) / period) * Math.PI * 2);
