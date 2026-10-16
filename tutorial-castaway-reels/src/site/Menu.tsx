import React from "react";
import { interpolate } from "remotion";
import { IconChevronDown } from "../components/Icons";
import { SCREEN_W } from "../components/Phone";
import { C, F } from "../theme";
import { HEADER_H } from "./SiteHeader";

export const MENU_ITEMS = ["About Us", "Clients", "Jobs", "VIP", "Apply Now!", "Academy", "Store", "FAQs", "Contact Us"];
export const MENU_ROW = 64;
export const APPLY_INDEX = 4;
/** Centro vertical (coordenadas da página) do item "Apply Now!". */
export const APPLY_Y = HEADER_H + APPLY_INDEX * MENU_ROW + MENU_ROW / 2;

const clamp = { extrapolateLeft: "clamp", extrapolateRight: "clamp" } as const;

/** Menu do site. `open` 0..1 abre o painel; `active` 0..1 destaca "Apply Now!". */
export const Menu: React.FC<{ open: number; active: number }> = ({ open, active }) => {
  if (open <= 0) return null;
  const h = MENU_ITEMS.length * MENU_ROW;
  return (
    <div
      style={{
        position: "absolute",
        left: 0,
        top: HEADER_H,
        width: SCREEN_W,
        height: h * open,
        overflow: "hidden",
        background: C.menu,
        boxShadow: "0 10px 20px rgba(0,0,0,0.15)",
      }}
    >
      {MENU_ITEMS.map((item, i) => {
        const p = interpolate(open, [0.2 + i * 0.06, 0.55 + i * 0.06], [0, 1], clamp);
        const isApply = i === APPLY_INDEX;
        return (
          <div
            key={item}
            style={{
              position: "absolute",
              left: 0,
              top: i * MENU_ROW,
              width: SCREEN_W,
              height: MENU_ROW,
              display: "flex",
              alignItems: "center",
              justifyContent: "space-between",
              padding: "0 22px",
              boxSizing: "border-box",
              background: isApply ? `rgba(30,80,140,${0.35 * active})` : "transparent",
              fontFamily: F.openSans,
              fontWeight: isApply && active > 0.5 ? 700 : 400,
              fontSize: 17,
              color: "#fff",
              opacity: p,
              transform: `translateX(${(1 - p) * -24}px)`,
            }}
          >
            {item}
            {item === "About Us" || item === "Jobs" ? <IconChevronDown size={14} color="#fff" /> : null}
          </div>
        );
      })}
    </div>
  );
};
