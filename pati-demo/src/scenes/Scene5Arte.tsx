import React from "react";
import { useVideoConfig } from "remotion";
import { ASSETS, COLORS, LAYOUT, TEXTS, TIMING } from "../config";
import { nb, sec } from "../anim";
import { Emphasis } from "../components/Text";
import {
  PatiBlock,
  PatiMessage,
  RecoCard,
  Thumb,
  UserMessage,
} from "../components/Messages";

/** Cena 5 (25–35 s): arte da fogueira -> emoção abre, linha de apoio prova substância. */
export const Scene5Arte: React.FC = () => {
  const { fps } = useVideoConfig();
  const t = TIMING.test3;
  const x = TEXTS.test3;
  return (
    <div data-anchor="t3">
      <UserMessage
        anchor="t3-user"
        at={sec(t.send, fps)}
        attachment={
          <Thumb
            src={ASSETS.artImage}
            aspect={ASSETS.artAspect}
            height={LAYOUT.artThumbHeight}
          />
        }
      >
        {x.user}
      </UserMessage>
      <PatiMessage
        anchor="t3-pati"
        thinkingAt={sec(t.thinking, fps)}
        firstBlockAt={sec(t.reply1, fps)}
      >
        <PatiBlock anchor="t3-r1" at={sec(t.reply1, fps)}>
          {x.reply1}
        </PatiBlock>
        <PatiBlock anchor="t3-r2" at={sec(t.reply2, fps)}>
          {nb(x.reply2)}
        </PatiBlock>
        <RecoCard anchor="t3-reco" at={sec(t.reco, fps)}>
          <Emphasis text={x.reco} words={x.recoEmphasis} />
        </RecoCard>
        <RecoCard
          anchor="t3-sug"
          at={sec(t.suggestion, fps)}
          label={x.suggestionLabel}
          size={24}
        >
          <span style={{ fontWeight: 500, color: COLORS.text }}>
            “{x.suggestion}”
          </span>
        </RecoCard>
      </PatiMessage>
    </div>
  );
};
