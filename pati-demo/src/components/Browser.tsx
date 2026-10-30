import React from "react";
import { useCurrentFrame, useVideoConfig } from "remotion";
import {
  ASSETS,
  COLORS,
  LAYOUT,
  STORY_PRIVACY_MASKS,
  TEXTS,
  TIMING,
} from "../config";
import { appear, fade, GEO, nb, sec } from "../anim";
import {
  ArrowUpIcon,
  CheckIcon,
  ChevronIcon,
  EditIcon,
  LockIcon,
  PlusIcon,
} from "./Icons";
import { Avatar, Thumb } from "./Messages";

const W = LAYOUT.window;

/** Janela do navegador com barra de abas discreta. O conteúdo do app vem como children. */
export const BrowserWindow: React.FC<{
  readonly children: React.ReactNode;
  readonly style?: React.CSSProperties;
}> = ({ children, style }) => (
  <div
    style={{
      position: "absolute",
      left: W.x,
      top: W.y,
      width: W.width,
      height: W.height,
      borderRadius: W.radius,
      overflow: "hidden",
      backgroundColor: COLORS.window,
      boxShadow:
        "0 30px 80px rgba(30, 28, 24, 0.16), 0 2px 8px rgba(30, 28, 24, 0.08)",
      border: `1px solid ${COLORS.chromeLine}`,
      ...style,
    }}
  >
    <div
      style={{
        height: LAYOUT.chromeHeight,
        backgroundColor: COLORS.chrome,
        borderBottom: `1px solid ${COLORS.chromeLine}`,
        display: "flex",
        alignItems: "center",
        padding: "0 20px",
        gap: 9,
      }}
    >
      {["#E46A5E", "#E9B84A", "#61BE59"].map((c) => (
        <div
          key={c}
          style={{
            width: 13,
            height: 13,
            borderRadius: 7,
            backgroundColor: c,
            opacity: 0.85,
          }}
        />
      ))}
      <div
        style={{
          marginLeft: 24,
          height: 34,
          padding: "0 16px",
          borderRadius: "9px 9px 0 0",
          backgroundColor: COLORS.window,
          alignSelf: "flex-end",
          display: "flex",
          alignItems: "center",
          gap: 10,
          fontSize: 15,
          color: COLORS.textSoft,
          minWidth: 200,
        }}
      >
        <Avatar size={18} />
        {TEXTS.tabTitle}
      </div>
      <div
        style={{
          position: "absolute",
          left: "50%",
          translate: "-50% 0",
          height: 32,
          width: 520,
          borderRadius: 16,
          backgroundColor: "#E7E6E2",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          gap: 8,
          fontSize: 15,
          color: COLORS.textSoft,
        }}
      >
        <LockIcon />
        {TEXTS.address}
      </div>
    </div>
    <div
      style={{ position: "relative", height: GEO.appHeight, display: "flex" }}
    >
      {children}
    </div>
  </div>
);

const SIDEBAR_ITEMS = [
  {
    text: TEXTS.test1.sidebar,
    at: TIMING.test1.start,
    until: TIMING.test2.start,
  },
  {
    text: TEXTS.test2.sidebar,
    at: TIMING.test2.start,
    until: TIMING.test3.start,
  },
  {
    text: TEXTS.test3.sidebar,
    at: TIMING.test3.start,
    until: TIMING.closing.start,
  },
];

export const Sidebar: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const closing = sec(TIMING.closing.start, fps);
  return (
    <div
      style={{
        width: LAYOUT.sidebarWidth,
        flexShrink: 0,
        backgroundColor: COLORS.sidebar,
        borderRight: `1px solid ${COLORS.line}`,
        padding: "16px 14px",
        display: "flex",
        flexDirection: "column",
        gap: 6,
      }}
    >
      <div
        style={{
          display: "flex",
          alignItems: "center",
          gap: 12,
          height: 40,
          padding: "0 10px",
          fontWeight: 700,
          fontSize: 19,
        }}
      >
        <Avatar size={30} />
        PATI
      </div>
      <div
        style={{
          display: "flex",
          alignItems: "center",
          gap: 12,
          height: 42,
          padding: "0 10px",
          fontSize: 16,
          color: COLORS.text,
          marginTop: 10,
        }}
      >
        <EditIcon />
        {TEXTS.sidebarNew}
      </div>
      <div
        style={{
          fontSize: 13,
          color: COLORS.textMuted,
          fontWeight: 600,
          padding: "22px 10px 6px",
          letterSpacing: 0.4,
        }}
      >
        {TEXTS.sidebarSection}
      </div>
      {SIDEBAR_ITEMS.map((item) => {
        const at = sec(item.at, fps);
        const active = frame >= at && frame < sec(item.until, fps);
        return (
          <div
            key={item.text}
            style={{
              display: "flex",
              alignItems: "center",
              justifyContent: "space-between",
              height: 40,
              padding: "0 10px",
              borderRadius: 9,
              fontSize: 16,
              color: COLORS.text,
              backgroundColor: active ? "#EAEAE6" : "transparent",
              ...appear(frame, at, 10, 8),
            }}
          >
            {item.text}
            <div style={{ opacity: fade(frame, closing + 4, closing + 14) }}>
              <CheckIcon />
            </div>
          </div>
        );
      })}
      <div style={{ flex: 1 }} />
      <div
        style={{
          display: "flex",
          alignItems: "center",
          gap: 12,
          height: 48,
          padding: "0 10px",
          fontSize: 15,
          color: COLORS.textSoft,
        }}
      >
        <div
          style={{
            width: 30,
            height: 30,
            borderRadius: 15,
            backgroundColor: "#DCDAD4",
            fontSize: 11,
            fontWeight: 700,
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            color: COLORS.textSoft,
          }}
        >
          GRH
        </div>
        {TEXTS.sidebarFooter}
      </div>
    </div>
  );
};

