import React from "react";
import { F } from "../theme";
import { IconBackspace, IconMic, IconShift, IconSmile, IconArrow } from "./Icons";
import { SCREEN_W } from "./Phone";

export const KEYBOARD_H = 300;

type Variant = "text" | "email" | "url" | "phone";

const ROWS = ["QWERTYUIOP", "ASDFGHJKL", "ZXCVBNM"];
const KEY_W = 33.2;
const KEY_H = 43;
const GAP_X = 5.6;
const ROW_Y = [56, 110, 164];
const BOTTOM_Y = 218;

const keyBase: React.CSSProperties = {
  position: "absolute",
  height: KEY_H,
  borderRadius: 6,
  background: "#6b6b6e",
  color: "#fff",
  display: "flex",
  alignItems: "center",
  justifyContent: "center",
  fontFamily: F.ui,
  boxShadow: "0 1px 0 rgba(0,0,0,0.6)",
};

const darkKey: React.CSSProperties = { ...keyBase, background: "#464648" };

/**
 * Teclado do iPhone (tema escuro, como no vídeo de referência).
 * `pressed` é o caractere que está sendo digitado neste frame (ou null).
 */
export const Keyboard: React.FC<{
  variant?: Variant;
  pressed?: string | null;
  suggestion?: string;
  returnLabel?: string;
  returnPressed?: boolean;
}> = ({ variant = "text", pressed = null, suggestion = "", returnLabel, returnPressed = false }) => {
  if (variant === "phone") return <PhonePad pressed={pressed} />;
  const p = pressed ? pressed.toUpperCase() : null;

  const keys: React.ReactNode[] = [];
  ROWS.forEach((row, r) => {
    const rowW = row.length * KEY_W + (row.length - 1) * GAP_X;
    const x0 = (SCREEN_W - rowW) / 2;
    row.split("").forEach((ch, i) => {
      const x = x0 + i * (KEY_W + GAP_X);
      const isP = p === ch;
      keys.push(
        <div key={ch} style={{ ...keyBase, left: x, top: ROW_Y[r], width: KEY_W, fontSize: 22, background: isP ? "#9a9a9e" : "#6b6b6e" }}>
          {ch}
        </div>,
      );
      if (isP) {
        keys.push(
          <div
            key={`${ch}-pop`}
            style={{
              position: "absolute",
              left: x - 9,
              top: ROW_Y[r] - 58,
              width: KEY_W + 18,
              height: 56,
              borderRadius: 10,
              background: "#7d7d81",
              color: "#fff",
              fontFamily: F.ui,
              fontSize: 34,
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              boxShadow: "0 6px 14px rgba(0,0,0,0.45)",
              zIndex: 5,
            }}
          >
            {ch}
          </div>,
        );
      }
    });
  });

  const bottom: { label: React.ReactNode; w: number; dark?: boolean; match?: string; blue?: boolean }[] =
    variant === "url"
      ? [
          { label: "123", w: 82, dark: true },
          { label: ".", w: 46, match: "." },
          { label: "/", w: 46, match: "/" },
          { label: ".com", w: 80, match: ".com" },
          { label: returnLabel ?? "go", w: 98, blue: true },
        ]
      : variant === "email"
        ? [
            { label: "123", w: 82, dark: true },
            { label: "space", w: 120, match: " " },
            { label: "@", w: 44, match: "@" },
            { label: ".", w: 44, match: "." },
            { label: returnLabel ?? <IconArrow dir="right" color="#fff" size={22} />, w: 64, blue: true },
          ]
        : [
            { label: "123", w: 82, dark: true },
            { label: "", w: 184, match: " " },
            { label: returnLabel ?? <IconArrow dir="right" color="#fff" size={22} />, w: 98, blue: true },
          ];
  const totalW = bottom.reduce((a, b) => a + b.w, 0) + (bottom.length - 1) * GAP_X;
  let bx = (SCREEN_W - totalW) / 2;

  return (
    <div
      style={{
        position: "absolute",
        left: 0,
        bottom: 0,
        width: SCREEN_W,
        height: KEYBOARD_H,
        background: "rgba(43,43,45,0.97)",
        borderTopLeftRadius: 22,
        borderTopRightRadius: 22,
        boxShadow: "0 -4px 18px rgba(0,0,0,0.25)",
      }}
    >
      {/* sugestões */}
      <div
        style={{
          position: "absolute",
          left: 0,
          top: 6,
          width: SCREEN_W,
          height: 40,
          display: "flex",
          alignItems: "center",
          fontFamily: F.ui,
          color: "#fff",
          fontSize: 16,
        }}
      >
        {[suggestion ? `“${suggestion}”` : "I", "The", "I'm"].map((s, i) => (
          <div
            key={i}
            style={{
              flex: 1,
              textAlign: "center",
              borderLeft: i ? "1px solid rgba(255,255,255,0.18)" : "none",
              whiteSpace: "nowrap",
              overflow: "hidden",
              textOverflow: "ellipsis",
              padding: "0 6px",
            }}
          >
            {s}
          </div>
        ))}
      </div>
      {keys}
      <div style={{ ...darkKey, left: 3, top: ROW_Y[2], width: 44 }}>
        <IconShift size={20} />
      </div>
      <div style={{ ...darkKey, left: SCREEN_W - 47, top: ROW_Y[2], width: 44 }}>
        <IconBackspace size={22} />
      </div>
      {bottom.map((b, i) => {
        const x = bx;
        bx += b.w + GAP_X;
        const isP = !!b.match && pressed === b.match;
        return (
          <div
            key={i}
            style={{
              ...(b.dark ? darkKey : keyBase),
              left: x,
              top: BOTTOM_Y,
              width: b.w,
              fontSize: typeof b.label === "string" && b.label.length > 2 ? 16 : 22,
              background: b.blue ? (returnPressed ? "#0a5bd6" : "#0a84ff") : isP ? "#9a9a9e" : b.dark ? "#464648" : "#6b6b6e",
            }}
          >
            {b.label}
          </div>
        );
      })}
      <div style={{ position: "absolute", left: 22, top: 270 }}>
        <IconSmile size={24} color="#c9c9cc" />
      </div>
      <div style={{ position: "absolute", right: 24, top: 268 }}>
        <IconMic size={24} color="#c9c9cc" />
      </div>
    </div>
  );
};

