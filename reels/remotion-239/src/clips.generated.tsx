// Generated from tools/picks.json: one sequence per full combination (hard cuts, real speed).
import {Video} from "@remotion/media";
import {TransitionSeries} from "@remotion/transitions";
import {staticFile} from "remotion";

export const TOTAL_FRAMES = 1188;

export const PadClips: React.FC = () => {
  return (
    <TransitionSeries name="Pad combos">
      <TransitionSeries.Sequence name="00 punches > high kick > knee (opener)" durationInFrames={110}>
        <Video name="a0505 @55.14s" src={staticFile("clips/c00.mp4")} volume={1} objectFit="cover" />
      </TransitionSeries.Sequence>
      <TransitionSeries.Sequence name="01 10-strike combo" durationInFrames={137}>
        <Video name="a0514 @1.64s" src={staticFile("clips/c01.mp4")} volume={1} objectFit="cover" />
      </TransitionSeries.Sequence>
      <TransitionSeries.Sequence name="02 kicks + punches" durationInFrames={92}>
        <Video name="a0506 @106.84s" src={staticFile("clips/c02.mp4")} volume={1} objectFit="cover" />
      </TransitionSeries.Sequence>
      <TransitionSeries.Sequence name="03 punches > kick x2" durationInFrames={106}>
        <Video name="a0505 @17.79s" src={staticFile("clips/c03.mp4")} volume={1} objectFit="cover" />
      </TransitionSeries.Sequence>
      <TransitionSeries.Sequence name="04 punch, kick, knee" durationInFrames={89}>
        <Video name="a0506 @33.22s" src={staticFile("clips/c04.mp4")} volume={1} objectFit="cover" />
      </TransitionSeries.Sequence>
      <TransitionSeries.Sequence name="05 11-strike combo" durationInFrames={158}>
        <Video name="a0509 @3.13s" src={staticFile("clips/c05.mp4")} volume={1} objectFit="cover" />
      </TransitionSeries.Sequence>
      <TransitionSeries.Sequence name="06 punch combo" durationInFrames={102}>
        <Video name="a0505 @71.46s" src={staticFile("clips/c06.mp4")} volume={1} objectFit="cover" />
      </TransitionSeries.Sequence>
      <TransitionSeries.Sequence name="07 punches, close" durationInFrames={95}>
        <Video name="a0506 @146.14s" src={staticFile("clips/c07.mp4")} volume={1} objectFit="cover" />
      </TransitionSeries.Sequence>
      <TransitionSeries.Sequence name="08 10-strike combo" durationInFrames={116}>
        <Video name="a0515 @6.33s" src={staticFile("clips/c08.mp4")} volume={1} objectFit="cover" />
      </TransitionSeries.Sequence>
      <TransitionSeries.Sequence name="09 punches > kick" durationInFrames={65}>
        <Video name="a0505 @82.65s" src={staticFile("clips/c09.mp4")} volume={1} objectFit="cover" />
      </TransitionSeries.Sequence>
      <TransitionSeries.Sequence name="10 punches > kick" durationInFrames={80}>
        <Video name="a0514 @7.65s" src={staticFile("clips/c10.mp4")} volume={1} objectFit="cover" />
      </TransitionSeries.Sequence>
      <TransitionSeries.Sequence name="11 high kick (finisher)" durationInFrames={38}>
        <Video name="a0505 @88.97s" src={staticFile("clips/c11.mp4")} volume={1} objectFit="cover" />
      </TransitionSeries.Sequence>
    </TransitionSeries>
  );
};
