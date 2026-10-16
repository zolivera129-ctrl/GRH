import React from "react";

type P = { size?: number; color?: string; style?: React.CSSProperties };

const svg = (size: number, children: React.ReactNode, style?: React.CSSProperties, vb = "0 0 24 24") => (
  <svg width={size} height={size} viewBox={vb} style={{ display: "block", flexShrink: 0, ...style }}>
    {children}
  </svg>
);

export const IconUser: React.FC<P> = ({ size = 16, color = "#333", style }) =>
  svg(
    size,
    <>
      <circle cx="12" cy="7" r="4.6" fill={color} />
      <path d="M3 22c0-5 4-8.5 9-8.5s9 3.5 9 8.5z" fill={color} />
    </>,
    style,
  );

export const IconUserCheck: React.FC<P> = ({ size = 16, color = "#333", style }) =>
  svg(
    size,
    <>
      <circle cx="9" cy="7" r="4.3" fill={color} />
      <path d="M1 21c0-4.6 3.6-7.8 8-7.8s8 3.2 8 7.8z" fill={color} />
      <path d="M15.5 11.5l2.3 2.3 4.7-5" stroke={color} strokeWidth="2.4" fill="none" strokeLinecap="round" />
    </>,
    style,
  );

export const IconGlobe: React.FC<P> = ({ size = 16, color = "#333", style }) =>
  svg(
    size,
    <>
      <circle cx="12" cy="12" r="10" fill={color} />
      <path
        d="M7 5.5c1.5 1 1 2.5 2.5 3s2.5-.5 3 1-1.5 2-1 3.5 2 1 2 2.5-1 2.5-.5 4.5M15.5 3.5c-.5 1.2.5 2 1.8 2.3s2.2 1.7 1.7 3"
        stroke="#fff"
        strokeWidth="1.5"
        fill="none"
        strokeLinecap="round"
      />
    </>,
    style,
  );

export const IconMail: React.FC<P> = ({ size = 16, color = "#333", style }) =>
  svg(
    size,
    <>
      <rect x="2" y="5" width="20" height="14" rx="2" fill={color} />
      <path d="M3 6.5l9 6.5 9-6.5" stroke="#fff" strokeWidth="1.7" fill="none" />
    </>,
    style,
  );

export const IconPhone: React.FC<P> = ({ size = 16, color = "#333", style }) =>
  svg(
    size,
    <>
      <rect x="2" y="2" width="20" height="20" rx="3" fill={color} />
      <path
        d="M8.2 6.5l1.6 2.6-1.2 1.2c.8 1.8 2.3 3.3 4.1 4.1l1.2-1.2 2.6 1.6-.8 2.2c-4.7-.3-8.6-4.2-8.9-8.9z"
        fill="#fff"
      />
    </>,
    style,
  );

export const IconChevronDown: React.FC<P> = ({ size = 16, color = "#333", style }) =>
  svg(size, <path d="M5 9l7 7 7-7" stroke={color} strokeWidth="2.6" fill="none" strokeLinecap="round" strokeLinejoin="round" />, style);

export const IconCheck: React.FC<P & { stroke?: number }> = ({ size = 16, color = "#333", style, stroke = 3 }) =>
  svg(size, <path d="M4.5 12.5l5 5L19.5 7" stroke={color} strokeWidth={stroke} fill="none" strokeLinecap="round" strokeLinejoin="round" />, style);

export const IconUpload: React.FC<P> = ({ size = 16, color = "#333", style }) =>
  svg(
    size,
    <>
      <path d="M12 3l6 6h-4v6h-4V9H6z" fill={color} />
      <path d="M4 15v5h16v-5" stroke={color} strokeWidth="2.4" fill="none" />
    </>,
    style,
  );

export const IconFile: React.FC<P> = ({ size = 16, color = "#333", style }) =>
  svg(
    size,
    <>
      <path d="M5 2h9l5 5v15H5z" fill={color} />
      <path d="M14 2v5h5" fill="#fff" opacity=".45" />
      <text x="12" y="17.5" fontSize="5.6" fontWeight="700" fill="#fff" textAnchor="middle" fontFamily="Inter">
        PDF
      </text>
    </>,
    style,
  );

