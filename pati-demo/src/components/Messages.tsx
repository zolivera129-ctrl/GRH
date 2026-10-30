import React from "react";
import { Img, staticFile, useCurrentFrame } from "remotion";
import { COLORS, LAYOUT } from "../config";
import { appear, fade, GEO } from "../anim";
import { useFittedFont } from "./ChatViewport";

type Mask = { left: number; top: number; width: number; height: number };

/** Miniatura de imagem anexada. As máscaras desfocam e cobrem identificadores pessoais. */
export const Thumb: React.FC<{
  readonly src: string;
  readonly aspect: number;
  readonly height: number;
  readonly masks?: Mask[];
  readonly radius?: number;
}> = ({ src, aspect, height, masks = [], radius = 18 }) => {
  const width = Math.round(height * aspect);
  const image = (
    <Img
      src={staticFile(src)}
      style={{ width, height, objectFit: "cover", display: "block" }}
    />
  );
  return (
    <div
      style={{
        position: "relative",
        width,
        height,
        borderRadius: radius,
        overflow: "hidden",
        border: `1px solid ${COLORS.line}`,
        flexShrink: 0,
      }}
    >
      {image}
      {masks.map((m, i) => (
        <div
          key={i}
          style={{
            position: "absolute",
            left: `${m.left}%`,
            top: `${m.top}%`,
            width: `${m.width}%`,
            height: `${m.height}%`,
            overflow: "hidden",
          }}
        >
          {/* cópia desfocada da própria imagem, recortada na área sensível */}
          <Img
            src={staticFile(src)}
            style={{
              position: "absolute",
              left: (-m.left / 100) * width,
              top: (-m.top / 100) * height,
              width,
              height,
              objectFit: "cover",
              filter: "blur(9px)",
              scale: "1.08",
            }}
          />
          <div
            style={{
              position: "absolute",
              inset: 0,
              backgroundColor: "rgba(36, 36, 40, 0.6)",
            }}
          />
        </div>
      ))}
    </div>
  );
};

/** Mensagem do usuário: anexo opcional + balão cinza-claro à direita. */
export const UserMessage: React.FC<{
  readonly anchor: string;
  readonly at: number; // frame em que a mensagem é enviada
  readonly attachment?: React.ReactNode;
  readonly children: React.ReactNode;
}> = ({ anchor, at, attachment, children }) => {
  const frame = useCurrentFrame();
  const fitId = `${anchor}-bubble`;
  const font = useFittedFont(fitId, LAYOUT.userFont);
  return (
    <div
      data-anchor={anchor}
      style={{
        display: "flex",
        flexDirection: "column",
        alignItems: "flex-end",
        gap: 12,
        marginBottom: 40,
        ...appear(frame, at, 12, 18),
      }}
    >
      {attachment}
      <div
        data-fit-id={fitId}
        data-fit-font={LAYOUT.userFont}
        data-fit-min={LAYOUT.userFontMin}
        data-fit-max-height={Math.round(
          GEO.viewportHeight * LAYOUT.userBubbleMaxHeightRatio,
        )}
        style={{
          maxWidth: LAYOUT.userBubbleMaxWidth,
          backgroundColor: COLORS.userBubble,
          borderRadius: 26,
          padding: "18px 26px",
          fontSize: font,
          lineHeight: 1.5,
          color: COLORS.text,
          overflowWrap: "break-word",
        }}
      >
        {children}
      </div>
    </div>
  );
};

export const Avatar: React.FC<{ readonly size?: number }> = ({ size = 40 }) => (
  <div
    style={{
      width: size,
      height: size,
      borderRadius: size / 2,
      backgroundColor: COLORS.accent,
      color: "white",
      fontWeight: 700,
      fontSize: size * 0.48,
      display: "flex",
      alignItems: "center",
      justifyContent: "center",
      flexShrink: 0,
    }}
  >
    P
  </div>
);

