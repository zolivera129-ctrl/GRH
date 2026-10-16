import React from "react";
import { Composition, Folder } from "remotion";
import { TUTORIAL_FRAMES, Tutorial } from "./Tutorial";
import { HOOK_FRAMES, Hook } from "./scenes/Hook";
import { OUTRO_FRAMES, Outro } from "./scenes/Outro";
import { WALKTHROUGH_FRAMES, Walkthrough } from "./scenes/Walkthrough";

export const RemotionRoot: React.FC = () => {
  return (
    <>
      <Composition id="CastawayApplyReel" component={Tutorial} durationInFrames={TUTORIAL_FRAMES} fps={30} width={1080} height={1920} />
      <Folder name="Scenes">
        <Composition id="Hook" component={Hook} durationInFrames={HOOK_FRAMES} fps={30} width={1080} height={1920} />
        <Composition id="Walkthrough" component={Walkthrough} durationInFrames={WALKTHROUGH_FRAMES} fps={30} width={1080} height={1920} />
        <Composition id="Outro" component={Outro} durationInFrames={OUTRO_FRAMES} fps={30} width={1080} height={1920} />
      </Folder>
    </>
  );
};
