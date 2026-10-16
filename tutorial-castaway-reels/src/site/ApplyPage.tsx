import React from "react";
import {
  IconChevronDown,
  IconFile,
  IconGlobe,
  IconMail,
  IconPhone,
  IconUpload,
  IconUser,
  IconUserCheck,
  IconCheck,
} from "../components/Icons";
import { SCREEN_W } from "../components/Phone";
import { C, F } from "../theme";
import { HEADER_H } from "./SiteHeader";

const PAD = 20;
const INNER = SCREEN_W - PAD * 2;
export const FIELD_H = 46;

/** Posições verticais (coordenadas da página) de cada bloco do formulário. */
export const Y = {
  intro: HEADER_H + 26,
  contacts: 362,
  firstName: 405,
  lastName: 465,
  nationality: 525,
  email: 585,
  prefix: 645,
  phone: 705,
  consents: 792,
  documents: 1050,
  survey: 1470,
  jobs: 1880,
  languages: 2160,
  referral: 2440,
  codeLabel: 2502,
  code: 2556,
  hear: 2630,
  instagram: 2730,
  send: 3010,
  captcha: 3090,
  footer: 3220,
  end: 3420,
};
/** Altura de cada radio da pergunta "How did you hear about us?" */
const HEAR_ROWS: [string, number][] = [
  ["Google", 32],
  ["Facebook", 32],
  ["Instagram", 32],
  ["LinkedIn", 32],
  ["I have a friend or family member who has been recruited by Cast-A-Way before", 48],
  ["I am related to a Cast-A-Way staff member", 32],
  ["I am related to someone who works for the cruising industry, who referred me to Cast-A-Way", 66],
  ["Others", 32],
];
/** Centro vertical do radio "Instagram" (coordenadas da página). */
export const RADIO_INSTAGRAM_Y = Y.hear + 36 + 32 * 2 + 9;

export type FieldId = "firstName" | "lastName" | "nationality" | "email" | "prefix" | "phone" | "code" | null;

export type ApplyState = {
  firstName: string;
  lastName: string;
  nationality: string;
  email: string;
  prefix: string;
  phone: string;
  code: string;
  focus: FieldId;
  caret: boolean;
  flash: Partial<Record<Exclude<FieldId, null>, number>>;
  instagram: number;
  captcha: "idle" | "loading" | "checked";
  captchaSpin: number;
  sendPressed: number;
};

const Heading: React.FC<{ y: number; children: React.ReactNode; size?: number }> = ({ y, children, size = 22 }) => (
  <div
    style={{
      position: "absolute",
      left: PAD,
      top: y,
      width: INNER,
      fontFamily: F.raleway,
      fontWeight: 400,
      fontSize: size,
      lineHeight: 1.3,
      color: C.heading,
    }}
  >
    {children}
  </div>
);

const Field: React.FC<{
  y: number;
  icon: React.ReactNode;
  placeholder: string;
  value: string;
  select?: boolean;
  focused?: boolean;
  caret?: boolean;
  flash?: number;
}> = ({ y, icon, placeholder, value, select = false, focused = false, caret = false, flash = 0 }) => (
  <div
    style={{
      position: "absolute",
      left: PAD,
      top: y,
      width: INNER,
      height: FIELD_H,
      boxSizing: "border-box",
      border: `1.5px solid ${focused ? C.brand : C.field}`,
      borderRadius: 3,
      background: flash > 0 ? `rgba(255,207,63,${0.35 * flash})` : "#fff",
      boxShadow: focused ? "0 0 0 3px rgba(44,130,200,0.18)" : flash > 0 ? `0 0 0 ${4 * flash}px rgba(255,190,40,${0.55 * flash})` : "none",
      display: "flex",
      alignItems: "center",
      gap: 12,
      padding: "0 14px",
      fontFamily: F.openSans,
      fontSize: 15.5,
      color: value ? "#222" : C.muted,
    }}
  >
    {icon}
    <div style={{ flex: 1, whiteSpace: "nowrap", overflow: "hidden", display: "flex", alignItems: "center" }}>
      {value || (caret ? "" : placeholder)}
      {caret ? <span style={{ display: "inline-block", width: 2, height: 21, background: "#0a84ff", marginLeft: 1 }} /> : null}
      {!value && caret ? <span style={{ color: C.muted, marginLeft: 2 }}>{placeholder}</span> : null}
    </div>
    {select ? <IconChevronDown size={16} color="#333" /> : null}
  </div>
);

