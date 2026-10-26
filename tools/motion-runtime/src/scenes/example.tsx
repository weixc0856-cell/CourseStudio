import {Grid, Line, makeScene2D, Txt} from '@motion-canvas/2d';
import {all, createRef, easeOutCubic, waitFor} from '@motion-canvas/core';
import {theme} from '../theme';

const ORIGIN: [number, number] = [0, 0];
const A_TIP: [number, number] = [360, -180];
const B_TIP: [number, number] = [120, -300];
const SUM_TIP: [number, number] = [480, -480];

/**
 * Template segment: 45 seconds, geometric build, explicit hold beats.
 * Real episodes should keep each segment within 45-90 seconds.
 */
export default makeScene2D(function* (view) {
  view.fill(theme.background);

  const grid = createRef<Grid>();
  const vecA = createRef<Line>();
  const vecB = createRef<Line>();
  const vecBShift = createRef<Line>();
  const vecSum = createRef<Line>();
  const parallelogram = createRef<Line>();
  const title = createRef<Txt>();
  const labelA = createRef<Txt>();
  const labelB = createRef<Txt>();
  const labelBShift = createRef<Txt>();
  const labelSum = createRef<Txt>();
  const caption = createRef<Txt>();

  view.add(
    <>
      <Grid
        ref={grid}
        width={1920}
        height={1080}
        spacing={[80, 80]}
        stroke={theme.grid}
        lineWidth={1}
        end={0}
      />

      <Txt
        ref={title}
        text={'向量加法：把两个箭头接起来'}
        fill={theme.ink}
        fontFamily={theme.fontFamily}
        fontSize={theme.fontSize.title}
        y={-430}
        opacity={0}
      />

      <Line
        ref={vecA}
        points={[ORIGIN, A_TIP]}
        stroke={theme.accent}
        lineWidth={8}
        endArrow
        arrowSize={26}
        end={0}
      />
      <Txt
        ref={labelA}
        text={'a'}
        fill={theme.accent}
        fontFamily={theme.fontFamily}
        fontSize={theme.fontSize.label}
        x={390}
        y={-190}
        opacity={0}
      />

      <Line
        ref={vecB}
        points={[ORIGIN, B_TIP]}
        stroke={theme.highlight}
        lineWidth={8}
        endArrow
        arrowSize={26}
        end={0}
      />
      <Txt
        ref={labelB}
        text={'b'}
        fill={theme.highlight}
        fontFamily={theme.fontFamily}
        fontSize={theme.fontSize.label}
        x={150}
        y={-310}
        opacity={0}
      />

      <Line
        ref={parallelogram}
        points={[ORIGIN, A_TIP, SUM_TIP, B_TIP]}
        closed
        fill={theme.accentSoft}
        stroke={theme.muted}
        lineWidth={2}
        opacity={0}
      />

      <Line
        ref={vecBShift}
        points={[A_TIP, SUM_TIP]}
        stroke={theme.highlight}
        lineWidth={6}
        endArrow
        arrowSize={22}
        end={0}
      />
      <Txt
        ref={labelBShift}
        text={'b'}
        fill={theme.highlight}
        fontFamily={theme.fontFamily}
        fontSize={theme.fontSize.label}
        x={530}
        y={-360}
        opacity={0}
      />

      <Line
        ref={vecSum}
        points={[ORIGIN, SUM_TIP]}
        stroke={theme.accent}
        lineWidth={10}
        endArrow
        arrowSize={30}
        end={0}
      />
      <Txt
        ref={labelSum}
        text={'a + b'}
        fill={theme.ink}
        fontFamily={theme.fontFamily}
        fontSize={theme.fontSize.body}
        x={520}
        y={-540}
        opacity={0}
      />
      <Txt
        ref={caption}
        text={'先沿 a 走，再沿 b 走；终点就是 a + b'}
        fill={theme.muted}
        fontFamily={theme.fontFamily}
        fontSize={theme.fontSize.caption}
        y={360}
        opacity={0}
      />
    </>,
  );

  // 0-5s: establish the grid and the question.
  yield* title().opacity(1, 1);
  yield* grid().end(1, 2);
  yield* waitFor(2);

  // 5-10s: build a.
  yield* all(vecA().end(1, 2, easeOutCubic), labelA().opacity(1, 1));
  yield* waitFor(3);

  // 10-15s: build b.
  yield* all(vecB().end(1, 2, easeOutCubic), labelB().opacity(1, 1));
  yield* waitFor(3);

  // 15-23s: translate b and reveal the parallelogram.
  yield* parallelogram().opacity(1, 2);
  yield* all(vecBShift().end(1, 2, easeOutCubic), labelBShift().opacity(1, 1));
  yield* waitFor(4);

  // 23-33s: draw the resultant and state the rule.
  yield* all(vecSum().end(1, 3, easeOutCubic), labelSum().opacity(1, 1));
  yield* caption().opacity(1, 1.5);
  yield* waitFor(5.5);

  // 33-45s: one clear emphasis, then a long hold for narration.
  yield* all(vecSum().lineWidth(14, 1), vecSum().stroke(theme.highlight, 1));
  yield* waitFor(5);
  yield* all(vecSum().lineWidth(10, 1), vecSum().stroke(theme.accent, 1));
  yield* waitFor(5);
});
