import { Audio } from "@remotion/media";
import { AbsoluteFill, interpolate, staticFile, useCurrentFrame, useVideoConfig } from "remotion";
import { Edit } from "./edit.generated";

const Music: React.FC = () => {
  const frame = useCurrentFrame();
  const { durationInFrames } = useVideoConfig();
  return (
    <Audio
      name="Music"
      src={staticFile("music.wav")}
      volume={interpolate(frame, [0, 20, durationInFrames - 45, durationInFrames - 1], [0, 0.8, 0.8, 0], {
        extrapolateLeft: "clamp",
        extrapolateRight: "clamp",
      })}
    />
  );
};

const FadeInOut: React.FC = () => {
  const frame = useCurrentFrame();
  const { durationInFrames } = useVideoConfig();
  return (
    <AbsoluteFill
      style={{
        backgroundColor: "black",
        opacity: interpolate(frame, [0, 12, durationInFrames - 30, durationInFrames - 1], [1, 0, 0, 1], {
          extrapolateLeft: "clamp",
          extrapolateRight: "clamp",
        }),
      }}
    />
  );
};

export const FriendVideo: React.FC = () => (
  <AbsoluteFill style={{ backgroundColor: "black" }}>
    <Edit />
    <FadeInOut />
    <Music />
  </AbsoluteFill>
);
