import { Composition } from "remotion";
import { PatiDemo } from "./PatiDemo";

export const RemotionRoot: React.FC = () => {
  return (
    <Composition
      id="PatiDemo"
      component={PatiDemo}
      durationInFrames={38 * 30}
      fps={30}
      width={1920}
      height={1080}
    />
  );
};
