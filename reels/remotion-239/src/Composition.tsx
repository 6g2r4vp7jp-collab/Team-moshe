import { Audio } from "@remotion/media";
import {
  AbsoluteFill,
  interpolate,
  staticFile,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import { PadClips } from "./clips.generated";

// Clean version: footage + sound only (no captions, no logo).

const MusicBed: React.FC = () => {
  const frame = useCurrentFrame();
  const { durationInFrames } = useVideoConfig();
  return (
    <Audio
      name="Music"
      src={staticFile("music.wav")}
      volume={interpolate(frame, [0, 8, durationInFrames - 30, durationInFrames - 1], [0, 0.28, 0.28, 0], {
        extrapolateLeft: "clamp",
        extrapolateRight: "clamp",
      })}
    />
  );
};

const FadeOut: React.FC = () => {
  const frame = useCurrentFrame();
  const { durationInFrames, fps } = useVideoConfig();
  return (
    <AbsoluteFill
      name="Fade out"
      style={{
        backgroundColor: "black",
        opacity: interpolate(frame, [durationInFrames - 0.4 * fps, durationInFrames - 1], [0, 1], {
          extrapolateLeft: "clamp",
          extrapolateRight: "clamp",
        }),
      }}
    />
  );
};

export const PadsReel: React.FC = () => {
  return (
    <AbsoluteFill style={{ backgroundColor: "black" }}>
      <PadClips />
      <FadeOut />
      <MusicBed />
    </AbsoluteFill>
  );
};
