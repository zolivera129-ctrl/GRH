import React from "react";
import { useCurrentFrame, useVideoConfig } from "remotion";
import { ASSETS, LAYOUT, STORY_PRIVACY_MASKS, TEXTS, TIMING } from "../config";
import { sec } from "../anim";
import { MarkedText, Emphasis } from "../components/Text";
import {
  PatiBlock,
  PatiMessage,
  RecoCard,
  Thumb,
  UserMessage,
} from "../components/Messages";

/** Cena 3 (9–17 s): story da palestra -> "Eu pararia nesse gancho." */
export const Scene3Palestra: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const t = TIMING.test1;
  const x = TEXTS.test1;
  const marks = [
    { phrase: x.userMarks[0], start: sec(t.mark1, fps) },
    { phrase: x.userMarks[1], start: sec(t.mark2, fps) },
  ];
  return (
    <div data-anchor="t1">
      <UserMessage
        anchor="t1-user"
        at={sec(t.send, fps)}
        attachment={
          <Thumb
            src={ASSETS.storyImage}
            aspect={ASSETS.storyAspect}
            height={LAYOUT.storyThumbHeight}
            masks={STORY_PRIVACY_MASKS}
          />
        }
      >
        <MarkedText text={x.user} marks={marks} frame={frame} />
      </UserMessage>
      <PatiMessage
        anchor="t1-pati"
        thinkingAt={sec(t.thinking, fps)}
        firstBlockAt={sec(t.reply1, fps)}
      >
        <PatiBlock anchor="t1-r1" at={sec(t.reply1, fps)} strong>
          {x.reply1}
        </PatiBlock>
        <PatiBlock anchor="t1-r2" at={sec(t.reply2, fps)}>
          {x.reply2}
        </PatiBlock>
        <RecoCard anchor="t1-reco" at={sec(t.reco, fps)}>
          <Emphasis text={x.reco} words={x.recoEmphasis} />
        </RecoCard>
      </PatiMessage>
    </div>
  );
};
