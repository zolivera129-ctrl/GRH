import React from "react";
import { AbsoluteFill, Sequence, interpolate, useCurrentFrame, useVideoConfig } from "remotion";
import { Background } from "../components/Background";
import { StepCaption } from "../components/Caption";
import { IconBolt, IconCheck, IconEye, IconTarget } from "../components/Icons";
import { KEYBOARD_H, KeyGlow, Keyboard } from "../components/Keyboard";
import { Porthole } from "../components/Logo";
import { BEZEL, PHONE_H, PHONE_W, Phone, SCREEN_H, SCREEN_W } from "../components/Phone";
import { COUNTRIES, TARGET_COUNTRY, PICKER_ROW, PICKER_VISIBLE, Picker, scrollToRow } from "../components/Picker";
import { Touch } from "../components/Touch";
import { Sfx, SfxEvent, keyClicks } from "../components/Sfx";
import { backOut, lerp, out, pulse, smooth, track, typed } from "../lib/anim";
import { ApplyPage, ApplyState, CODE_RECT, FIELD_H, RADIO_INSTAGRAM_Y, Y } from "../site/ApplyPage";
import { BrowserChrome, contentTop } from "../site/Browser";
import { HomePage } from "../site/HomePage";
import { APPLY_Y, Menu } from "../site/Menu";
import { BURGER, SiteHeader } from "../site/SiteHeader";
import { C, COPY, F } from "../theme";
import "../fonts";

// ---------------------------------------------------------------------------
// Linha do tempo (frames a 30 fps, relativos ao início desta cena)
// ---------------------------------------------------------------------------
export const WALKTHROUGH_FRAMES = 1250;

const T = {
  // Passo 1: abrir o site
  urlTap: 34,
  urlType: 46,
  goTap: 90,
  siteIn: 104,
  // Passo 2: menu
  cap2: 118,
  menuTap: 146,
  applyTap: 188,
  nav: 200,
  // Passo 3: contatos
  cap3: 222,
  fnTap: 258,
  fnType: 270,
  lnTap: 290,
  lnType: 296,
  natTap: 338,
  natPick: 392,
  emailTap: 422,
  emailType: 434,
  preTap: 494,
  prePick: 548,
  phoneTap: 614,
  phoneType: 626,
  // Passo 4: demais seções
  cap4: 664,
  // Passo 5: código de campanha
  cap5: 784,
  card: 826,
  lift: 864,
  land: 892,
  benefits: 918,
  // Passo 6: enviar
  cap6: 1066,
  igTap: 1090,
  captchaTap: 1134,
  sendTap: 1166,
  success: 1180,
};

const K = 1.5; // escala base do celular
const DEF = { z: 1, fx: SCREEN_W / 2, fy: SCREEN_H / 2, cx: 540, cy: 1290, ry: 0, rx: 0 };

const S_CONTACTS = 320;
const S_REF = 2382;
const S_SEND = 2598;

const TOP_APPLY = contentTop(1); // 72
const sy = (pageY: number, scroll: number) => TOP_APPLY + pageY - scroll; // página -> tela
const fieldC = (pageY: number, scroll = S_CONTACTS) => sy(pageY, scroll) + FIELD_H / 2;

type Cam = typeof DEF;
const key = (f: number, c: Partial<Cam>): Cam & { f: number } => ({ ...DEF, ...c, f });

const CAM_KEYS = [
  key(0, {}),
  key(22, {}),
  key(40, { z: 1.9, fy: 75, cy: 1000 }),
  key(74, { z: 1.9, fy: 75, cy: 1000 }),
  key(92, {}),
  key(122, {}),
  key(140, { z: 1.8, fx: 300, fy: 148, cy: 1000 }),
  key(158, { z: 1.8, fx: 300, fy: 148, cy: 1000 }),
  key(180, { z: 1.35, fy: 400, cy: 1150 }),
  key(196, { z: 1.35, fy: 400, cy: 1150 }),
  key(216, {}),
  key(240, {}),
  key(256, { z: 1.4, fy: 330, cy: 1100 }),
  key(316, { z: 1.4, fy: 330, cy: 1100 }),
  key(334, { z: 1.55, fy: 420, cy: 1060 }),
  key(404, { z: 1.55, fy: 420, cy: 1060 }),
  key(420, { z: 1.4, fy: 430, cy: 1100 }),
  key(470, { z: 1.4, fy: 430, cy: 1100 }),
  key(490, { z: 1.5, fy: 560, cy: 1090 }),
  key(554, { z: 1.5, fy: 560, cy: 1090 }),
  key(572, { z: 2.15, fy: fieldC(Y.prefix), cy: 1020 }),
  key(596, { z: 2.15, fy: fieldC(Y.prefix), cy: 1020 }),
  key(612, { z: 1.4, fy: 520, cy: 1080 }),
  key(664, { z: 1.4, fy: 520, cy: 1080 }),
  key(690, { z: 0.82, cx: 700, cy: 1230, ry: -16, rx: 6 }),
  key(770, { z: 0.82, cx: 700, cy: 1230, ry: -16, rx: 6 }),
  key(792, {}),
  key(796, {}),
  key(818, { z: 2.0, fy: fieldC(Y.code, S_REF), cy: 960 }),
  key(1054, { z: 2.0, fy: fieldC(Y.code, S_REF), cy: 960 }),
  key(1078, { z: 1.45, fy: 400, cy: 1150 }),
  key(1102, { z: 1.45, fy: 400, cy: 1150 }),
  key(1126, { z: 1.5, fy: 560, cy: 1150 }),
  key(1178, { z: 1.5, fy: 560, cy: 1150 }),
  key(1200, {}),
];

