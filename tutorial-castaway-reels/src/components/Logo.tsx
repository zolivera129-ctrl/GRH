import React from "react";
import { Img, staticFile } from "remotion";

/*
 * Logo oficial da Cast-A-Way, recortado do manual em vetor (CAW_LOGOTIPO_final_VECTOR.pdf):
 * - castaway-symbol.svg: a escotilha com a palmeira. O miolo e os rebites são transparentes
 *   no arquivo original, por isso o SVG ganhou um disco branco por trás (como no site).
 * - castaway-wordmark-white.svg: "CAST·A·WAY / CRUISE & RESORT HIRING AGENCY" (Futura) em branco,
 *   para os fundos azuis.
 */

// Os SVGs têm 1 pt de margem: símbolo 194,5 × 194,5 pt e wordmark 241,75 × 68,5 pt.
const WORDMARK_RATIO = 241.75 / 68.5;
/** Lockup vertical do manual, em múltiplos do tamanho do símbolo (espaço visível de 16,75 pt). */
export const LOCKUP = { wordmarkHeight: 68.5 / 194.5, gap: 14.75 / 194.5 };

// O aro começa em 82,3% do raio. As máscaras se sobrepõem um pouco (as duas camadas são brancas
// nessa faixa) para não aparecer emenda quando o aro gira.
const INNER_MASK = "radial-gradient(circle closest-side, #000 81%, transparent 81.5%)";
const RING_MASK = "radial-gradient(circle closest-side, transparent 80%, #000 80.5%)";

/** Símbolo da escotilha. `spin` gira só o aro com os rebites; a palmeira fica parada. */
export const Porthole: React.FC<{ size: number; spin?: number; style?: React.CSSProperties }> = ({ size, spin = 0, style }) => {
  const src = staticFile("logo/castaway-symbol.svg");
  if (!spin) return <Img src={src} style={{ display: "block", width: size, height: size, ...style }} />;
  const layer: React.CSSProperties = { position: "absolute", left: 0, top: 0, width: size, height: size };
  return (
    <div style={{ position: "relative", width: size, height: size, ...style }}>
      <Img src={src} style={{ ...layer, WebkitMaskImage: INNER_MASK, maskImage: INNER_MASK }} />
      <Img src={src} style={{ ...layer, transform: `rotate(${spin}deg)`, WebkitMaskImage: RING_MASK, maskImage: RING_MASK }} />
    </div>
  );
};

export const Wordmark: React.FC<{ height: number; style?: React.CSSProperties }> = ({ height, style }) => (
  <Img src={staticFile("logo/castaway-wordmark-white.svg")} style={{ display: "block", height, width: height * WORDMARK_RATIO, ...style }} />
);
