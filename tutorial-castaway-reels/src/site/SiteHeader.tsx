import React from "react";
import { Porthole, Wordmark } from "../components/Logo";
import { SCREEN_W } from "../components/Phone";
import { C } from "../theme";

export const HEADER_H = 96;
export const BURGER = { x: 337, y: 48 }; // centro do botão ☰ (coordenadas da página)

/** Cabeçalho azul do site. `menu` (0..1) transforma o ☰ em ✕. */
export const SiteHeader: React.FC<{ menu: number }> = ({ menu }) => {
  const bar = (i: number): React.CSSProperties => {
    const y = (i - 1) * 9;
    const rot = i === 1 ? 0 : (i === 0 ? 45 : -45) * menu;
    return {
      position: "absolute",
      left: 0,
      top: 11 + y * (1 - menu),
      width: 30,
      height: 3.2,
      borderRadius: 2,
      background: "#fff",
      transform: `rotate(${rot}deg)`,
      opacity: i === 1 ? 1 - menu : 1,
    };
  };
  return (
    <div style={{ position: "absolute", left: 0, top: 0, width: SCREEN_W, height: HEADER_H, background: C.brand }}>
      <div style={{ position: "absolute", left: 18, top: 9 }}>
        <Porthole size={80} />
      </div>
      <Wordmark height={40} style={{ position: "absolute", left: 108, top: 29 }} />
      <div style={{ position: "absolute", left: BURGER.x - 15, top: BURGER.y - 12, width: 30, height: 24 }}>
        {[0, 1, 2].map((i) => (
          <div key={i} style={bar(i)} />
        ))}
      </div>
    </div>
  );
};
