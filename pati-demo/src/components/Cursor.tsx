import React from "react";
import { interpolate, useCurrentFrame, useVideoConfig } from "remotion";
import { TIMING } from "../config";
import { EASE_IN_OUT, fade, GEO, sec } from "../anim";
import { PointerIcon } from "./Icons";

type Pass = {
  in: number;
  start: { x: number; y: number };
  clicks: { at: number; x: number; y: number }[];
};

/** Cursor realista: aparece só para anexar imagem e enviar mensagem. */
export const Cursor: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const { plusButton: plus, sendButton: send } = GEO;
  const passes: Pass[] = [
    {
      in: sec(TIMING.test1.cursorIn, fps),
      start: { x: 1180, y: 700 },
      clicks: [
        { at: sec(TIMING.test1.attachClick, fps), ...plus },
        { at: sec(TIMING.test1.sendClick, fps), ...send },
      ],
    },
    {
      in: sec(TIMING.test2.cursorIn, fps),
      start: { x: 1320, y: 760 },
      clicks: [{ at: sec(TIMING.test2.sendClick, fps), ...send }],
    },
    {
      in: sec(TIMING.test3.cursorIn, fps),
      start: { x: 1200, y: 720 },
      clicks: [
        { at: sec(TIMING.test3.attachClick, fps), ...plus },
        { at: sec(TIMING.test3.sendClick, fps), ...send },
      ],
    },
  ];

  const pass = passes.find(
    (p) => frame >= p.in && frame <= p.clicks[p.clicks.length - 1].at + 16,
  );
  if (!pass) return null;

  // posições: início -> cada clique (chega 2 frames antes do clique)
  const times = [pass.in, ...pass.clicks.map((c) => c.at - 2)];
  const xs = [pass.start.x, ...pass.clicks.map((c) => c.x)];
  const ys = [pass.start.y, ...pass.clicks.map((c) => c.y)];
  const seg = (vals: number[]) => {
    for (let i = 1; i < times.length; i++) {
      if (frame <= times[i]) {
        return interpolate(
          frame,
          [Math.max(times[i - 1] + 2, times[i] - 13), times[i]],
          [vals[i - 1], vals[i]],
          {
            extrapolateLeft: "clamp",
            extrapolateRight: "clamp",
            easing: EASE_IN_OUT,
          },
        );
      }
    }
    return vals[vals.length - 1];
  };
  const x = seg(xs);
  const y = seg(ys);
  const last = pass.clicks[pass.clicks.length - 1].at;
  const opacity = Math.min(
    fade(frame, pass.in, pass.in + 5),
    fade(frame, last + 6, last + 16, 1, 0),
  );
  const pressed = pass.clicks.some((c) => frame >= c.at && frame < c.at + 4);
  const ripple = pass.clicks.find((c) => frame >= c.at && frame < c.at + 12);

  return (
    <>
      {ripple ? (
        <div
          style={{
            position: "absolute",
            left: ripple.x,
            top: ripple.y,
            width: 56,
            height: 56,
            marginLeft: -28,
            marginTop: -28,
            borderRadius: 28,
            border: "2px solid rgba(31, 77, 58, 0.5)",
            scale: interpolate(frame - ripple.at, [0, 12], [0.4, 1.2]),
            opacity: interpolate(frame - ripple.at, [0, 12], [0.8, 0]),
          }}
        />
      ) : null}
      <div
        style={{
          position: "absolute",
          left: x - 3,
          top: y - 3,
          opacity,
          scale: pressed ? "0.88" : "1",
          transformOrigin: "3px 3px",
        }}
      >
        <PointerIcon />
      </div>
    </>
  );
};
