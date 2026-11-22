// Generated from tools/picks.json: one sequence per full combination (hard cuts, real speed).
import {Video} from "@remotion/media";
import {TransitionSeries} from "@remotion/transitions";
import {staticFile} from "remotion";

export const TOTAL_FRAMES = 899;

export const PadClips: React.FC = () => {
  return (
    <TransitionSeries name="Pad combos">
      <TransitionSeries.Sequence name="00 kicks + punches (opener, fastest/hardest)" durationInFrames={88}>
        <Video name="a0506 @106.99s" src={staticFile("clips/c00.mp4")} volume={1} objectFit="cover" />
      </TransitionSeries.Sequence>
      <TransitionSeries.Sequence name="01 punches > kick" durationInFrames={65}>
        <Video name="a0505 @82.65s" src={staticFile("clips/c01.mp4")} volume={1} objectFit="cover" />
      </TransitionSeries.Sequence>
      <TransitionSeries.Sequence name="02 punches > kick x2" durationInFrames={106}>
        <Video name="a0505 @17.79s" src={staticFile("clips/c02.mp4")} volume={1} objectFit="cover" />
      </TransitionSeries.Sequence>
      <TransitionSeries.Sequence name="03 punch, kick, knee" durationInFrames={89}>
        <Video name="a0506 @33.22s" src={staticFile("clips/c03.mp4")} volume={1} objectFit="cover" />
      </TransitionSeries.Sequence>
      <TransitionSeries.Sequence name="04 10-strike combo" durationInFrames={116}>
        <Video name="a0515 @6.33s" src={staticFile("clips/c04.mp4")} volume={1} objectFit="cover" />
      </TransitionSeries.Sequence>
      <TransitionSeries.Sequence name="05 10-strike combo" durationInFrames={137}>
        <Video name="a0514 @1.64s" src={staticFile("clips/c05.mp4")} volume={1} objectFit="cover" />
      </TransitionSeries.Sequence>
      <TransitionSeries.Sequence name="06 punch combo" durationInFrames={102}>
        <Video name="a0505 @71.46s" src={staticFile("clips/c06.mp4")} volume={1} objectFit="cover" />
      </TransitionSeries.Sequence>
      <TransitionSeries.Sequence name="07 11-strike combo" durationInFrames={158}>
        <Video name="a0509 @3.13s" src={staticFile("clips/c07.mp4")} volume={1} objectFit="cover" />
      </TransitionSeries.Sequence>
      <TransitionSeries.Sequence name="08 high kick (finisher)" durationInFrames={38}>
        <Video name="a0505 @88.97s" src={staticFile("clips/c08.mp4")} volume={1} objectFit="cover" />
      </TransitionSeries.Sequence>
    </TransitionSeries>
  );
};