const Check: React.FC<{ y: number; checked?: boolean; children: React.ReactNode; h?: number; round?: boolean; fill?: number }> = ({
  y,
  checked = false,
  children,
  round = false,
  fill,
}) => {
  const f = fill ?? (checked ? 1 : 0);
  return (
    <div
      style={{
        position: "absolute",
        left: PAD,
        top: y,
        width: INNER,
        display: "flex",
        gap: 10,
        fontFamily: F.openSans,
        fontSize: 14.5,
        lineHeight: 1.12,
        color: "#333",
      }}
    >
      <div
        style={{
          width: 16,
          height: 16,
          marginTop: 1,
          flexShrink: 0,
          borderRadius: round ? 16 : 3,
          border: `1.5px solid ${f > 0.5 ? C.brand : "#9aa0a6"}`,
          background: round ? "#fff" : f > 0.5 ? C.brand : "#fff",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          boxSizing: "border-box",
        }}
      >
        {round ? (
          <div style={{ width: 8 * f, height: 8 * f, borderRadius: 8, background: C.brand }} />
        ) : f > 0.5 ? (
          <IconCheck size={12} color="#fff" stroke={4} />
        ) : null}
      </div>
      <div>{children}</div>
    </div>
  );
};

const YesNo: React.FC<{ y: number }> = ({ y }) => (
  <>
    <div style={{ position: "absolute", left: PAD, top: y }}>
      <Check y={0} round checked>
        YES
      </Check>
    </div>
    <div style={{ position: "absolute", left: PAD + 80, top: y }}>
      <Check y={0} round>
        NO
      </Check>
    </div>
  </>
);

const Para: React.FC<{ y: number; children: React.ReactNode; size?: number; color?: string }> = ({ y, children, size = 14.5, color = "#333" }) => (
  <div style={{ position: "absolute", left: PAD, top: y, width: INNER, fontFamily: F.openSans, fontSize: size, lineHeight: 1.45, color }}>{children}</div>
);