const camAt = (frame: number): Cam => {
  const p = (k: keyof Cam) => track(frame, CAM_KEYS.map((c) => [c.f, c[k]] as [number, number]), smooth);
  return { z: p("z"), fx: p("fx"), fy: p("fy"), cx: p("cx"), cy: p("cy"), ry: p("ry"), rx: p("rx") };
};

/** Converte um ponto da tela do celular em coordenadas do quadro (sem inclinação). */
const toComp = (cam: Cam, x: number, y: number) => {
  const s = K * cam.z;
  return { x: cam.cx + (x - cam.fx) * s, y: cam.cy + (y - cam.fy) * s, s };
};

// Digitação ----------------------------------------------------------------
const URL_TOKENS = ["c", "a", "s", "t", "-", "a", "-", "w", "a", "y", ".com"];
const URL_PER = 2.6;
const urlTyped = (frame: number) => {
  if (frame < T.urlType) return "";
  const n = Math.min(URL_TOKENS.length, Math.floor((frame - T.urlType) / URL_PER) + 1);
  return URL_TOKENS.slice(0, n).join("");
};

const PER_NAME = 3;
const PER_EMAIL = 2;
const PER_PHONE = 2;

// Cada tecla acende no frame em que é digitada e apaga em KEY_FADE frames.
const KEY_FADE = 6;
type Press = { key: string; f: number };
const pressesOf = (start: number, chars: string[], per: number): Press[] =>
  chars.map((ch, i) => ({ key: ch.length === 1 ? ch.toUpperCase() : ch, f: start + i * per }));
const PRESSES: Press[] = [
  ...pressesOf(T.urlType, URL_TOKENS, URL_PER),
  ...pressesOf(T.fnType, COPY.firstName.split(""), PER_NAME),
  ...pressesOf(T.lnType, COPY.lastName.split(""), PER_NAME),
  ...pressesOf(T.emailType, COPY.email.split(""), PER_EMAIL),
  ...pressesOf(T.phoneType, COPY.phone.split(""), PER_PHONE),
];
const keyGlow = (frame: number): KeyGlow => {
  const glow: KeyGlow = {};
  for (const p of PRESSES) {
    const age = frame - p.f;
    if (age < 0 || age > KEY_FADE) continue;
    glow[p.key] = Math.max(glow[p.key] ?? 0, 1 - age / KEY_FADE);
  }
  return glow;
};

// Toque nos campos perto da borda direita, para o círculo não cobrir o texto digitado.
const FIELD_TAP_X = 318;

const NAT_ITEMS = COUNTRIES.map(([n]) => n);
const PRE_ITEMS = COUNTRIES.map(([n, c]) => `${n} (${c})`);

// SFX ----------------------------------------------------------------------
const SFX: SfxEvent[] = [
  { f: 0, src: "whoosh", vol: 0.6 },
  { f: T.urlTap, src: "tap" },
  ...keyClicks(T.urlType, URL_TOKENS.map(() => "x").join(""), URL_PER),
  { f: T.goTap, src: "tap" },
  { f: T.siteIn, src: "pop", vol: 0.5 },
  { f: T.cap2, src: "pop", vol: 0.4 },
  { f: T.menuTap, src: "tap" },
  { f: T.applyTap, src: "tap" },
  { f: T.nav, src: "whoosh", vol: 0.4 },
  { f: T.cap3, src: "pop", vol: 0.4 },
  { f: T.fnTap, src: "tap" },
  ...keyClicks(T.fnType, COPY.firstName, PER_NAME),
  { f: T.lnTap, src: "tap" },
  ...keyClicks(T.lnType, COPY.lastName, PER_NAME),
  { f: T.natTap, src: "tap" },
  { f: T.natTap + 16, src: "whoosh", vol: 0.25 },
  { f: T.natPick, src: "tap" },
  { f: T.natPick + 4, src: "ding", vol: 0.35 },
  { f: T.emailTap, src: "tap" },
  ...keyClicks(T.emailType, COPY.email, PER_EMAIL),
  { f: T.preTap, src: "tap" },
  { f: T.preTap + 16, src: "whoosh", vol: 0.25 },
  { f: T.prePick, src: "tap" },
  { f: T.prePick + 4, src: "ding", vol: 0.45 },
  { f: T.phoneTap, src: "tap" },
  ...keyClicks(T.phoneType, COPY.phone, PER_PHONE),
  { f: T.cap4, src: "whoosh", vol: 0.55 },
  { f: 690, src: "pop", vol: 0.35 },
  { f: 706, src: "pop", vol: 0.35 },
  { f: 722, src: "pop", vol: 0.35 },
  { f: 738, src: "pop", vol: 0.35 },
  { f: 754, src: "pop", vol: 0.35 },
  { f: T.cap5, src: "impact", vol: 0.9 },
  { f: T.card, src: "pop", vol: 0.5 },
  { f: T.lift + 4, src: "whoosh", vol: 0.45 },
  { f: T.land, src: "ding", vol: 0.7 },
  { f: T.benefits, src: "pop", vol: 0.45 },
  { f: T.benefits + 34, src: "pop", vol: 0.45 },
  { f: T.benefits + 68, src: "pop", vol: 0.45 },
  { f: T.cap6, src: "pop", vol: 0.4 },
  { f: T.igTap, src: "tap" },
  { f: T.captchaTap, src: "tap" },
  { f: T.sendTap, src: "tap" },
  { f: T.success + 2, src: "success", vol: 0.8 },
];

