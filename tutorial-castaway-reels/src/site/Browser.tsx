import React from "react";
import { interpolate } from "remotion";
import { IconArrow, IconSearch, IconShare, IconTranslate } from "../components/Icons";
import { SCREEN_H, SCREEN_W, StatusBar } from "../components/Phone";
import { F } from "../theme";

export const STATUS_H = 50;
export const URLBAR_H = 50; // barra de endereço expandida
export const URLBAR_MINI = 22; // recolhida (só o domínio)
export const TOOLBAR_H = 70;

/** Topo do conteúdo da página, em função do quanto a barra está recolhida (0..1). */
export const contentTop = (collapse: number) => STATUS_H + interpolate(collapse, [0, 1], [URLBAR_H, URLBAR_MINI]);

/** "Chrome" do navegador em tema escuro, igual ao vídeo de referência. */
export const BrowserChrome: React.FC<{
  url: string;
  placeholder?: boolean;
  focused?: boolean;
  caret?: boolean;
  collapse: number;
  toolbar: number;
  progress?: number;
}> = ({ url, placeholder = false, focused = false, caret = false, collapse, toolbar, progress = 0 }) => {
  const barH = interpolate(collapse, [0, 1], [URLBAR_H, URLBAR_MINI]);
  return (
    <>
      <StatusBar dark />
      <div
        style={{
          position: "absolute",
          left: 0,
          top: STATUS_H,
          width: SCREEN_W,
          height: barH,
          background: "#000",
          zIndex: 45,
          overflow: "hidden",
        }}
      >
        {/* pílula expandida */}
        <div
          style={{
            position: "absolute",
            left: 10,
            right: 10,
            top: 5,
            height: 38,
            borderRadius: 13,
            background: focused ? "#3a3a3d" : "#2b2b2d",
            border: focused ? "2px solid #0a84ff" : "2px solid transparent",
            boxSizing: "border-box",
            display: "flex",
            alignItems: "center",
            padding: "0 12px",
            gap: 10,
            opacity: 1 - collapse,
          }}
        >
          {focused ? <IconSearch size={16} color="#9a9aa0" /> : <IconTranslate size={18} color="#c9c9cc" />}
          <div
            style={{
              flex: 1,
              textAlign: focused ? "left" : "center",
              fontFamily: F.ui,
              fontSize: 16,
              color: placeholder ? "#8e8e93" : "#fff",
              whiteSpace: "nowrap",
              display: "flex",
              justifyContent: focused ? "flex-start" : "center",
              alignItems: "center",
            }}
          >
            {url}
            {caret ? <span style={{ display: "inline-block", width: 2, height: 20, background: "#0a84ff", marginLeft: 1 }} /> : null}
          </div>
          {focused ? null : <IconShare size={18} color="#c9c9cc" />}
        </div>
        {/* domínio pequeno (recolhida) */}
        <div
          style={{
            position: "absolute",
            left: 0,
            right: 0,
            top: 2,
            textAlign: "center",
            fontFamily: F.ui,
            fontSize: 12.5,
            color: "#fff",
            opacity: collapse,
          }}
        >
          {url}
        </div>
        {progress > 0 && progress < 1 ? (
          <div style={{ position: "absolute", left: 10, bottom: 0, height: 3, width: (SCREEN_W - 20) * progress, background: "#0a84ff", borderRadius: 2 }} />
        ) : null}
      </div>
      {/* barra de ferramentas inferior */}
      <div
        style={{
          position: "absolute",
          left: 0,
          top: SCREEN_H - TOOLBAR_H * toolbar,
          width: SCREEN_W,
          height: TOOLBAR_H,
          background: "#1c1c1e",
          zIndex: 45,
          display: "flex",
          justifyContent: "space-around",
          alignItems: "flex-start",
          paddingTop: 12,
          boxSizing: "border-box",
        }}
      >
        <IconArrow dir="left" color="#fff" size={22} />
        <IconArrow dir="right" color="#fff" size={22} />
        <div style={{ width: 26, height: 26, borderRadius: 26, background: "#8e8e93", color: "#1c1c1e", fontSize: 22, lineHeight: "26px", textAlign: "center", fontFamily: F.ui }}>
          +
        </div>
        <div style={{ width: 20, height: 20, borderRadius: 5, border: "2px solid #fff" }} />
        <div style={{ color: "#fff", fontSize: 22, lineHeight: "16px", fontFamily: F.ui, letterSpacing: 1 }}>•••</div>
        <div style={{ position: "absolute", left: (SCREEN_W - 134) / 2, bottom: 8, width: 134, height: 5, borderRadius: 3, background: "#fff" }} />
      </div>
    </>
  );
};
