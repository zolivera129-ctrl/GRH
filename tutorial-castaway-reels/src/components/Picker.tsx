import React from "react";
import { F } from "../theme";
import { IconCheck } from "./Icons";

export const PICKER_ROW = 44;
export const PICKER_VISIBLE = 8;

export const COUNTRIES: [string, string][] = [
  ["Afghanistan", "+93"],
  ["Albania", "+355"],
  ["Algeria", "+213"],
  ["Andorra", "+376"],
  ["Angola", "+244"],
  ["Argentina", "+54"],
  ["Armenia", "+374"],
  ["Australia", "+61"],
  ["Austria", "+43"],
  ["Bahamas", "+1-242"],
  ["Bangladesh", "+880"],
  ["Barbados", "+1-246"],
  ["Belgium", "+32"],
  ["Brazil", "+55"],
  ["Bulgaria", "+359"],
  ["Canada", "+1"],
  ["Chile", "+56"],
  ["China", "+86"],
  ["Colombia", "+57"],
  ["Costa Rica", "+506"],
  ["Croatia", "+385"],
  ["Cuba", "+53"],
  ["Denmark", "+45"],
  ["Ecuador", "+593"],
  ["Egypt", "+20"],
  ["France", "+33"],
  ["Germany", "+49"],
  ["Ghana", "+233"],
  ["Greece", "+30"],
  ["Honduras", "+504"],
  ["Hungary", "+36"],
  ["India", "+91"],
  ["Indonesia", "+62"],
  ["Ireland", "+353"],
  ["Italy", "+39"],
  ["Jamaica", "+1-876"],
  ["Japan", "+81"],
  ["Kenya", "+254"],
  ["Mexico", "+52"],
  ["Morocco", "+212"],
  ["Nepal", "+977"],
  ["Netherlands", "+31"],
  ["Nigeria", "+234"],
  ["Norway", "+47"],
  ["Pakistan", "+92"],
  ["Panama", "+507"],
  ["Peru", "+51"],
  ["Philippines", "+63"],
  ["Poland", "+48"],
  ["Portugal", "+351"],
  ["Romania", "+40"],
  ["Serbia", "+381"],
];

export const PHILIPPINES = COUNTRIES.findIndex(([n]) => n === "Philippines");

/**
 * Menu de seleção do Safari (popover escuro com a lista de países).
 * `scroll` é o deslocamento da lista em px; `active` é a linha tocada.
 */
export const Picker: React.FC<{
  items: string[];
  header: string;
  x: number;
  y: number;
  width: number;
  open: number;
  scroll: number;
  active: number | null;
}> = ({ items, header, x, y, width, open, scroll, active }) => {
  if (open <= 0.001) return null;
  const h = PICKER_ROW * PICKER_VISIBLE;
  return (
    <div
      style={{
        position: "absolute",
        left: x,
        top: y,
        width,
        height: h,
        borderRadius: 16,
        overflow: "hidden",
        background: "rgba(44,44,46,0.94)",
        boxShadow: "0 18px 50px rgba(0,0,0,0.45)",
        opacity: open,
        transform: `scale(${0.85 + 0.15 * open})`,
        transformOrigin: "50% 0%",
        zIndex: 40,
      }}
    >
      <div style={{ position: "absolute", left: 0, top: -scroll, width: "100%" }}>
        {[header, ...items].map((label, i) => {
          const isActive = active !== null && i - 1 === active;
          return (
            <div
              key={label}
              style={{
                height: PICKER_ROW,
                display: "flex",
                alignItems: "center",
                gap: 8,
                padding: "0 16px",
                fontFamily: F.ui,
                fontSize: 16,
                color: i === 0 ? "rgba(255,255,255,0.6)" : "#fff",
                background: isActive ? "rgba(255,255,255,0.18)" : "transparent",
                borderBottom: "0.5px solid rgba(255,255,255,0.12)",
                boxSizing: "border-box",
                whiteSpace: "nowrap",
              }}
            >
              <div style={{ width: 16 }}>{i === 0 ? <IconCheck size={15} color="rgba(255,255,255,0.7)" /> : null}</div>
              {label}
            </div>
          );
        })}
      </div>
    </div>
  );
};

/** Deslocamento que deixa a linha `index` no centro do popover. */
export const scrollToRow = (index: number) => (index + 1) * PICKER_ROW - (PICKER_ROW * PICKER_VISIBLE) / 2 + PICKER_ROW / 2;