export const IconBriefcase: React.FC<P> = ({ size = 16, color = "#333", style }) =>
  svg(
    size,
    <>
      <path d="M9 6V4.5A1.5 1.5 0 0 1 10.5 3h3A1.5 1.5 0 0 1 15 4.5V6" stroke={color} strokeWidth="2" fill="none" />
      <rect x="2.5" y="6" width="19" height="14" rx="2.5" fill={color} />
      <rect x="2.5" y="11" width="19" height="1.8" fill="#fff" opacity=".5" />
    </>,
    style,
  );

export const IconTarget: React.FC<P> = ({ size = 16, color = "#333", style }) =>
  svg(
    size,
    <>
      <circle cx="12" cy="12" r="9.5" stroke={color} strokeWidth="2.4" fill="none" />
      <circle cx="12" cy="12" r="5.5" stroke={color} strokeWidth="2.4" fill="none" />
      <circle cx="12" cy="12" r="2" fill={color} />
    </>,
    style,
  );

export const IconBolt: React.FC<P> = ({ size = 16, color = "#333", style }) =>
  svg(size, <path d="M13.5 2L4 13.5h6.5L9 22l10-12h-6.6z" fill={color} />, style);

export const IconEye: React.FC<P> = ({ size = 16, color = "#333", style }) =>
  svg(
    size,
    <>
      <path d="M1.5 12S5.5 4.5 12 4.5 22.5 12 22.5 12 18.5 19.5 12 19.5 1.5 12 1.5 12z" fill={color} />
      <circle cx="12" cy="12" r="4.2" fill="#fff" />
      <circle cx="12" cy="12" r="2.2" fill={color} />
    </>,
    style,
  );

export const IconBookmark: React.FC<P> = ({ size = 16, color = "#333", style }) =>
  svg(size, <path d="M6 2.5h12v19l-6-4.6-6 4.6z" stroke={color} strokeWidth="2.2" fill="none" strokeLinejoin="round" />, style);

export const IconSend: React.FC<P> = ({ size = 16, color = "#333", style }) =>
  svg(
    size,
    <path d="M22 2.5L2.5 10l7.8 3.2L22 2.5 13.4 21.5l-3.1-8.3" stroke={color} strokeWidth="2.1" fill="none" strokeLinejoin="round" />,
    style,
  );

export const IconHeart: React.FC<P & { filled?: boolean }> = ({ size = 16, color = "#333", style, filled }) =>
  svg(
    size,
    <path
      d="M12 21s-8.5-5.2-8.5-11.3A4.7 4.7 0 0 1 12 6.9a4.7 4.7 0 0 1 8.5 2.8C20.5 15.8 12 21 12 21z"
      fill={filled ? color : "none"}
      stroke={color}
      strokeWidth="2"
    />,
    style,
  );

export const IconWarn: React.FC<P> = ({ size = 16, color = "#333", style }) =>
  svg(
    size,
    <>
      <path d="M12 2.5L23 21.5H1z" fill={color} />
      <rect x="10.8" y="9" width="2.4" height="7" rx="1.2" fill="#1b1b1b" />
      <circle cx="12" cy="18.6" r="1.4" fill="#1b1b1b" />
    </>,
    style,
  );

// Ícones da barra de status / navegador
export const StatusIcons: React.FC<{ color: string }> = ({ color }) => (
  <div style={{ display: "flex", alignItems: "center", gap: 6 }}>
    <svg width="18" height="12" viewBox="0 0 18 12">
      {[0, 1, 2, 3].map((i) => (
        <rect key={i} x={i * 4.6} y={9 - i * 2.8} width="3.2" height={3 + i * 2.8} rx="1" fill={color} />
      ))}
    </svg>
    <svg width="17" height="12" viewBox="0 0 17 12">
      <path d="M8.5 11.5l2.4-2.9a3.6 3.6 0 0 0-4.8 0z" fill={color} />
      <path d="M3.9 6.4a7 7 0 0 1 9.2 0l-1.4 1.7a4.8 4.8 0 0 0-6.4 0z" fill={color} />
      <path d="M1.2 3.2a11.3 11.3 0 0 1 14.6 0l-1.4 1.7a9.1 9.1 0 0 0-11.8 0z" fill={color} />
    </svg>
    <svg width="27" height="13" viewBox="0 0 27 13">
      <rect x="0.5" y="0.5" width="23" height="12" rx="3.6" stroke={color} strokeOpacity=".4" fill="none" />
      <rect x="2.2" y="2.2" width="19.6" height="8.6" rx="2.2" fill={color} />
      <path d="M25 4.4v4.2c.8-.3 1.4-1.1 1.4-2.1s-.6-1.8-1.4-2.1z" fill={color} fillOpacity=".4" />
    </svg>
  </div>
);

