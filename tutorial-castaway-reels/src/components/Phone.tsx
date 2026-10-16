import React from "react";
import { F } from "../theme";
import { StatusIcons } from "./Icons";

export const SCREEN_W = 390;
export const SCREEN_H = 844;
export const BEZEL = 13;
export const PHONE_W = SCREEN_W + BEZEL * 2;
export const PHONE_H = SCREEN_H + BEZEL * 2;

/** iPhone genérico em coordenadas lógicas (390 × 844). */
export const Phone: React.FC<{ children: React.ReactNode; style?: React.CSSProperties }> = ({ children, style }) => (
  <div
    style={{
      position: "absolute",
      left: 0,
      top: 0,
      width: PHONE_W,
      height: PHONE_H,
      borderRadius: 64,
      background: "linear-gradient(145deg, #3b3f46, #121418 40%, #2a2d33)",
      boxShadow: "0 40px 80px rgba(0,0,0,0.45), 0 0 0 1.5px #5b6068 inset, 0 0 0 4px #0b0c0e inset",
      ...style,
    }}
  >
    {/* botões laterais */}
    <div style={{ position: "absolute", left: -3, top: 170, width: 4, height: 34, borderRadius: 2, background: "#2a2d33" }} />
    <div style={{ position: "absolute", left: -3, top: 225, width: 4, height: 62, borderRadius: 2, background: "#2a2d33" }} />
    <div style={{ position: "absolute", left: -3, top: 300, width: 4, height: 62, borderRadius: 2, background: "#2a2d33" }} />
    <div style={{ position: "absolute", right: -3, top: 250, width: 4, height: 96, borderRadius: 2, background: "#2a2d33" }} />
    <div
      style={{
        position: "absolute",
        left: BEZEL,
        top: BEZEL,
        width: SCREEN_W,
        height: SCREEN_H,
        borderRadius: 52,
        overflow: "hidden",
        background: "#000",
        isolation: "isolate",
      }}
    >
      {children}
      {/* Dynamic Island */}
      <div
        style={{
          position: "absolute",
          left: (SCREEN_W - 122) / 2,
          top: 11,
          width: 122,
          height: 35,
          borderRadius: 20,
          background: "#000",
          zIndex: 100,
        }}
      />
    </div>
  </div>
);

export const StatusBar: React.FC<{ dark?: boolean }> = ({ dark = true }) => {
  const color = dark ? "#fff" : "#000";
  return (
    <div
      style={{
        position: "absolute",
        left: 0,
        top: 0,
        width: SCREEN_W,
        height: 50,
        background: dark ? "#000" : "transparent",
        display: "flex",
        alignItems: "center",
        justifyContent: "space-between",
        padding: "6px 30px 0 44px",
        boxSizing: "border-box",
        zIndex: 50,
      }}
    >
      <div style={{ fontFamily: F.ui, fontWeight: 600, fontSize: 16.5, color, letterSpacing: -0.2 }}>9:41</div>
      <StatusIcons color={color} />
    </div>
  );
};
