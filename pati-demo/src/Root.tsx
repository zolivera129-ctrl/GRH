import { Composition } from "remotion";
import { PatiDemo } from "./PatiDemo";
import { VIDEO } from "./config";

export const RemotionRoot: React.FC = () => {
  return (
    <Composition
      id="PatiDemo"
      component={PatiDemo}
      durationInFrames={VIDEO.durationInSeconds * VIDEO.fps}
      fps={VIDEO.fps}
      width={VIDEO.width}
      height={VIDEO.height}
    />
  );
};