/** Página "Apply Now" do site (sem o cabeçalho), com estado dos campos. */
export const ApplyPage: React.FC<{ s: ApplyState }> = ({ s }) => {
  const iconC = "#333";
  return (
    <div style={{ position: "absolute", left: 0, top: 0, width: SCREEN_W, height: Y.end, background: C.page }}>
      <Heading y={Y.intro} size={27}>
        Do You Want To Work On A Cruise Ship?
      </Heading>
      <Para y={Y.intro + 84}>
        If you want to apply for one of our vacancies, fill out the form below and{" "}
        <b>it is essential that you attach your complete resume</b> to increase your chances!
      </Para>

      {/* 01 */}
      <Heading y={Y.contacts}>01. Contacts</Heading>
      <Field
        y={Y.firstName}
        icon={<IconUser size={16} color={iconC} />}
        placeholder="First Name *"
        value={s.firstName}
        focused={s.focus === "firstName"}
        caret={s.focus === "firstName" && s.caret}
      />
      <Field
        y={Y.lastName}
        icon={<IconUserCheck size={17} color={iconC} />}
        placeholder="Last Name *"
        value={s.lastName}
        focused={s.focus === "lastName"}
        caret={s.focus === "lastName" && s.caret}
      />
      <Field
        y={Y.nationality}
        icon={<IconGlobe size={16} color={iconC} />}
        placeholder="Nationality as per passport*"
        value={s.nationality}
        select
        focused={s.focus === "nationality"}
        flash={s.flash.nationality}
      />
      <Field
        y={Y.email}
        icon={<IconMail size={16} color={iconC} />}
        placeholder="Your best email (this will be your login) *"
        value={s.email}
        focused={s.focus === "email"}
        caret={s.focus === "email" && s.caret}
      />
      <Field
        y={Y.prefix}
        icon={<span style={{ width: 0 }} />}
        placeholder="Country prefix*"
        value={s.prefix}
        select
        focused={s.focus === "prefix"}
        flash={s.flash.prefix}
      />
      <Field
        y={Y.phone}
        icon={<IconPhone size={16} color={iconC} />}
        placeholder="Phone with WhatsApp or Telegram *"
        value={s.phone}
        focused={s.focus === "phone"}
        caret={s.focus === "phone" && s.caret}
      />

      {/* 02 */}
      <Heading y={Y.consents}>02. Consents &amp; Policies</Heading>
      <Check y={Y.consents + 46} checked>
        I am 21 years old or will turn 21 within the next 6 months.*
      </Check>
      <Check y={Y.consents + 92} checked>
        I have read and agree to the <b style={{ color: "#7a5a00" }}>Privacy Policy</b>.*
      </Check>
      <Check y={Y.consents + 122} checked>
        I have read and agree to the <b style={{ color: "#7a5a00" }}>Complaints Policy</b>.*
      </Check>
      <Check y={Y.consents + 152} checked>
        I have read and agree to the <b style={{ color: "#7a5a00" }}>Costs involved in obtaining the required onboarding documentation</b>.*
      </Check>
      <Check y={Y.consents + 198} checked>
        I have read and agree to the <b style={{ color: "#7a5a00" }}>NO FEE Statement</b>.*
      </Check>

      {/* 03 */}
      <Heading y={Y.documents}>03. Documents and Personal Information</Heading>
      <Para y={Y.documents + 70}>Click or drag here, your PDF resume with photo, to upload: *</Para>
      <div
        style={{
          position: "absolute",
          left: PAD,
          top: Y.documents + 122,
          width: INNER,
          height: 120,
          border: "2px dashed #b9c3cc",
          borderRadius: 6,
          boxSizing: "border-box",
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          justifyContent: "center",
          gap: 10,
          background: "#fff",
        }}
      >
        <IconUpload size={26} color="#333" />
        <div
          style={{
            display: "flex",
            alignItems: "center",
            gap: 8,
            padding: "6px 12px",
            borderRadius: 20,
            background: "#e9f4ec",
            color: "#1f7a3c",
            fontFamily: F.openSans,
            fontWeight: 600,
            fontSize: 13.5,
          }}
        >
          <IconFile size={18} color="#c0392b" />
          Maria_Santos_Resume.pdf
          <IconCheck size={14} color="#1f7a3c" stroke={4} />
        </div>
      </div>
      <Field y={Y.documents + 262} icon={<span />} placeholder="Marital Status*" value="Single" select />
      <Field y={Y.documents + 322} icon={<span />} placeholder="Gender as per passport*" value="Female" select />

      {/* 04 */}
      <Heading y={Y.survey}>
        04. Survey – Please read carefully the following questions, make sure you understand them and answer truthfully
      </Heading>
      <Para y={Y.survey + 128}>
        Are you willing to work onboard a ship for 10 to 34 weeks away from your family and friends, working 10-12 hours a day, 7 days a week?
      </Para>
      <YesNo y={Y.survey + 222} />
      <Para y={Y.survey + 262}>Do you have any Technical Certification?</Para>
      <YesNo y={Y.survey + 292} />
      <Para y={Y.survey + 332}>Have you received two or more Covid-19 vaccinations and can provide proof?</Para>
      <YesNo y={Y.survey + 382} />

      {/* 05 */}
      <Heading y={Y.jobs}>05. Job Positions</Heading>
      <Para y={Y.jobs + 44}>Choose up to 3 job positions you can handle: *</Para>
      <Field y={Y.jobs + 80} icon={<span />} placeholder="Choose Position 1" value="Bartender" select />
      <Field y={Y.jobs + 140} icon={<span />} placeholder="Choose Position 2" value="" select />
      <Field y={Y.jobs + 200} icon={<span />} placeholder="Choose Position 3" value="" select />

      {/* 06 */}
      <Heading y={Y.languages}>06. Languages</Heading>
      <Para y={Y.languages + 44}>Select at least one language you speak:</Para>
      {["Arabic", "Chinese (Mandarin)", "English", "French", "German", "Spanish"].map((l, i) => (
        <Check key={l} y={Y.languages + 80 + i * 30} checked={l === "English"}>
          {l}
        </Check>
      ))}

      {/* 07 */}
      <Heading y={Y.referral}>07. Referral &amp; Campaign Information</Heading>
      <Para y={Y.codeLabel} size={15}>
        Campaign code (Applications submitted with a campaign code may be given priority)
      </Para>
      <Field
        y={Y.code}
        icon={<span style={{ width: 0 }} />}
        placeholder=""
        value={s.code}
        focused={s.focus === "code"}
        caret={s.focus === "code" && s.caret}
        flash={s.flash.code}
      />
      <Para y={Y.hear} size={15.5}>
        How did you hear about us? <span style={{ textDecoration: "underline" }}>*</span>
      </Para>
      {HEAR_ROWS.reduce<{ y: number; els: React.ReactNode[] }>(
        (acc, [label, h]) => {
          acc.els.push(
            <Check key={label} y={acc.y} round fill={label === "Instagram" ? s.instagram : 0}>
              {label}
            </Check>,
          );
          acc.y += h;
          return acc;
        },
        { y: Y.hear + 36, els: [] },
      ).els}

      {/* enviar */}
      <div
        style={{
          position: "absolute",
          left: PAD,
          top: Y.send,
          width: INNER,
          height: 56,
          borderRadius: 2,
          background: s.sendPressed > 0.5 ? C.buttonPressed : `linear-gradient(180deg, #64a8e2, ${C.button} 55%, #4a8ccc)`,
          boxShadow: "0 4px 10px rgba(0,0,0,0.15)",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          fontFamily: F.openSans,
          fontSize: 17,
          letterSpacing: 0.5,
          color: "#fff",
          transform: `scale(${1 - 0.04 * s.sendPressed})`,
        }}
      >
        SEND YOUR RESUME
      </div>

      {/* reCAPTCHA (genérico) */}
      <div
        style={{
          position: "absolute",
          left: PAD,
          top: Y.captcha,
          width: 300,
          height: 76,
          borderRadius: 3,
          border: "1px solid #d3d3d3",
          background: "#f9f9f9",
          boxShadow: "0 0 4px rgba(0,0,0,0.08)",
          display: "flex",
          alignItems: "center",
          padding: "0 12px",
          boxSizing: "border-box",
          gap: 12,
          fontFamily: F.ui,
          fontSize: 14,
          color: "#222",
        }}
      >
        <div style={{ width: 28, height: 28, position: "relative" }}>
          {s.captcha === "idle" ? (
            <div style={{ width: 26, height: 26, border: "2px solid #c1c1c1", borderRadius: 3, background: "#fff" }} />
          ) : s.captcha === "loading" ? (
            <div
              style={{
                width: 26,
                height: 26,
                borderRadius: 26,
                border: "3px solid #d6e4f5",
                borderTopColor: "#4a90e2",
                boxSizing: "border-box",
                transform: `rotate(${s.captchaSpin}deg)`,
              }}
            />
          ) : (
            <IconCheck size={32} color="#1fa463" stroke={3.6} style={{ marginTop: -4 }} />
          )}
        </div>
        I&apos;m not a robot
        <div style={{ marginLeft: "auto", display: "flex", flexDirection: "column", alignItems: "center", gap: 2 }}>
          <svg width="30" height="30" viewBox="0 0 24 24">
            <path d="M12 3a9 9 0 0 1 8.5 6" stroke="#4a90e2" strokeWidth="3" fill="none" />
            <path d="M21 12a9 9 0 0 1-6 8.5" stroke="#1c3aa9" strokeWidth="3" fill="none" />
            <path d="M12 21a9 9 0 0 1-8.6-6.5" stroke="#b4b4b4" strokeWidth="3" fill="none" />
            <path d="M3 12a9 9 0 0 1 4-7.5" stroke="#4a90e2" strokeWidth="3" fill="none" />
          </svg>
          <div style={{ fontSize: 8.5, color: "#555" }}>reCAPTCHA</div>
        </div>
      </div>

      <div
        style={{
          position: "absolute",
          left: 0,
          width: SCREEN_W,
          top: Y.footer - 30,
          height: 2,
          background: "linear-gradient(90deg, transparent, #c9ced3, transparent)",
        }}
      />
      <div
        style={{
          position: "absolute",
          left: 0,
          width: SCREEN_W,
          top: Y.footer,
          textAlign: "center",
          fontFamily: F.raleway,
          fontWeight: 400,
          fontSize: 38,
          color: C.heading,
        }}
      >
        Do You Want To
      </div>
    </div>
  );
};

/** Retângulo (coordenadas da página) do campo do código de campanha. */
export const CODE_RECT = { x: PAD, y: Y.code, w: INNER, h: FIELD_H };
export const FIELD_X = PAD;
export const FIELD_W = INNER;
