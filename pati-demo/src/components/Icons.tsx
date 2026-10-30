import React from "react";

type P = { readonly size?: number; readonly color?: string };

export const PlusIcon: React.FC<P> = ({ size = 20, color = "#333" }) => (
  <svg width={size} height={size} viewBox="0 0 20 20">
    <path
      d="M10 4v12M4 10h12"
      stroke={color}
      strokeWidth={1.8}
      strokeLinecap="round"
    />
  </svg>
);

export const ArrowUpIcon: React.FC<P> = ({ size = 20, color = "#fff" }) => (
  <svg width={size} height={size} viewBox="0 0 20 20">
    <path
      d="M10 15V5M5.5 9.5 10 5l4.5 4.5"
      stroke={color}
      strokeWidth={2}
      fill="none"
      strokeLinecap="round"
      strokeLinejoin="round"
    />
  </svg>
);

export const LockIcon: React.FC<P> = ({ size = 14, color = "#777" }) => (
  <svg width={size} height={size} viewBox="0 0 14 14">
    <rect x={2.5} y={6} width={9} height={6.5} rx={1.5} fill={color} />
    <path
      d="M4.5 6V4.5a2.5 2.5 0 0 1 5 0V6"
      stroke={color}
      strokeWidth={1.4}
      fill="none"
    />
  </svg>
);

export const EditIcon: React.FC<P> = ({ size = 18, color = "#444" }) => (
  <svg width={size} height={size} viewBox="0 0 18 18">
    <path
      d="M3 15h3l8-8-3-3-8 8v3z"
      stroke={color}
      strokeWidth={1.5}
      fill="none"
      strokeLinejoin="round"
    />
  </svg>
);

export const CheckIcon: React.FC<P> = ({ size = 16, color = "#1F4D3A" }) => (
  <svg width={size} height={size} viewBox="0 0 16 16">
    <path
      d="M3.5 8.5 6.5 11.5 12.5 4.5"
      stroke={color}
      strokeWidth={2}
      fill="none"
      strokeLinecap="round"
      strokeLinejoin="round"
    />
  </svg>
);

export const ChevronIcon: React.FC<P> = ({ size = 14, color = "#777" }) => (
  <svg width={size} height={size} viewBox="0 0 14 14">
    <path
      d="M3.5 5.5 7 9l3.5-3.5"
      stroke={color}
      strokeWidth={1.6}
      fill="none"
      strokeLinecap="round"
      strokeLinejoin="round"
    />
  </svg>
);

/** Ponteiro do mouse no estilo macOS. */
export const PointerIcon: React.FC<P> = ({ size = 30 }) => (
  <svg
    width={size}
    height={size * 1.4}
    viewBox="0 0 20 28"
    style={{ filter: "drop-shadow(0 2px 3px rgba(0,0,0,0.3))" }}
  >
    <path
      d="M2 2v20.5l5.2-4.9 3.4 7.9 3.6-1.5-3.4-7.7H18L2 2z"
      fill="#111"
      stroke="#fff"
      strokeWidth={1.6}
      strokeLinejoin="round"
    />
  </svg>
);
