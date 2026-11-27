import { Video } from "@remotion/media";
import { loadFont } from "@remotion/fonts";
import {
  AbsoluteFill,
  Easing,
  interpolate,
  Sequence,
  staticFile,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";

export const FONT = "Heebo";
loadFont({ family: FONT, url: staticFile("fonts/heebo-hebrew.woff2"), weight: "300 900", unicodeRange: "U+0307-0308, U+0590-05FF, U+200C-2010, U+20AA, U+25CC, U+FB1D-FB4F" });
loadFont({ family: FONT, url: staticFile("fonts/heebo-latin.woff2"), weight: "300 900", unicodeRange: "U+0000-00FF, U+2000-206F" });
loadFont({ family: "Emoji", url: staticFile("fonts/NotoColorEmoji.ttf") });
const FAMILY = `${FONT}, Emoji`;
const ease = Easing.bezier(0.16, 1, 0.3, 1);
const clamp = { extrapolateLeft: "clamp", extrapolateRight: "clamp" } as const;

// One shot of the source video with a gentle push-in towards `origin` (percent x/y).
export const Shot: React.FC<{ name?: string; trimBefore: number; zoom: number[]; origin: number[]; volume: number }> = ({ name, trimBefore, zoom, origin, volume }) => {
  const frame = useCurrentFrame();
  const { durationInFrames } = useVideoConfig();
  return (
    <AbsoluteFill style={{ overflow: "hidden" }}>
      <AbsoluteFill
        style={{
          scale: interpolate(frame, [0, durationInFrames], [zoom[0], zoom[1]], clamp),
          transformOrigin: `${origin[0]}% ${origin[1]}%`,
        }}
      >
        <Video name={name} src={staticFile("source.mp4")} trimBefore={trimBefore} volume={volume} objectFit="cover" />
      </AbsoluteFill>
    </AbsoluteFill>
  );
};

const pop = (frame: number) => ({
  opacity: interpolate(frame, [0, 4], [0, 1], clamp),
  scale: interpolate(frame, [0, 6], [0.92, 1], { ...clamp, easing: ease }),
});

// Spoken-word caption: upper-middle (chest level) - below the ingredient label, clear of the Reels UI and of the counter work.
export const Caption: React.FC<{ from: number; durationInFrames: number; text: string }> = ({ from, durationInFrames, text }) => (
  <Sequence from={from} durationInFrames={durationInFrames} layout="none">
    <CaptionInner text={text} />
  </Sequence>
);
const CaptionInner: React.FC<{ text: string }> = ({ text }) => {
  const frame = useCurrentFrame();
  return (
    <AbsoluteFill style={{ justifyContent: "flex-start", alignItems: "center", paddingTop: 470, paddingLeft: 90, paddingRight: 90 }}>
      <div
        dir="rtl"
        lang="he"
        style={{
          ...pop(frame),
          fontFamily: FAMILY,
          fontWeight: 800,
          fontSize: 66,
          lineHeight: 1.18,
          color: "white",
          textAlign: "center",
          background: "rgba(0,0,0,0.55)",
          padding: "14px 30px 18px",
          borderRadius: 22,
          maxWidth: 900,
        }}
      >
        {text}
      </div>
    </AbsoluteFill>
  );
};

// Ingredient + amount, exactly as said in the video. Top area, clear of face/hands.
export const Label: React.FC<{ text: string; sub?: string }> = ({ text, sub }) => {
  const frame = useCurrentFrame();
  return (
    <AbsoluteFill style={{ justifyContent: "flex-start", alignItems: "center", paddingTop: 250 }}>
      <div
        dir="rtl"
        lang="he"
        style={{
          opacity: interpolate(frame, [0, 6], [0, 1], clamp),
          translate: interpolate(frame, [0, 8], ["0px -20px", "0px 0px"], { ...clamp, easing: ease }),
          fontFamily: FAMILY,
          textAlign: "center",
          background: "rgba(255,255,255,0.93)",
          color: "#1a1a1a",
          padding: "16px 34px 18px",
          borderRadius: 26,
          boxShadow: "0 8px 30px rgba(0,0,0,0.25)",
        }}
      >
        <div style={{ fontSize: 56, fontWeight: 800 }}>{text}</div>
        {sub ? <div style={{ fontSize: 42, fontWeight: 600, color: "#B7791F", marginTop: 2 }}>{sub}</div> : null}
      </div>
    </AbsoluteFill>
  );
};

export const Title: React.FC<{ text: string }> = ({ text }) => {
  const frame = useCurrentFrame();
  return (
    <AbsoluteFill style={{ justifyContent: "flex-start", alignItems: "center", paddingTop: 300, paddingLeft: 80, paddingRight: 80 }}>
      <div
        dir="rtl"
        lang="he"
        style={{
          ...pop(frame),
          fontFamily: FAMILY,
          fontWeight: 900,
          fontSize: 92,
          lineHeight: 1.12,
          color: "white",
          textAlign: "center",
          textShadow: "0 6px 28px rgba(0,0,0,0.75), 0 2px 6px rgba(0,0,0,0.6)",
        }}
      >
        {text}
      </div>
    </AbsoluteFill>
  );
};

export const Cta: React.FC<{ text: string }> = ({ text }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  return (
    <Sequence from={Math.round(0.6 * fps)} layout="none">
      <AbsoluteFill style={{ justifyContent: "center", alignItems: "center", paddingLeft: 80, paddingRight: 80 }}>
        <div
          dir="rtl"
          lang="he"
          style={{
            ...pop(Math.max(0, frame - Math.round(0.6 * fps))),
            fontFamily: FAMILY,
            fontWeight: 900,
            fontSize: 84,
            lineHeight: 1.15,
            color: "#1a1a1a",
            textAlign: "center",
            background: "rgba(255,255,255,0.94)",
            padding: "26px 44px 30px",
            borderRadius: 30,
            boxShadow: "0 10px 40px rgba(0,0,0,0.3)",
          }}
        >
          {text}
        </div>
      </AbsoluteFill>
    </Sequence>
  );
};
