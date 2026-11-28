import { Video } from "@remotion/media";
import { AbsoluteFill, Img, interpolate, useCurrentFrame, useVideoConfig } from "remotion";

const clamp = { extrapolateLeft: "clamp", extrapolateRight: "clamp" } as const;

// Video clip, full frame, original look (no zoom), muted - music only.
export const Clip: React.FC<{ name?: string; src: string }> = ({ name, src }) => (
  <AbsoluteFill>
    <Video name={name} src={src} muted objectFit="cover" />
  </AbsoluteFill>
);

// Still photo with a slow, gentle Ken Burns move (max 7%).
export const Photo: React.FC<{ name?: string; src: string; from: number; to: number }> = ({ src, from, to }) => {
  const frame = useCurrentFrame();
  const { durationInFrames } = useVideoConfig();
  return (
    <AbsoluteFill style={{ overflow: "hidden", backgroundColor: "black" }}>
      <Img
        src={src}
        style={{
          width: "100%",
          height: "100%",
          objectFit: "cover",
          scale: interpolate(frame, [0, durationInFrames], [from, to], clamp),
        }}
      />
    </AbsoluteFill>
  );
};
