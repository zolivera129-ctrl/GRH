import React from "react";
import { C, F } from "../theme";

/**
 * Releitura em vetor do logo da Cast-A-Way (escotilha com palmeira, mar e areia),
 * feita a partir do print do site. Se tiver o arquivo oficial, troque aqui.
 */
export const Porthole: React.FC<{ size: number; spin?: number; style?: React.CSSProperties }> = ({
  size,
  spin = 0,
  style,
}) => (
  <svg width={size} height={size} viewBox="0 0 100 100" style={{ display: "block", ...style }}>
    <defs>
      <clipPath id="porthole-inner">
        <circle cx="50" cy="50" r="38.5" />
      </clipPath>
    </defs>
    <g transform={`rotate(${spin} 50 50)`}>
      <circle cx="50" cy="50" r="49" fill="#fff" />
      <circle cx="50" cy="50" r="46.5" fill={C.ring} />
      {[
        [50, 7.6],
        [92.4, 50],
        [50, 92.4],
        [7.6, 50],
      ].map(([x, y]) => (
        <circle key={`${x}-${y}`} cx={x} cy={y} r="3.1" fill="#fff" />
      ))}
    </g>
    <circle cx="50" cy="50" r="40" fill="#fff" />
    <g clipPath="url(#porthole-inner)">
      <rect x="0" y="0" width="100" height="100" fill="#fff" />
      {/* mar */}
      <path d="M8 63 C22 61 36 64 47 71 C55 76 60 83 62 92 L8 92 Z" fill={C.sea} />
      {/* areia */}
      <path d="M44 92 C52 76 68 66 92 63 L92 92 Z" fill={C.sand} />
      {/* faixa branca entre mar e areia */}
      <path d="M41 92 C50 74 66 64 92 60.5 L92 63 C68 66 52 76 44 92 Z" fill="#fff" />
      {/* tronco */}
      <path d="M48.5 70 C50 58 50 46 45.5 33 L48.6 32.4 C53.8 45 54.5 58 53.2 70 Z" fill={C.palm} />
      {/* folhas */}
      <g fill={C.palm}>
        <path d="M46 32 C40 22 30 20 21 25 C29 24 36 26 41 31 C33 30 26 33 22 40 C29 35 37 34 45 35 Z" />
        <path d="M47 31 C49 21 56 15 67 15 C60 18 55 22 52 28 C59 24 67 24 73 29 C65 28 57 30 49 34 Z" />
        <path d="M47.5 33 C55 33 62 37 66 45 C60 41 54 39 48.5 37 Z" />
        <path d="M45 33 C39 38 36 45 37 52 C39 45 42 40 46.5 36 Z" />
        <path d="M46.5 30.5 C44 23 45 16 50 11 C48.6 17 48.6 23 49.5 30 Z" />
      </g>
    </g>
    <circle cx="50" cy="50" r="40" fill="none" stroke="#fff" strokeWidth="1.2" />
  </svg>
);

export const Wordmark: React.FC<{ height: number; color?: string; style?: React.CSSProperties }> = ({
  height,
  color = "#fff",
  style,
}) => (
  <div style={{ display: "flex", flexDirection: "column", justifyContent: "center", lineHeight: 1, color, ...style }}>
    <div
      style={{
        fontFamily: F.oswald,
        fontWeight: 600,
        fontSize: height * 0.68,
        letterSpacing: height * 0.005,
        lineHeight: 1,
        whiteSpace: "nowrap",
      }}
    >
      CAST·A·WAY
    </div>
    <div
      style={{
        fontFamily: F.oswald,
        fontWeight: 400,
        fontSize: height * 0.21,
        letterSpacing: height * 0.004,
        marginTop: height * 0.06,
        whiteSpace: "nowrap",
      }}
    >
      CRUISE &amp; RESORT HIRING AGENCY
    </div>
  </div>
);