/** Cabeçalho do chat. O nome entra quando o título da apresentação sobe (Cena 1). */
export const Header: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const at = sec(TIMING.introToHeader, fps) + 10;
  return (
    <div
      style={{
        position: "absolute",
        left: 0,
        right: 0,
        top: 0,
        height: LAYOUT.headerHeight,
        display: "flex",
        alignItems: "center",
        padding: "0 28px",
        backgroundColor: COLORS.window,
        zIndex: 2,
      }}
    >
      <div
        style={{
          display: "flex",
          alignItems: "center",
          gap: 12,
          ...appear(frame, at, 14, 10),
        }}
      >
        <Avatar size={30} />
        <div style={{ fontSize: 20, fontWeight: 600, color: COLORS.text }}>
          {TEXTS.appName}
        </div>
        <ChevronIcon />
      </div>
    </div>
  );
};

type ComposerSession = {
  attachAt?: number;
  attachment?: React.ReactNode;
  textAt: number;
  text: React.ReactNode;
  sendAt: number;
};

/** Campo de mensagem fixo na base. Cresce para cima quando recebe anexo e texto. */
export const Composer: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const t1 = TIMING.test1;
  const t2 = TIMING.test2;
  const t3 = TIMING.test3;
  const sessions: ComposerSession[] = [
    {
      attachAt: sec(t1.attachClick, fps) + 3,
      attachment: (
        <Thumb
          src={ASSETS.storyImage}
          aspect={ASSETS.storyAspect}
          height={76}
          masks={STORY_PRIVACY_MASKS}
          radius={10}
        />
      ),
      textAt: sec(t1.composerText, fps),
      text: TEXTS.test1.user,
      sendAt: sec(t1.send, fps),
    },
    {
      textAt: sec(t2.composerText, fps),
      text: (
        <>
          {nb(TEXTS.test2.userIntro)} {TEXTS.test2.optionA.label} -{" "}
          {TEXTS.test2.optionA.text} / {TEXTS.test2.optionB.label} -{" "}
          {TEXTS.test2.optionB.text}
        </>
      ),
      sendAt: sec(t2.send, fps),
    },
    {
      attachAt: sec(t3.attachClick, fps) + 3,
      attachment: (
        <Thumb
          src={ASSETS.artImage}
          aspect={ASSETS.artAspect}
          height={76}
          radius={10}
        />
      ),
      textAt: sec(t3.composerText, fps),
      text: TEXTS.test3.user,
      sendAt: sec(t3.send, fps),
    },
  ];
  const session = sessions.find(
    (s) => frame >= (s.attachAt ?? s.textAt) && frame < s.sendAt,
  );
  const hasText = session && frame >= session.textAt;

  return (
    <>
      <div
        style={{
          position: "absolute",
          left: GEO.columnLeftInMain,
          width: LAYOUT.columnWidth,
          bottom: LAYOUT.disclaimerHeight + LAYOUT.composerBottom,
          backgroundColor: COLORS.window,
          border: "1px solid #DCDBD6",
          borderRadius: 28,
          boxShadow: "0 4px 18px rgba(0,0,0,0.05)",
          padding: "16px 18px 14px",
          display: "flex",
          flexDirection: "column",
          gap: 12,
          zIndex: 3,
        }}
      >
        {session?.attachment ? (
          <div style={{ ...appear(frame, session.attachAt ?? 0, 8, 8) }}>
            {session.attachment}
          </div>
        ) : null}
        <div
          style={{
            minHeight: 30,
            fontSize: 21,
            lineHeight: 1.45,
            color: hasText ? COLORS.text : COLORS.textMuted,
            padding: "0 6px",
          }}
        >
          {hasText ? (
            <div
              style={{
                opacity: fade(frame, session.textAt, session.textAt + 5),
              }}
            >
              {session.text}
            </div>
          ) : (
            TEXTS.composerPlaceholder
          )}
        </div>
        <div
          style={{
            height: 40,
            display: "flex",
            justifyContent: "space-between",
          }}
        >
          <div
            style={{
              width: 40,
              height: 40,
              borderRadius: 20,
              border: "1px solid #DCDBD6",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
            }}
          >
            <PlusIcon />
          </div>
          <div
            style={{
              width: 40,
              height: 40,
              borderRadius: 20,
              backgroundColor: hasText ? COLORS.accent : "#D6D5D0",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
            }}
          >
            <ArrowUpIcon />
          </div>
        </div>
      </div>
      <div
        style={{
          position: "absolute",
          left: 0,
          right: 0,
          bottom: 0,
          height: LAYOUT.disclaimerHeight + LAYOUT.composerBottom + 30,
          paddingBottom: 9,
          backgroundColor: COLORS.window,
          display: "flex",
          justifyContent: "center",
          alignItems: "flex-end",
          fontSize: 14,
          color: COLORS.textMuted,
          zIndex: 2,
        }}
      >
        {TEXTS.disclaimer}
      </div>
    </>
  );
};