/** Resposta da PATI: avatar à esquerda, indicador "analisando" e blocos que entram em sequência. */
export const PatiMessage: React.FC<{
  readonly anchor: string;
  readonly thinkingAt: number;
  readonly firstBlockAt: number;
  readonly children: React.ReactNode;
}> = ({ anchor, thinkingAt, firstBlockAt, children }) => {
  const frame = useCurrentFrame();
  const thinkingOpacity = Math.min(
    fade(frame, thinkingAt, thinkingAt + 6),
    fade(frame, firstBlockAt - 4, firstBlockAt, 1, 0),
  );
  const dot = (i: number) =>
    0.35 + 0.65 * Math.max(0, Math.sin((frame - thinkingAt) / 4 - i * 0.9));
  return (
    <div
      data-anchor={anchor}
      style={{ display: "flex", gap: 18, marginBottom: 96 }}
    >
      <div style={{ opacity: fade(frame, thinkingAt, thinkingAt + 6) }}>
        <Avatar />
      </div>
      <div style={{ position: "relative", flex: 1, paddingTop: 4 }}>
        <div
          style={{
            position: "absolute",
            top: 10,
            left: 0,
            display: "flex",
            gap: 8,
            alignItems: "center",
            opacity: thinkingOpacity,
            color: COLORS.textMuted,
            fontSize: 20,
          }}
        >
          Analisando
          {[0, 1, 2].map((i) => (
            <div
              key={i}
              style={{
                width: 7,
                height: 7,
                borderRadius: 4,
                backgroundColor: COLORS.textMuted,
                opacity: dot(i),
              }}
            />
          ))}
        </div>
        {children}
      </div>
    </div>
  );
};

export const PatiBlock: React.FC<{
  readonly anchor: string;
  readonly at: number;
  readonly strong?: boolean;
  readonly children: React.ReactNode;
}> = ({ anchor, at, strong, children }) => {
  const frame = useCurrentFrame();
  return (
    <div
      data-anchor={anchor}
      style={{
        fontSize: LAYOUT.patiFont,
        lineHeight: 1.5,
        color: COLORS.text,
        fontWeight: strong ? 600 : 400,
        marginBottom: 14,
        ...appear(frame, at),
      }}
    >
      {children}
    </div>
  );
};

/** Recomendação em destaque: barra lateral na cor da PATI e fundo suave. */
export const RecoCard: React.FC<{
  readonly anchor: string;
  readonly at: number;
  readonly label?: string;
  readonly size?: number;
  readonly children: React.ReactNode;
  readonly note?: React.ReactNode;
  readonly noteAt?: number;
}> = ({ anchor, at, label, size = 30, children, note, noteAt }) => {
  const frame = useCurrentFrame();
  return (
    <div
      data-anchor={anchor}
      style={{
        marginTop: 10,
        marginBottom: 16,
        padding: "20px 28px 22px",
        backgroundColor: COLORS.accentSoft,
        borderLeft: `5px solid ${COLORS.accent}`,
        borderRadius: "4px 14px 14px 4px",
        ...appear(frame, at, 14, 18),
      }}
    >
      {label ? (
        <div
          style={{
            fontSize: 17,
            fontWeight: 600,
            letterSpacing: 1.2,
            textTransform: "uppercase",
            color: COLORS.accent,
            marginBottom: 8,
          }}
        >
          {label}
        </div>
      ) : null}
      <div
        style={{
          fontSize: size,
          lineHeight: 1.38,
          fontWeight: 600,
          color: COLORS.text,
        }}
      >
        {children}
      </div>
      {note ? (
        <div
          style={{
            fontSize: 22,
            lineHeight: 1.45,
            color: COLORS.textSoft,
            marginTop: 10,
            ...appear(frame, noteAt ?? at, 12, 10),
          }}
        >
          {note}
        </div>
      ) : null}
    </div>
  );
};