// ---------------------------------------------------------------------------

const clamp = { extrapolateLeft: "clamp", extrapolateRight: "clamp" } as const;

export const Walkthrough: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const cam = camAt(frame);
  const s = K * cam.z;

  // entrada do celular
  const enter = lerp(frame, [0, 26], [0, 1], out);

  // ----- estado do navegador -----
  const onApply = frame >= T.nav + 8;
  const collapse = lerp(frame, [T.nav, T.nav + 12], [0, 1]);
  const toolbar = 1 - collapse;
  const progress = lerp(frame, [T.goTap + 2, T.siteIn + 6], [0, 1], (t) => t);
  const urlText = urlTyped(frame);
  const urlFocused = frame >= T.urlTap && frame < T.goTap + 2;
  const siteShown = frame >= T.siteIn;
  const siteIn = lerp(frame, [T.siteIn, T.siteIn + 8], [0, 1]);

  // menu
  const menuOpen = frame < T.nav + 8 ? lerp(frame, [T.menuTap + 2, T.menuTap + 20], [0, 1], out) : 0;
  const applyActive = lerp(frame, [T.applyTap, T.applyTap + 5], [0, 1]);
  const navFlash = interpolate(frame, [T.nav, T.nav + 8, T.nav + 16], [0, 1, 0], clamp);

  // rolagem da página Apply
  const scroll = track(
    frame,
    [
      [T.nav + 14, 0],
      [T.nav + 46, S_CONTACTS],
      [680, S_CONTACTS],
      [772, S_REF],
      [1102, S_REF],
      [1126, S_SEND],
    ],
    smooth,
  );

  // ----- teclados -----
  type KbSpec = { up: number; down: number; variant: "text" | "email" | "url" | "phone" };
  const KBS: KbSpec[] = [
    { up: T.urlTap + 2, down: T.goTap + 2, variant: "url" },
    { up: T.fnTap + 2, down: 316, variant: "text" },
    { up: T.emailTap + 2, down: 468, variant: "email" },
    { up: T.phoneTap + 2, down: 656, variant: "phone" },
  ];
  const kb = KBS.find((k) => frame >= k.up && frame < k.down + 12);
  const kbY = kb ? lerp(frame, [kb.up, kb.up + 10], [KEYBOARD_H, 0], out) + lerp(frame, [kb.down, kb.down + 10], [0, KEYBOARD_H], smooth) : KEYBOARD_H;

  const glow = keyGlow(frame);
  let suggestion = "";
  if (frame >= T.fnType && frame < T.lnTap) suggestion = typed(frame, T.fnType, COPY.firstName, PER_NAME);
  if (frame >= T.lnType && frame < 316) suggestion = typed(frame, T.lnType, COPY.lastName, PER_NAME);

  // ----- pickers -----
  const natOpen = lerp(frame, [T.natTap + 2, T.natTap + 10], [0, 1], out) * (1 - lerp(frame, [T.natPick + 4, T.natPick + 12], [0, 1]));
  const natScroll = lerp(frame, [T.natTap + 14, T.natPick - 8], [0, scrollToRow(TARGET_COUNTRY)], smooth);
  const preOpen = lerp(frame, [T.preTap + 2, T.preTap + 10], [0, 1], out) * (1 - lerp(frame, [T.prePick + 4, T.prePick + 12], [0, 1]));
  const preScroll = lerp(frame, [T.preTap + 14, T.prePick - 8], [0, scrollToRow(TARGET_COUNTRY)], smooth);
  const pickerRowY = (fieldPageY: number) => sy(fieldPageY, S_CONTACTS) + FIELD_H + 6;

  // ----- estado do formulário -----
  const caretOn = Math.floor(frame / 15) % 2 === 0;
  let focus: ApplyState["focus"] = null;
  if (frame >= T.fnTap && frame < T.lnTap) focus = "firstName";
  else if (frame >= T.lnTap && frame < 316) focus = "lastName";
  else if (frame >= T.natTap && frame < T.natPick + 6) focus = "nationality";
  else if (frame >= T.emailTap && frame < 468) focus = "email";
  else if (frame >= T.preTap && frame < T.prePick + 6) focus = "prefix";
  else if (frame >= T.phoneTap && frame < 656) focus = "phone";
  else if (frame >= 816 && frame < T.land) focus = "code";

  const phoneTyped = typed(frame, T.phoneType, COPY.phone, PER_PHONE);
  const state: ApplyState = {
    firstName: typed(frame, T.fnType, COPY.firstName, PER_NAME),
    lastName: typed(frame, T.lnType, COPY.lastName, PER_NAME),
    nationality: frame >= T.natPick + 4 ? COPY.nationality : "",
    email: typed(frame, T.emailType, COPY.email, PER_EMAIL),
    prefix: frame >= T.prePick + 4 ? COPY.prefix : "",
    phone: phoneTyped.trimEnd(),
    code: frame >= T.land ? COPY.campaignCode : "",
    focus,
    caret: focus !== null && (caretOn || (frame >= T.fnType && frame < 316) || (frame >= T.emailType && frame < 468) || (frame >= T.phoneType && frame < 656)),
    flash: {
      nationality: interpolate(frame, [T.natPick + 4, T.natPick + 8, T.natPick + 30], [0, 1, 0], clamp),
      prefix: interpolate(frame, [T.prePick + 4, T.prePick + 8, T.prePick + 44], [0, 1, 0], clamp),
      code: frame >= T.land ? Math.max(interpolate(frame, [T.land, T.land + 4, T.land + 40], [0, 1, 0.35], clamp), frame < 1050 ? 0.35 + 0.25 * pulse(frame, T.land + 40, 40) : interpolate(frame, [1050, 1066], [0.35, 0], clamp)) : 0,
    },
    instagram: lerp(frame, [T.igTap, T.igTap + 5], [0, 1], backOut),
    captcha: frame < T.captchaTap + 1 ? "idle" : frame < T.captchaTap + 20 ? "loading" : "checked",
    captchaSpin: (frame - T.captchaTap) * 24,
    sendPressed: interpolate(frame, [T.sendTap, T.sendTap + 3, T.sendTap + 10], [0, 1, 1], clamp),
  };

  // ----- destaque do código (spotlight) -----
  const spot = lerp(frame, [800, 816], [0, 1]) * (1 - lerp(frame, [1050, 1066], [0, 1]));
  const codeTop = sy(CODE_RECT.y, S_REF);
  const warm = lerp(frame, [T.cap5, T.cap5 + 16], [0, 1]) * (1 - lerp(frame, [1050, 1070], [0, 1]));

  // ----- sucesso -----
  const ok = lerp(frame, [T.success, T.success + 14], [0, 1], out);

  // ----- toques (coordenadas da tela) -----
  const taps: [number, number, number][] = [
    [T.urlTap, 195, 75],
    [T.goTap, 333, SCREEN_H - KEYBOARD_H + 239],
    [T.menuTap, BURGER.x, contentTop(0) + BURGER.y],
    [T.applyTap, 110, contentTop(0) + APPLY_Y],
    [T.fnTap, FIELD_TAP_X, fieldC(Y.firstName)],
    [T.lnTap, FIELD_TAP_X, fieldC(Y.lastName)],
    [T.natTap, FIELD_TAP_X, fieldC(Y.nationality)],
    [T.natPick, 160, pickerRowY(Y.nationality) + (PICKER_ROW * PICKER_VISIBLE) / 2],
    [T.emailTap, FIELD_TAP_X, fieldC(Y.email)],
    [T.preTap, FIELD_TAP_X, fieldC(Y.prefix)],
    [T.prePick, 160, pickerRowY(Y.prefix) + (PICKER_ROW * PICKER_VISIBLE) / 2],
    [T.phoneTap, FIELD_TAP_X, fieldC(Y.phone)],
    [T.igTap, 28, sy(RADIO_INSTAGRAM_Y, S_REF)],
    [T.captchaTap, 46, sy(Y.captcha + 38, S_SEND)],
    [T.sendTap, 195, sy(Y.send + 28, S_SEND)],
  ];

  // posição do celular no quadro
  const tx = cam.cx - (BEZEL + cam.fx) * s;
  const ty = cam.cy - (BEZEL + cam.fy) * s + (1 - enter) * 1400;

  // Inclinação 3D só quando existe (entrada do celular e passo 4). Com o 3D sempre
  // ligado, o Chrome às vezes deixava "buracos" retangulares no celular durante o render.
  const rotX = cam.rx + (1 - enter) * 28;
  const tilted = Math.abs(rotX) > 0.01 || Math.abs(cam.ry) > 0.01;

  return (
    <AbsoluteFill style={{ fontFamily: F.raleway, overflow: "hidden" }}>
      <Background warm={warm} />

      {/* ---------------- celular + câmera ---------------- */}
      <AbsoluteFill style={tilted ? { perspective: 2600, perspectiveOrigin: `${cam.cx}px ${cam.cy}px` } : undefined}>
        <AbsoluteFill
          style={
            tilted
              ? { transformOrigin: `${cam.cx}px ${cam.cy}px`, transform: `rotateY(${cam.ry}deg) rotateX(${rotX}deg)` }
              : undefined
          }
        >
          <div style={{ position: "absolute", left: 0, top: 0, width: PHONE_W, height: PHONE_H, transformOrigin: "0 0", transform: `translate(${tx}px, ${ty}px) scale(${s})` }}>
            <Phone>
              {/* página inicial do navegador / site */}
              <div style={{ position: "absolute", left: 0, top: contentTop(collapse), width: SCREEN_W, height: SCREEN_H, overflow: "hidden" }}>
                {!onApply ? (
                  <>
                    <StartPage />
                    {siteShown ? (
                      <div style={{ position: "absolute", inset: 0, opacity: siteIn }}>
                        <HomePage />
                        <Menu open={menuOpen} active={applyActive} />
                        <SiteHeader menu={menuOpen} />
                      </div>
                    ) : null}
                  </>
                ) : (
                  <div style={{ position: "absolute", left: 0, top: -scroll, width: SCREEN_W }}>
                    <div style={{ position: "absolute", left: 0, top: 0, width: SCREEN_W }}>
                      <ApplyPage s={state} />
                    </div>
                    <SiteHeader menu={0} />
                  </div>
                )}
                <div style={{ position: "absolute", inset: 0, background: "#fff", opacity: navFlash, pointerEvents: "none" }} />
              </div>

              {/* spotlight do código de campanha */}
              {spot > 0 ? (
                <div
                  style={{
                    position: "absolute",
                    left: CODE_RECT.x - 8,
                    top: codeTop - 8,
                    width: CODE_RECT.w + 16,
                    height: CODE_RECT.h + 16,
                    borderRadius: 12,
                    boxShadow: `0 0 0 2000px rgba(4,18,36,${0.9 * spot})`,
                    border: `3px solid rgba(255,207,63,${spot})`,
                    outline: `${2 + 4 * pulse(frame, 816, 36)}px solid rgba(255,207,63,${0.35 * spot})`,
                    zIndex: 30,
                  }}
                />
              ) : null}

              {/* pickers */}
              <Picker
                items={NAT_ITEMS}
                header="Nationality as per passport*"
                x={24}
                y={pickerRowY(Y.nationality)}
                width={SCREEN_W - 48}
                open={natOpen}
                scroll={natScroll}
                active={frame >= T.natPick - 4 ? TARGET_COUNTRY : null}
              />
              <Picker
                items={PRE_ITEMS}
                header="Country prefix*"
                x={24}
                y={pickerRowY(Y.prefix)}
                width={SCREEN_W - 48}
                open={preOpen}
                scroll={preScroll}
                active={frame >= T.prePick - 4 ? TARGET_COUNTRY : null}
              />

              {/* sucesso */}
              {ok > 0 ? <SuccessSheet p={ok} frame={frame - T.success} /> : null}

              {/* teclado */}
              {kb ? (
                <div style={{ position: "absolute", left: 0, top: kbY, width: SCREEN_W, height: SCREEN_H, zIndex: 60 }}>
                  <Keyboard variant={kb.variant} glow={glow} suggestion={suggestion} returnPressed={kb.variant === "url" && frame >= T.goTap && frame < T.goTap + 4} />
                </div>
              ) : null}

              <BrowserChrome
                url={siteShown || frame >= T.goTap ? COPY.site : urlText || "Search or enter website name"}
                placeholder={!urlText && !(siteShown || frame >= T.goTap)}
                focused={urlFocused}
                caret={urlFocused && (caretOn || (frame >= T.urlType && frame < T.goTap))}
                collapse={collapse}
                toolbar={toolbar * (kb ? 0 : 1)}
                progress={progress}
              />

              {taps.map(([f, x, y]) => (
                <Touch key={f} frame={frame} at={f} x={x} y={y} />
              ))}
            </Phone>
          </div>
        </AbsoluteFill>
      </AbsoluteFill>

      {/* ---------------- passo 4: checklist ---------------- */}
      <Checklist frame={frame} />

      {/* ---------------- passo 5: anúncio + código voando + benefícios ---------------- */}
      <CampaignCode frame={frame} cam={cam} />

      {/* ---------------- confete ---------------- */}
      {frame >= T.success ? <Confetti frame={frame - T.success} /> : null}

      {/* ---------------- legendas ---------------- */}
      <Sequence from={6} durationInFrames={T.cap2 - 6} premountFor={fps}>
        <StepCaption step={1} title="Open cast-a-way.com" subs={[{ from: 0, text: "Use the *browser* on your phone" }]} duration={T.cap2 - 6} />
      </Sequence>
      <Sequence from={T.cap2} durationInFrames={T.cap3 - T.cap2} premountFor={fps}>
        <StepCaption step={2} title="Open the menu" subs={[{ from: 0, text: "Then tap *Apply Now!*" }]} duration={T.cap3 - T.cap2} />
      </Sequence>
      <Sequence from={T.cap3} durationInFrames={T.cap4 - T.cap3} premountFor={fps}>
        <StepCaption
          step={3}
          title="Fill in your contacts"
          subs={[
            { from: 0, text: "Start with your *name*" },
            { from: 330 - T.cap3, text: "*Nationality*: as in your passport" },
            { from: 470 - T.cap3, text: "*Country prefix*: so we know where you're calling from" },
            { from: 596 - T.cap3, text: "Phone with *WhatsApp* or *Telegram*" },
          ]}
          duration={T.cap4 - T.cap3}
        />
      </Sequence>
      <Sequence from={T.cap4} durationInFrames={T.cap5 - T.cap4} premountFor={fps}>
        <StepCaption step={4} title="Complete every section" subs={[{ from: 0, text: "Resume, survey, positions &amp; languages" }]} duration={T.cap5 - T.cap4} />
      </Sequence>
      <Sequence from={T.cap5} durationInFrames={T.cap6 - T.cap5} premountFor={fps}>
        <StepCaption
          step={5}
          alert
          title="Add the campaign code"
          subs={[
            { from: 0, text: "This one is *very important*" },
            { from: T.card - T.cap5, text: "Find it in the *job post* you saw" },
            { from: T.land + 8 - T.cap5, text: "It tells recruiters *which job* you want" },
          ]}
          duration={T.cap6 - T.cap5}
        />
      </Sequence>
      <Sequence from={T.cap6} durationInFrames={WALKTHROUGH_FRAMES - T.cap6} premountFor={fps}>
        <StepCaption
          step={6}
          title="Send your application"
          subs={[
            { from: 0, text: "Tell us *how you found us*" },
            { from: T.captchaTap - 6 - T.cap6, text: "Tick *I'm not a robot*, then tap *Send*" },
            { from: T.success - T.cap6, text: "*Done!* Your application is in" },
          ]}
          duration={WALKTHROUGH_FRAMES - T.cap6 + 20}
        />
      </Sequence>

      <Sfx events={SFX} />
    </AbsoluteFill>
  );
};

