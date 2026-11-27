import { Composition } from "remotion";
import { ShakeReel } from "./Composition";
import { TOTAL_FRAMES } from "./edit.generated";

export const RemotionRoot: React.FC = () => (
  <Composition id="ProteinShakeReel" component={ShakeReel} durationInFrames={TOTAL_FRAMES} fps={30} width={1080} height={1920} />
);
