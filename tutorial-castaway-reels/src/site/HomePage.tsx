import React from "react";
import { Img, staticFile } from "remotion";
import { SCREEN_W } from "../components/Phone";
import { C, F } from "../theme";
import { HEADER_H } from "./SiteHeader";

/** Página inicial (abaixo do cabeçalho): foto do navio, faixa azul e onda. */
export const HomePage: React.FC = () => (
  <div style={{ position: "absolute", left: 0, top: HEADER_H, width: SCREEN_W, height: 900, background: C.page }}>
    <Img src={staticFile("img/hero.jpg")} style={{ position: "absolute", left: 0, top: 0, width: SCREEN_W, height: 240, objectFit: "cover" }} />
    <div style={{ position: "absolute", left: 0, top: 240, width: SCREEN_W, height: 200, background: C.brand }}>
      <div
        style={{
          position: "absolute",
          left: 0,
          right: 0,
          top: 42,
          textAlign: "center",
          fontFamily: F.raleway,
          fontWeight: 400,
          fontSize: 35,
          lineHeight: 1.2,
          color: "#fff",
        }}
      >
        TOP TALENT <span style={{ fontSize: 30 }}>To</span>
        <br />
        TOP EMPLOYERS
      </div>
    </div>
    <svg width={SCREEN_W} height={90} viewBox="0 0 390 90" style={{ position: "absolute", left: 0, top: 410 }}>
      <path d="M0 30 C60 0 120 60 195 34 C270 8 330 58 390 26 L390 90 L0 90 Z" fill="#8cc6ee" />
      <path d="M0 48 C70 22 130 74 205 48 C280 22 330 66 390 44 L390 90 L0 90 Z" fill="#d6ecfa" />
      <path d="M0 62 C80 40 140 86 215 62 C290 38 340 76 390 60 L390 90 L0 90 Z" fill={C.page} />
    </svg>
    <div
      style={{
        position: "absolute",
        left: 22,
        top: 520,
        fontFamily: F.raleway,
        fontWeight: 300,
        fontSize: 30,
        lineHeight: 1.18,
        color: C.heading,
      }}
    >
      CAST-A-WAY
      <br />
      CRUISE
      <br />
      TRANSFORM THE
      <br />
      WORLD!
    </div>
    {/* selo "Apply now" */}
    <div
      style={{
        position: "absolute",
        left: 320,
        top: 436,
        width: 54,
        height: 54,
        borderRadius: 54,
        background: C.sun,
        boxShadow: "0 3px 8px rgba(0,0,0,0.25)",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        fontFamily: F.oswald,
        fontWeight: 700,
        fontSize: 12,
        lineHeight: 1,
        textAlign: "center",
        color: "#7a3f00",
        transform: "rotate(-8deg)",
      }}
    >
      APPLY
      <br />
      NOW!
    </div>
  </div>
);