// ---------------------------------------------------------------------------

const StartPage: React.FC = () => (
  <div style={{ position: "absolute", inset: 0, background: "#1c1c1e", padding: "34px 22px", boxSizing: "border-box" }}>
    <div style={{ fontFamily: F.ui, fontWeight: 700, fontSize: 22, color: "#fff" }}>Favorites</div>
    <div style={{ display: "flex", gap: 22, marginTop: 18 }}>
      {["#3a3a3c", "#3a3a3c", "#3a3a3c", "#3a3a3c"].map((c, i) => (
        <div key={i} style={{ width: 66, height: 66, borderRadius: 15, background: c }} />
      ))}
    </div>
  </div>
);

const SuccessSheet: React.FC<{ p: number; frame: number }> = ({ p, frame }) => {
  const draw = interpolate(frame, [6, 20], [0, 1], { ...clamp, easing: out });
  return (
    <div style={{ position: "absolute", inset: 0, zIndex: 70 }}>
      <div style={{ position: "absolute", inset: 0, background: `rgba(10,30,55,${0.55 * p})` }} />
      <div
        style={{
          position: "absolute",
          left: 30,
          right: 30,
          top: 250,
          height: 330,
          borderRadius: 26,
          background: "#fff",
          boxShadow: "0 20px 60px rgba(0,0,0,0.35)",
          transform: `scale(${0.7 + 0.3 * p}) translateY(${(1 - p) * 60}px)`,
          opacity: p,
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          paddingTop: 40,
          boxSizing: "border-box",
        }}
      >
        <svg width="110" height="110" viewBox="0 0 110 110">
          <circle cx="55" cy="55" r="50" fill={C.green} opacity={0.15} />
          <circle cx="55" cy="55" r="40" fill={C.green} />
          <path
            d="M36 56 L50 70 L76 42"
            stroke="#fff"
            strokeWidth="8"
            fill="none"
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeDasharray="70"
            strokeDashoffset={70 * (1 - draw)}
          />
        </svg>
        <div style={{ fontFamily: F.raleway, fontWeight: 800, fontSize: 28, color: "#1d3557", marginTop: 18 }}>Application sent!</div>
        <div style={{ fontFamily: F.openSans, fontSize: 16, color: C.muted, marginTop: 10, textAlign: "center", padding: "0 30px" }}>
          Good luck, {COPY.firstName}! Our recruiters will review your profile.
        </div>
      </div>
    </div>
  );
};

