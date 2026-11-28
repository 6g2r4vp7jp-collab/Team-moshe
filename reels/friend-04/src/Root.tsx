import { Composition } from "remotion";
import { FriendVideo } from "./Composition";
import { TOTAL_FRAMES } from "./edit.generated";

export const RemotionRoot: React.FC = () => (
  <Composition id="FriendVideo04" component={FriendVideo} durationInFrames={TOTAL_FRAMES} fps={30} width={1080} height={1920} />
);
