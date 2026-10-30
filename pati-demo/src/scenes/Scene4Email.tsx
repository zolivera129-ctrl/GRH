import React from "react";
import { useVideoConfig } from "remotion";
import { COLORS, TEXTS, TIMING } from "../config";
import { nb, sec } from "../anim";
import {
  PatiBlock,
  PatiMessage,
  RecoCard,
  UserMessage,
} from "../components/Messages";

/** Cena 4 (teste 2): dois assuntos de e-mail -> assunto sugerido. */
export const Scene4Email: React.FC = () => {
  const { fps } = useVideoConfig();
  const t = TIMING.test2;
  const x = TEXTS.test2;
  const option = (o: { label: string; text: string }) => (
    <div style={{ display: "flex", gap: 10, marginTop: 6 }}>
      <span style={{ fontWeight: 600, whiteSpace: "nowrap" }}>{o.label} -</span>
      <span>{nb(o.text)}</span>
    </div>
  );
  return (
    <div data-anchor="t2">
      <UserMessage anchor="t2-user" at={sec(t.send, fps)}>
        <div style={{ marginBottom: 10 }}>{nb(x.userIntro)}</div>
        {option(x.optionA)}
        {option(x.optionB)}
      </UserMessage>
      <PatiMessage
        anchor="t2-pati"
        thinkingAt={sec(t.thinking, fps)}
        firstBlockAt={sec(t.reply1, fps)}
      >
        <PatiBlock anchor="t2-r1" at={sec(t.reply1, fps)}>
          {x.reply1}
        </PatiBlock>
        <PatiBlock anchor="t2-r2" at={sec(t.reply2, fps)}>
          {x.reply2}
        </PatiBlock>
        <RecoCard
          anchor="t2-sol"
          at={sec(t.solution, fps)}
          label={x.solutionLabel}
          size={32}
          note={
            <span style={{ color: COLORS.textSoft }}>{x.solutionNote}</span>
          }
          noteAt={sec(t.solutionNote, fps)}
        >
          {x.solution}
        </RecoCard>
      </PatiMessage>
    </div>
  );
};