const PAD = [
  ["1", ""],
  ["2", "ABC"],
  ["3", "DEF"],
  ["4", "GHI"],
  ["5", "JKL"],
  ["6", "MNO"],
  ["7", "PQRS"],
  ["8", "TUV"],
  ["9", "WXYZ"],
  ["+*#", ""],
  ["0", ""],
  ["del", ""],
];

const PhonePad: React.FC<{ pressed: string | null }> = ({ pressed }) => (
  <div
    style={{
      position: "absolute",
      left: 0,
      bottom: 0,
      width: SCREEN_W,
      height: KEYBOARD_H,
      background: "rgba(43,43,45,0.97)",
      borderTopLeftRadius: 22,
      borderTopRightRadius: 22,
    }}
  >
    {PAD.map(([d, l], i) => {
      const col = i % 3;
      const row = Math.floor(i / 3);
      const w = 120;
      const x = 8 + col * (w + 7);
      const y = 12 + row * 56;
      const special = d === "+*#" || d === "del";
      const isP = pressed === d;
      return (
        <div
          key={d}
          style={{
            ...keyBase,
            left: x,
            top: y,
            width: w,
            height: 48,
            flexDirection: "column",
            background: special ? "transparent" : isP ? "#9a9a9e" : "#6b6b6e",
            boxShadow: special ? "none" : keyBase.boxShadow,
          }}
        >
          {d === "del" ? (
            <IconBackspace size={24} />
          ) : (
            <>
              <div style={{ fontSize: special ? 20 : 26, lineHeight: 1 }}>{d}</div>
              {l ? <div style={{ fontSize: 9.5, letterSpacing: 2, fontWeight: 600, marginTop: 1 }}>{l}</div> : null}
            </>
          )}
        </div>
      );
    })}
  </div>
);
