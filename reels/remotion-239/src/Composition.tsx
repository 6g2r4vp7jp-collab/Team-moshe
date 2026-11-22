import { Audio } from "@remotion/media";
import { loadFont } from "@remotion/fonts";
import {
  AbsoluteFill,
  Easing,
  Img,
  interpolate,
  staticFile,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import { PadClips } from "./clips.generated";

// Heebo variable font served locally (render machine cannot reach Google Fonts).
const fontFamily = "Heebo";
loadFont({ family: fontFamily, url: staticFile("fonts/heebo-hebrew.woff2"), weight: "300 900", unicodeRange: "U+0307-0308, U+0590-05FF, U+200C-2010, U+20AA, U+25CC, U+FB1D-FB4F" });
loadFont({ family: fontFamily, url: staticFile("fonts/heebo-latin.woff2"), weight: "300 900", unicodeRange: "U+0000-00FF, U+2000-206F" });
const GOLD = "#D9B45A";

const ease = Easing.bezier(0.16, 1, 0.3, 1);

const OpeningTitle: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const opacity = interpolate(frame, [0.15 * fps, 0.55 * fps, 2.1 * fps, 2.5 * fps], [0, 1, 1, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  return (
    <AbsoluteFill style={{ justifyContent: "flex-start", alignItems: "center", paddingTop: 260 }}>
      <div
        dir="rtl"
        lang="he"
        style={{
          fontFamily,
          opacity,
          translate: interpolate(frame, [0.15 * fps, 0.7 * fps], ["0px 24px", "0px 0px"], {
            extrapolateLeft: "clamp",
            extrapolateRight: "clamp",
            easing: ease,
          }),
          textAlign: "center",
          color: GOLD,
          textShadow: "0 4px 24px rgba(0,0,0,0.7)",
        }}
      >
        <div style={{ fontSize: 92, fontWeight: 800, letterSpacing: 2 }}>כוח. מהירות. דיוק.</div>
        <div style={{ width: 160, height: 4, background: GOLD, margin: "22px auto 0", opacity: 0.85 }} />
      </div>
    </AbsoluteFill>
  );
};

const EndCard: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const opacity = interpolate(frame, [0, 0.5 * fps], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: ease,
  });
  return (
    <AbsoluteFill style={{ opacity }}>
      <AbsoluteFill style={{ background: "linear-gradient(to top, rgba(0,0,0,0.88) 0%, rgba(0,0,0,0.35) 45%, rgba(0,0,0,0) 70%)" }} />
      <AbsoluteFill style={{ justifyContent: "flex-end", alignItems: "center", paddingBottom: 300 }}>
        <Img src={staticFile("logo.png")} style={{ width: 300, height: 300, filter: "drop-shadow(0 6px 22px rgba(0,0,0,0.7))" }} />
        <div style={{ fontFamily, fontWeight: 800, fontSize: 64, letterSpacing: 14, color: GOLD, marginTop: 10 }}>TEAM MOSHE</div>
      </AbsoluteFill>
    </AbsoluteFill>
  );
};

const MusicBed: React.FC = () => {
  const frame = useCurrentFrame();
  const { durationInFrames } = useVideoConfig();
  return (
    <Audio
      name="Music"
      src={staticFile("music.wav")}
      volume={interpolate(frame, [0, 8, durationInFrames - 30, durationInFrames - 1], [0, 0.42, 0.42, 0], {
        extrapolateLeft: "clamp",
        extrapolateRight: "clamp",
      })}
    />
  );
};

export const PadsReel: React.FC = () => {
  const { fps, durationInFrames } = useVideoConfig();
  return (
    <AbsoluteFill style={{ backgroundColor: "black" }}>
      <PadClips />
      <AbsoluteFill name="Title" durationInFrames={Math.round(2.5 * fps)}>
        <OpeningTitle />
      </AbsoluteFill>
      <AbsoluteFill name="End card" from={durationInFrames - Math.round(2.4 * fps)}>
        <EndCard />
      </AbsoluteFill>
      <MusicBed />
    </AbsoluteFill>
  );
};