const CHECKS = ["Consents & policies", "Resume: PDF with photo", "Survey: answer truthfully", "Up to 3 job positions", "Languages you speak"];

const Checklist: React.FC<{ frame: number }> = ({ frame }) => {
  if (frame < 680 || frame > 800) return null;
  const exit = lerp(frame, [772, 790], [0, 1]);
  return (
    <>
      {CHECKS.map((label, i) => {
        const at = 690 + i * 16;
        const p = lerp(frame, [at, at + 12], [0, 1], backOut);
        const tick = lerp(frame, [at + 6, at + 14], [0, 1], out);
        return (
          <div
            key={label}
            style={{
              position: "absolute",
              left: 64,
              top: 690 + i * 132,
              display: "flex",
              alignItems: "center",
              gap: 20,
              padding: "20px 30px 20px 20px",
              borderRadius: 26,
              background: "rgba(255,255,255,0.97)",
              boxShadow: "0 16px 40px rgba(0,0,0,0.28)",
              opacity: Math.min(1, p * 1.4) * (1 - exit),
              transform: `translateX(${(1 - p) * -120 - exit * 80}px) scale(${0.8 + 0.2 * p})`,
              transformOrigin: "0% 50%",
              zIndex: 15,
            }}
          >
            <div style={{ width: 58, height: 58, borderRadius: 58, background: C.green, display: "flex", alignItems: "center", justifyContent: "center" }}>
              <IconCheck size={36} color="#fff" stroke={3.6} style={{ opacity: tick, transform: `scale(${0.5 + 0.5 * tick})` }} />
            </div>
            <div style={{ fontFamily: F.raleway, fontWeight: 800, fontSize: 42, color: "#14324f", whiteSpace: "nowrap" }}>
              <span style={{ color: C.brand }}>0{i + 2}</span> {label}
            </div>
          </div>
        );
      })}
    </>
  );
};

