import React, {
  createContext,
  useContext,
  useLayoutEffect,
  useRef,
  useState,
} from "react";
import { continueRender, delayRender, useCurrentFrame } from "remotion";
import { GEO } from "../anim";

export type ChatLayout = Record<string, { top: number; height: number }>;

type Fits = Record<string, number>;
const FitContext = createContext<Fits>({});

/** Tamanho de fonte ajustado para um balão (ou o máximo, antes da medição). */
export const useFittedFont = (id: string, max: number) =>
  useContext(FitContext)[id] ?? max;

type Props = {
  readonly children: React.ReactNode;
  /** Recebe as posições medidas e devolve o scroll (px) para o frame. */
  readonly scrollAt: (layout: ChatLayout, frame: number) => number;
};

/**
 * Área rolável da conversa. Na montagem:
 * 1. reduz a fonte dos balões marcados com data-fit-id até o texto completo caber;
 * 2. mede a posição de cada bloco com data-anchor, usada nos keyframes de scroll.
 * O scroll recebe um desfoque vertical proporcional à velocidade (motion blur sutil).
 */
export const ChatViewport: React.FC<Props> = ({ children, scrollAt }) => {
  const frame = useCurrentFrame();
  const columnRef = useRef<HTMLDivElement>(null);
  const [handle] = useState(() => delayRender("Medindo a conversa"));
  const [fits, setFits] = useState<Fits | null>(null);
  const [layout, setLayout] = useState<ChatLayout | null>(null);

  useLayoutEffect(() => {
    if (fits) return;
    let cancelled = false;
    document.fonts.ready.then(() => {
      if (cancelled || !columnRef.current) return;
      const result: Fits = {};
      columnRef.current
        .querySelectorAll<HTMLElement>("[data-fit-id]")
        .forEach((el) => {
          const maxHeight = Number(el.dataset.fitMaxHeight);
          const min = Number(el.dataset.fitMin);
          let size = Number(el.dataset.fitFont);
          el.style.fontSize = `${size}px`;
          while (el.scrollHeight > maxHeight && size > min) {
            size -= 1;
            el.style.fontSize = `${size}px`;
          }
          if (el.scrollHeight > maxHeight) {
            console.warn(
              `Texto de "${el.dataset.fitId}" excede o balão mesmo na fonte mínima.`,
            );
          }
          result[el.dataset.fitId as string] = size;
        });
      setFits(result);
    });
    return () => {
      cancelled = true;
    };
  }, [fits]);

  useLayoutEffect(() => {
    if (!fits || layout || !columnRef.current) return;
    const column = columnRef.current;
    const measured: ChatLayout = {};
    column.querySelectorAll<HTMLElement>("[data-anchor]").forEach((el) => {
      let top = 0;
      let node: HTMLElement | null = el;
      while (node && node !== column) {
        top += node.offsetTop;
        node = node.offsetParent as HTMLElement | null;
      }
      measured[el.dataset.anchor as string] = { top, height: el.offsetHeight };
    });
    setLayout(measured);
    continueRender(handle);
  }, [fits, layout, handle]);

  const scroll = layout ? scrollAt(layout, frame) : 0;
  const velocity = layout ? Math.abs(scroll - scrollAt(layout, frame - 1)) : 0;
  const blur = Math.min(6, velocity * 0.09);

  return (
    <div
      style={{
        position: "absolute",
        left: 0,
        right: 0,
        top: GEO.viewportTop - GEO.appTop,
        height: GEO.viewportHeight + 200, // segue por trás do composer, como no app real
        overflow: "hidden",
      }}
    >
      <svg width={0} height={0} style={{ position: "absolute" }}>
        <filter id="scroll-blur">
          <feGaussianBlur stdDeviation={`0 ${blur.toFixed(2)}`} />
        </filter>
      </svg>
      <FitContext.Provider value={fits ?? {}}>
        <div
          ref={columnRef}
          style={{
            position: "relative",
            marginLeft: GEO.columnLeftInMain,
            width: 960,
            translate: `0px ${-scroll}px`,
            filter: blur > 0.3 ? "url(#scroll-blur)" : undefined,
          }}
        >
          {children}
        </div>
      </FitContext.Provider>
    </div>
  );
};
