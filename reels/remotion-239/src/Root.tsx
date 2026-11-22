import { Composition } from "remotion";
import { PadsReel } from "./Composition";
import { TOTAL_FRAMES } from "./clips.generated";

export const RemotionRoot: React.FC = () => {
  return (
    <Composition
      id="PadsReel239"
      component={PadsReel}
      durationInFrames={TOTAL_FRAMES}
      fps={30}
      width={1080}
      height={1920}
    />
  );
};
