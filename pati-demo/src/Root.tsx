import { Composition } from "remotion";
import { PatiDemo } from "./PatiDemo";
import { DURATION_IN_SECONDS, VIDEO } from "./config";

export const RemotionRoot: React.FC = () => {
  return (
    <Composition
      id="PatiDemo"
      component={PatiDemo}
      durationInFrames={Math.round(DURATION_IN_SECONDS * VIDEO.fps)}
      fps={VIDEO.fps}
      width={VIDEO.width}
      height={VIDEO.height}
    />
  );
};