export const IconShare: React.FC<P> = ({ size = 16, color = "#333", style }) =>
  svg(
    size,
    <>
      <path d="M8 9H6v12h12V9h-2" stroke={color} strokeWidth="1.8" fill="none" />
      <path d="M12 15V2.5M8.3 6.2L12 2.5l3.7 3.7" stroke={color} strokeWidth="1.8" fill="none" strokeLinecap="round" />
    </>,
    style,
  );

export const IconTranslate: React.FC<P> = ({ size = 16, color = "#333", style }) =>
  svg(
    size,
    <>
      <rect x="2" y="3" width="13" height="13" rx="2" stroke={color} strokeWidth="1.6" fill="none" />
      <rect x="9" y="8" width="13" height="13" rx="2" fill={color} />
      <text x="15.5" y="18.2" fontSize="8" fontWeight="700" textAnchor="middle" fill="#2b2b2d" fontFamily="Inter">
        A
      </text>
    </>,
    style,
  );

export const IconSearch: React.FC<P> = ({ size = 16, color = "#333", style }) =>
  svg(
    size,
    <>
      <circle cx="10.5" cy="10.5" r="6.5" stroke={color} strokeWidth="2.2" fill="none" />
      <path d="M15.5 15.5l5 5" stroke={color} strokeWidth="2.4" strokeLinecap="round" />
    </>,
    style,
  );

export const IconArrow: React.FC<P & { dir?: "left" | "right" }> = ({ size = 16, color = "#333", style, dir = "left" }) =>
  svg(
    size,
    <path
      d={dir === "left" ? "M20 12H5M11 5l-7 7 7 7" : "M4 12h15M13 5l7 7-7 7"}
      stroke={color}
      strokeWidth="2.2"
      fill="none"
      strokeLinecap="round"
      strokeLinejoin="round"
    />,
    style,
  );

export const IconBackspace: React.FC<P> = ({ size = 16, color = "#fff", style }) =>
  svg(
    size,
    <>
      <path d="M8 4.5h13v15H8l-6-7.5z" stroke={color} strokeWidth="1.8" fill="none" strokeLinejoin="round" />
      <path d="M11.5 9l5 6M16.5 9l-5 6" stroke={color} strokeWidth="1.8" strokeLinecap="round" />
    </>,
    style,
  );

export const IconShift: React.FC<P> = ({ size = 16, color = "#fff", style }) =>
  svg(size, <path d="M12 3L3 12.5h5V21h8v-8.5h5z" fill={color} />, style);

export const IconMic: React.FC<P> = ({ size = 16, color = "#fff", style }) =>
  svg(
    size,
    <>
      <rect x="8.5" y="2" width="7" height="12.5" rx="3.5" fill={color} />
      <path d="M5 11a7 7 0 0 0 14 0M12 18v4" stroke={color} strokeWidth="2" fill="none" strokeLinecap="round" />
    </>,
    style,
  );

export const IconSmile: React.FC<P> = ({ size = 16, color = "#fff", style }) =>
  svg(
    size,
    <>
      <circle cx="12" cy="12" r="10" fill={color} />
      <circle cx="8.6" cy="9.6" r="1.4" fill="#2b2b2d" />
      <circle cx="15.4" cy="9.6" r="1.4" fill="#2b2b2d" />
      <path d="M7.5 14a5 5 0 0 0 9 0" stroke="#2b2b2d" strokeWidth="1.8" fill="none" strokeLinecap="round" />
    </>,
    style,
  );