const CampaignCode: React.FC<{ frame: number; cam: Cam }> = ({ frame, cam }) => {
  if (frame < T.card - 2 || frame > 1070) return null;
  const cardIn = lerp(frame, [T.card, T.card + 18], [0, 1], out);
  const cardOut = lerp(frame, [T.land + 8, T.land + 24], [0, 1], smooth);
  const CARD = { x: 110, y: 1170, w: 860 };
  const chipPos = { x: CARD.x + 520, y: CARD.y + 312 }; // centro-esquerda do chip no anúncio

  // destino: início do texto dentro do campo
  const target = toComp(cam, CODE_RECT.x + 1.5 + 14 + 12, sy(CODE_RECT.y, S_REF) + FIELD_H / 2);
  const fly = lerp(frame, [T.lift + 4, T.land], [0, 1], Easing2);
  const lift = lerp(frame, [T.lift, T.lift + 6], [0, 1], out);
  const flying = frame >= T.lift && frame < T.land + 1;
  const arc = Math.sin(fly * Math.PI) * -160;
  const fx = chipPos.x + (target.x - chipPos.x) * fly;
  const fy = chipPos.y + (target.y - chipPos.y) * fly + arc - lift * 20;
  const chipScale = 1 + 0.12 * lift - 0.12 * fly + ((15.5 * target.s) / 44 - 1) * fly;

  return (
    <>
      {/* anúncio da vaga */}
      {cardOut < 1 ? (
        <div
          style={{
            position: "absolute",
            left: CARD.x,
            top: CARD.y,
            width: CARD.w,
            borderRadius: 30,
            background: "#fff",
            overflow: "hidden",
            boxShadow: "0 30px 70px rgba(0,0,0,0.45)",
            opacity: cardIn * (1 - cardOut),
            transform: `translateY(${(1 - cardIn) * 260 + cardOut * 120}px) rotate(${(1 - cardIn) * 6 - 1.5}deg) scale(${1 - cardOut * 0.1})`,
            zIndex: 16,
          }}
        >
          <div style={{ display: "flex", alignItems: "center", gap: 16, padding: "18px 24px" }}>
            <div style={{ width: 62, height: 62, borderRadius: 62, background: "linear-gradient(45deg,#f9ce34,#ee2a7b,#6228d7)", padding: 3, boxSizing: "border-box" }}>
              <div style={{ width: "100%", height: "100%", borderRadius: 60, background: "#fff", padding: 2, boxSizing: "border-box" }}>
                <Porthole size={52} />
              </div>
            </div>
            <div style={{ fontFamily: F.ui, fontWeight: 700, fontSize: 32, color: "#111" }}>castawayhiring</div>
            <div style={{ marginLeft: "auto", fontFamily: F.ui, fontSize: 36, color: "#111", letterSpacing: 2 }}>•••</div>
          </div>
          <div
            style={{
              height: 180,
              background: `linear-gradient(135deg, ${C.brandDark}, ${C.brand} 60%, ${C.ring})`,
              display: "flex",
              flexDirection: "column",
              justifyContent: "center",
              padding: "0 40px",
              position: "relative",
              overflow: "hidden",
            }}
          >
            <div style={{ fontFamily: F.oswald, fontWeight: 600, fontSize: 38, letterSpacing: 4, color: C.yellow }}>NOW HIRING</div>
            <div style={{ fontFamily: F.oswald, fontWeight: 700, fontSize: 92, lineHeight: 1, color: "#fff" }}>{COPY.jobTitle.toUpperCase()}</div>
            <div style={{ position: "absolute", right: 30, top: 30, opacity: 0.95 }}>
              <Porthole size={140} />
            </div>
          </div>
          <div style={{ display: "flex", alignItems: "center", gap: 18, padding: "26px 28px 30px" }}>
            <div style={{ fontFamily: F.ui, fontSize: 32, color: "#222", lineHeight: 1.25 }}>
              Apply at <b>cast-a-way.com</b>
              <br />
              Campaign code:
            </div>
            <div
              style={{
                marginLeft: "auto",
                padding: "12px 22px",
                borderRadius: 14,
                border: `3px dashed ${flying || frame >= T.land ? "#d9b13a" : "transparent"}`,
                background: flying || frame >= T.land ? "#fff8dd" : C.yellow,
                fontFamily: F.oswald,
                fontWeight: 700,
                fontSize: 44,
                color: flying || frame >= T.land ? "transparent" : "#1b1b1b",
                boxShadow: flying ? "none" : `0 0 0 ${6 * pulse(frame, T.card + 10, 24)}px rgba(255,207,63,0.45)`,
              }}
            >
              {COPY.campaignCode}
            </div>
          </div>
        </div>
      ) : null}

      {/* código voando até o campo */}
      {flying ? (
        <div
          style={{
            position: "absolute",
            left: fx,
            top: fy,
            transform: `translate(${-14 * (1 - fly)}px, -50%) scale(${chipScale})`,
            transformOrigin: "0% 50%",
            padding: `${12 * (1 - fly)}px ${22 * (1 - fly)}px`,
            borderRadius: 14,
            background: `rgba(255,207,63,${1 - fly * 0.85})`,
            boxShadow: `0 ${20 * (1 - fly)}px 40px rgba(0,0,0,${0.35 * (1 - fly)})`,
            fontFamily: fly > 0.85 ? F.openSans : F.oswald,
            fontWeight: fly > 0.85 ? 400 : 700,
            fontSize: 44,
            color: "#1b1b1b",
            whiteSpace: "nowrap",
            zIndex: 18,
          }}
        >
          {COPY.campaignCode}
        </div>
      ) : null}

      {/* benefícios */}
      {[
        { icon: <IconTarget size={52} color="#1b1b1b" />, text: "Shows which job you're applying for" },
        { icon: <IconBolt size={52} color="#1b1b1b" />, text: "Your application may get priority" },
        { icon: <IconEye size={52} color="#1b1b1b" />, text: "More visibility with recruiters" },
      ].map((b, i) => {
        const at = T.benefits + i * 34;
        const p = lerp(frame, [at, at + 14], [0, 1], backOut);
        const exit = lerp(frame, [1044, 1060], [0, 1]);
        if (frame < at) return null;
        return (
          <div
            key={b.text}
            style={{
              position: "absolute",
              left: 80,
              right: 80,
              top: 1130 + i * 145,
              display: "flex",
              alignItems: "center",
              gap: 28,
              opacity: Math.min(1, p * 1.5) * (1 - exit),
              transform: `translateY(${(1 - p) * 60}px)`,
              zIndex: 17,
            }}
          >
            <div
              style={{
                width: 100,
                height: 100,
                borderRadius: 100,
                background: C.yellow,
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                flexShrink: 0,
                boxShadow: "0 10px 26px rgba(0,0,0,0.3)",
                transform: `scale(${0.6 + 0.4 * p})`,
              }}
            >
              {b.icon}
            </div>
            <div style={{ fontFamily: F.raleway, fontWeight: 800, fontSize: 50, lineHeight: 1.1, color: "#fff", textShadow: "0 3px 16px rgba(0,0,0,0.5)" }}>{b.text}</div>
          </div>
        );
      })}
    </>
  );
};

const Easing2 = (t: number) => (t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2);

const Confetti: React.FC<{ frame: number }> = ({ frame }) => {
  const colors = [C.yellow, C.ring, "#ffffff", C.green, "#ff7b7b", C.brand];
  return (
    <>
      {new Array(70).fill(0).map((_, i) => {
        const a = (i * 137.5 * Math.PI) / 180;
        const v = 18 + ((i * 53) % 23);
        const t = frame;
        const x = 540 + Math.cos(a) * v * t * 0.9;
        const y = 900 + Math.sin(a) * v * t * 0.7 - 30 * t + 0.9 * t * t;
        const op = interpolate(frame, [0, 4, 40, 60], [0, 1, 1, 0], clamp);
        return (
          <div
            key={i}
            style={{
              position: "absolute",
              left: x,
              top: y,
              width: 16 + (i % 3) * 6,
              height: 9 + (i % 2) * 5,
              borderRadius: 3,
              background: colors[i % colors.length],
              opacity: op,
              transform: `rotate(${t * (8 + (i % 7) * 3)}deg)`,
              zIndex: 25,
            }}
          />
        );
      })}
    </>
  );
};
