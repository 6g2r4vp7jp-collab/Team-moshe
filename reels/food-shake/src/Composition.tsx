import { Audio } from "@remotion/media";
import { AbsoluteFill, interpolate, staticFile, useCurrentFrame, useVideoConfig } from "remotion";
import { Edit } from "./edit.generated";

const MusicBed: React.FC = () => {
  const frame = useCurrentFrame();
  const { durationInFrames } = useVideoConfig();
  return (
    <Audio
      name="Music (soft, under the voice)"
      src={staticFile("music.wav")}
      volume={interpolate(frame, [0, 10, durationInFrames - 30, durationInFrames - 1], [0, 0.13, 0.13, 0], {
        extrapolateLeft: "clamp",
        extrapolateRight: "clamp",
      })}
    />
  );
};

export const ShakeReel: React.FC = () => (
  <AbsoluteFill style={{ backgroundColor: "black" }}>
    <Edit />
    <MusicBed />
  </AbsoluteFill>
);
