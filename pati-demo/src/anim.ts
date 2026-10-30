import { Easing, interpolate } from "remotion";
import { LAYOUT } from "./config";

export const EASE_OUT = Easing.bezier(0.22, 1, 0.36, 1);
export const EASE_IN_OUT = Easing.bezier(0.65, 0, 0.35, 1);

const clamp = { extrapolateLeft: "clamp", extrapolateRight: "clamp" } as const;

/** Converte segundos absolutos em frame. */
export const sec = (s: number, fps: number) => Math.round(s * fps);

/** Entrada padrão das mensagens: fade + deslocamento vertical de 16 px. */
export const appear = (
  frame: number,
  start: number,
  duration = 12,
  distance = 16,
) => ({
  opacity: interpolate(frame, [start, start + duration], [0, 1], {
    ...clamp,
    easing: EASE_OUT,
  }),
  translate: `0px ${interpolate(frame, [start, start + duration], [distance, 0], { ...clamp, easing: EASE_OUT })}px`,
});

export const fade = (frame: number, from: number, to: number, a = 0, b = 1) =>
  interpolate(frame, [from, to], [a, b], { ...clamp, easing: EASE_OUT });

/** Interpola entre pares [frame, valor] com easing em cada trecho. */
export const piecewise = (
  frame: number,
  keys: [number, number][],
  easing = EASE_IN_OUT,
) => {
  if (frame <= keys[0][0]) return keys[0][1];
  for (let i = 1; i < keys.length; i++) {
    const [f0, v0] = keys[i - 1];
    const [f1, v1] = keys[i];
    if (frame <= f1) {
      if (f1 === f0) return v1;
      return interpolate(frame, [f0, f1], [v0, v1], { ...clamp, easing });
    }
  }
  return keys[keys.length - 1][1];
};

// Geometria derivada do layout (coordenadas do quadro, antes do zoom).
const W = LAYOUT.window;
export const GEO = (() => {
  const appTop = W.y + LAYOUT.chromeHeight;
  const appHeight = W.height - LAYOUT.chromeHeight;
  const mainLeft = W.x + LAYOUT.sidebarWidth;
  const mainWidth = W.width - LAYOUT.sidebarWidth;
  const columnLeftInMain = (mainWidth - LAYOUT.columnWidth) / 2;
  const columnLeft = mainLeft + columnLeftInMain;
  const composerZone =
    LAYOUT.composerIdleHeight + LAYOUT.composerBottom + LAYOUT.disclaimerHeight;
  const viewportTop = appTop + LAYOUT.headerHeight;
  const viewportHeight = appHeight - LAYOUT.headerHeight - composerZone;
  const composerBottomY =
    W.y + W.height - LAYOUT.disclaimerHeight - LAYOUT.composerBottom;
  const buttonsY = composerBottomY - 14 - 20;
  return {
    appTop,
    appHeight,
    mainLeft,
    mainWidth,
    columnLeftInMain,
    columnLeft,
    viewportTop,
    viewportHeight,
    plusButton: { x: columnLeft + 18 + 20, y: buttonsY },
    sendButton: { x: columnLeft + LAYOUT.columnWidth - 18 - 20, y: buttonsY },
  };
})();

/** Impede quebra de linha em palavras com hífen ("e-mail", "bem-estar"). */
export const nb = (text: string) =>
  text.replace(/(\S)-(\S)/g, "$1\u2060-\u2060$2");
