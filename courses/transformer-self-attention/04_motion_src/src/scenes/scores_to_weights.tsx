import {Line, Node, Rect, Txt, makeScene2D} from '@motion-canvas/2d';
import {
  all,
  createRef,
  easeInOutCubic,
  easeOutCubic,
  waitFor,
  type ThreadGenerator,
} from '@motion-canvas/core';
import {theme} from '../theme';

/**
 * M5 / scores_to_weights — 68 seconds.
 *
 * Frozen toy example from 01_research/03-knowledge-structure.md:
 *   n = 4, d_k = 4, d_v = 2, sqrt(d_k) = 2
 *
 * The segment stops at the weight matrix A. It never draws O = A V.
 */
const SCORES = [
  [6, 0, 0, 0],
  [0, 4, 2, 0],
  [2, 2, 2, 2],
  [0, 0, 2, 4],
];

const SCALED = [
  [3, 0, 0, 0],
  [0, 2, 1, 0],
  [1, 1, 1, 1],
  [0, 0, 1, 2],
];

const WEIGHTS = [
  [0.87, 0.043, 0.043, 0.043],
  [0.083, 0.61, 0.225, 0.083],
  [0.25, 0.25, 0.25, 0.25],
  [0.083, 0.083, 0.225, 0.61],
];

const CELL_W = 104;
const CELL_H = 86;
const CELL_GAP = 8;
const ROWS = 4;
const COLS = 4;
const MATRIX_W = CELL_W * COLS + CELL_GAP * (COLS - 1);
const MATRIX_H = CELL_H * ROWS + CELL_GAP * (ROWS - 1);
const S_X = -420;
const S_Y = -40;
const A_X = 330;
const A_Y = -40;

const CELL_FILL = '#FFFFFF';
const CELL_STROKE = 'rgba(26, 26, 26, 0.18)';
const WEIGHT_FILL = 'rgba(232, 119, 34, 0.08)';
const WEIGHT_STROKE = 'rgba(232, 119, 34, 0.38)';
const WARM_HIGHLIGHT = 'rgba(180, 83, 9, 0.12)';

const cellX = (column: number) => (column - 1.5) * (CELL_W + CELL_GAP);
const cellY = (row: number) => (row - 1.5) * (CELL_H + CELL_GAP);
const rowIndices = (row: number) => [0, 1, 2, 3].map(column => row * 4 + column);
const weightColor = (row: number) =>
  row === 0 ? theme.accent : row === 2 ? theme.highlight : theme.ink;

export default makeScene2D(function* (view) {
  view.fill(theme.background);

  // Authoring clock. Every beat waits for exactly its declared duration, so the
  // scene lands on 68.0 s without relying on the editor timeline.
  let now = 0;
  function* beat(seconds: number, task?: ThreadGenerator) {
    if (task) {
      yield* all(task, waitFor(seconds));
    } else {
      yield* waitFor(seconds);
    }
    now += seconds;
  }
  function* holdTo(target: number) {
    const delta = target - now;
    if (delta < -0.001) {
      throw new Error(`timeline overrun: now=${now}s target=${target}s`);
    }
    if (delta > 0) {
      yield* waitFor(delta);
    }
    now = target;
  }

  const title = createRef<Txt>();
  const tokenGroup = createRef<Node>();
  const scoreGroup = createRef<Node>();
  const weightGroup = createRef<Node>();
  const arrowGroup = createRef<Node>();

  const scoreRects = SCORES.flat().map(() => createRef<Rect>());
  const scoreOrigTexts = SCORES.flat().map(() => createRef<Txt>());
  const scoreScaledTexts = SCORES.flat().map(() => createRef<Txt>());
  const weightRects = WEIGHTS.flat().map(() => createRef<Rect>());
  const weightTexts = WEIGHTS.flat().map(() => createRef<Txt>());

  const scoreRowHighlight = createRef<Rect>();
  const weightRow1Highlight = createRef<Rect>();
  const weightRow3Highlight = createRef<Rect>();
  const sSubRaw = createRef<Txt>();
  const sSubScaled = createRef<Txt>();
  const q1Caption = createRef<Txt>();
  const q1ScaledCaption = createRef<Txt>();
  const scaleFormula = createRef<Txt>();
  const scaleDetail = createRef<Txt>();
  const scaleRule = createRef<Txt>();
  const arrowLine = createRef<Line>();
  const arrowLabel = createRef<Txt>();
  const aRow1Label = createRef<Txt>();
  const aRow3Label = createRef<Txt>();
  const bottomCaption = createRef<Txt>();

  view.add(
    <>
      <Txt
        ref={title}
        text={'Self-attention：从 score 到权重'}
        fill={theme.ink}
        fontFamily={theme.fontFamily}
        fontSize={56}
        fontWeight={600}
        y={-490}
        opacity={0}
      />

      <Node ref={tokenGroup} y={-420} opacity={0}>
        {[0, 1, 2, 3].map(index => (
          <Rect
            x={(index - 1.5) * 136}
            width={112}
            height={64}
            radius={12}
            fill={theme.accentSoft}
            stroke={theme.accent}
            lineWidth={2}
          />
        ))}
        {[0, 1, 2, 3].map(index => (
          <Txt
            text={`t${index + 1}`}
            x={(index - 1.5) * 136}
            fill={theme.ink}
            fontFamily={theme.monoFamily}
            fontSize={32}
            textAlign={'center'}
          />
        ))}
      </Node>

      <Node ref={scoreGroup} x={S_X} y={S_Y} opacity={0}>
        <Txt
          text={'S = Q K^T'}
          y={-292}
          fill={theme.accent}
          fontFamily={theme.monoFamily}
          fontSize={34}
          textAlign={'center'}
        />
        <Txt
          ref={sSubRaw}
          text={'原始 score'}
          y={-250}
          fill={theme.muted}
          fontFamily={theme.fontFamily}
          fontSize={24}
          textAlign={'center'}
        />
        <Txt
          ref={sSubScaled}
          text={'缩放后'}
          y={-250}
          fill={theme.highlight}
          fontFamily={theme.fontFamily}
          fontSize={24}
          textAlign={'center'}
          opacity={0}
        />

        {['k1', 'k2', 'k3', 'k4'].map((label, column) => (
          <Txt
            text={label}
            x={cellX(column)}
            y={-214}
            fill={theme.muted}
            fontFamily={theme.monoFamily}
            fontSize={24}
            textAlign={'center'}
          />
        ))}
        {['q1', 'q2', 'q3', 'q4'].map((label, row) => (
          <Txt
            text={label}
            x={-MATRIX_W / 2 - 44}
            y={cellY(row)}
            fill={row === 0 ? theme.accent : theme.muted}
            fontFamily={theme.monoFamily}
            fontSize={26}
            textAlign={'center'}
          />
        ))}

        <Rect
          ref={scoreRowHighlight}
          y={cellY(0)}
          width={MATRIX_W + 12}
          height={CELL_H + 6}
          radius={12}
          fill={theme.accentSoft}
          stroke={theme.accent}
          lineWidth={2}
          opacity={0}
        />

        <Txt
          ref={q1Caption}
          text={'q1 这一行：对 4 个 key 的 score'}
          y={220}
          fill={theme.muted}
          fontFamily={theme.fontFamily}
          fontSize={26}
          textAlign={'center'}
          opacity={0}
        />
        <Txt
          ref={q1ScaledCaption}
          text={'q1 缩放后：[3, 0, 0, 0]'}
          y={220}
          fill={theme.highlight}
          fontFamily={theme.fontFamily}
          fontSize={26}
          textAlign={'center'}
          opacity={0}
        />
        <Txt
          ref={scaleFormula}
          text={'S / √d_k  =  S / 2'}
          y={262}
          fill={theme.accent}
          fontFamily={theme.monoFamily}
          fontSize={30}
          textAlign={'center'}
          opacity={0}
        />
        <Txt
          ref={scaleDetail}
          text={'d_k = 4   →   √d_k = 2'}
          y={300}
          fill={theme.muted}
          fontFamily={theme.monoFamily}
          fontSize={24}
          textAlign={'center'}
          opacity={0}
        />
        <Txt
          ref={scaleRule}
          text={'缩放只改变幅度，不改变谁大谁小'}
          y={338}
          fill={theme.muted}
          fontFamily={theme.fontFamily}
          fontSize={26}
          textAlign={'center'}
          opacity={0}
        />
      </Node>

      <Node ref={weightGroup} x={A_X} y={A_Y} opacity={0}>
        <Txt
          text={'A = row_softmax(S / √d_k)'}
          y={-292}
          fill={theme.accent}
          fontFamily={theme.monoFamily}
          fontSize={28}
          textAlign={'center'}
        />
        <Txt
          text={'每行权重和为 1'}
          y={-250}
          fill={theme.muted}
          fontFamily={theme.fontFamily}
          fontSize={24}
          textAlign={'center'}
        />

        {['k1', 'k2', 'k3', 'k4'].map((label, column) => (
          <Txt
            text={label}
            x={cellX(column)}
            y={-214}
            fill={theme.muted}
            fontFamily={theme.monoFamily}
            fontSize={24}
            textAlign={'center'}
          />
        ))}
        {['t1', 't2', 't3', 't4'].map((label, row) => (
          <Txt
            text={label}
            x={-MATRIX_W / 2 - 44}
            y={cellY(row)}
            fill={weightColor(row)}
            fontFamily={theme.monoFamily}
            fontSize={26}
            textAlign={'center'}
          />
        ))}

        <Rect
          ref={weightRow1Highlight}
          y={cellY(0)}
          width={MATRIX_W + 12}
          height={CELL_H + 6}
          radius={12}
          fill={theme.accentSoft}
          stroke={theme.accent}
          lineWidth={2}
          opacity={0}
        />
        <Rect
          ref={weightRow3Highlight}
          y={cellY(2)}
          width={MATRIX_W + 12}
          height={CELL_H + 6}
          radius={12}
          fill={WARM_HIGHLIGHT}
          stroke={theme.highlight}
          lineWidth={2}
          opacity={0}
        />

        {WEIGHTS.flatMap((_, rowIndex) =>
          [0, 1, 2, 3].map(columnIndex => {
            const index = rowIndex * 4 + columnIndex;
            return (
              <Rect
                ref={weightRects[index]}
                x={cellX(columnIndex)}
                y={cellY(rowIndex)}
                width={CELL_W}
                height={CELL_H}
                radius={10}
                fill={WEIGHT_FILL}
                stroke={WEIGHT_STROKE}
                lineWidth={1.5}
                opacity={0}
              />
            );
          }),
        )}
        {WEIGHTS.flatMap((row, rowIndex) =>
          row.map((value, columnIndex) => {
            const index = rowIndex * 4 + columnIndex;
            return (
              <Txt
                ref={weightTexts[index]}
                text={value.toFixed(3)}
                x={cellX(columnIndex)}
                y={cellY(rowIndex)}
                fill={weightColor(rowIndex)}
                fontFamily={theme.monoFamily}
                fontSize={28}
                textAlign={'center'}
                opacity={0}
              />
            );
          }),
        )}
      </Node>

      <Node ref={arrowGroup} opacity={0}>
        <Line
          ref={arrowLine}
          points={[
            [-178, -40],
            [96, -40],
          ]}
          stroke={theme.accent}
          lineWidth={4}
          endArrow
          arrowSize={18}
          end={0}
        />
        <Txt
          ref={arrowLabel}
          text={'逐行 softmax'}
          x={-40}
          y={-82}
          fill={theme.accent}
          fontFamily={theme.fontFamily}
          fontSize={24}
          textAlign={'center'}
        />
      </Node>

      <Txt
        ref={aRow1Label}
        text={'t1：集中在 k1 ≈ 0.870'}
        x={A_X}
        y={200}
        fill={theme.accent}
        fontFamily={theme.fontFamily}
        fontSize={26}
        textAlign={'center'}
        opacity={0}
      />
      <Txt
        ref={aRow3Label}
        text={'t3：四个 key 均匀 ≈ 0.250'}
        x={A_X}
        y={244}
        fill={theme.highlight}
        fontFamily={theme.fontFamily}
        fontSize={26}
        textAlign={'center'}
        opacity={0}
      />
      <Txt
        ref={bottomCaption}
        text={''}
        y={370}
        fill={theme.muted}
        fontFamily={theme.fontFamily}
        fontSize={28}
        textAlign={'center'}
        opacity={0}
      />
    </>,
  );

  // Add the score cells after the highlight so row 1 sits underneath its values.
  scoreGroup().add(
    <>
      {SCORES.flatMap((_, rowIndex) =>
        [0, 1, 2, 3].map(columnIndex => {
          const index = rowIndex * 4 + columnIndex;
          return (
            <Rect
              ref={scoreRects[index]}
              x={cellX(columnIndex)}
              y={cellY(rowIndex)}
              width={CELL_W}
              height={CELL_H}
              radius={10}
              fill={CELL_FILL}
              stroke={CELL_STROKE}
              lineWidth={1.5}
            />
          );
        }),
      )}
      {SCORES.flatMap((row, rowIndex) =>
        row.map((value, columnIndex) => {
          const index = rowIndex * 4 + columnIndex;
          return (
            <Txt
              ref={scoreOrigTexts[index]}
              text={String(value)}
              x={cellX(columnIndex)}
              y={cellY(rowIndex)}
              fill={theme.ink}
              fontFamily={theme.monoFamily}
              fontSize={32}
              textAlign={'center'}
            />
          );
        }),
      )}
      {SCALED.flatMap((row, rowIndex) =>
        row.map((value, columnIndex) => {
          const index = rowIndex * 4 + columnIndex;
          return (
            <Txt
              ref={scoreScaledTexts[index]}
              text={String(value)}
              x={cellX(columnIndex)}
              y={cellY(rowIndex)}
              fill={theme.highlight}
              fontFamily={theme.monoFamily}
              fontSize={32}
              textAlign={'center'}
              opacity={0}
            />
          );
        }),
      )}
    </>,
  );

  // 00:00 — establish the four tokens and the score matrix.
  yield* beat(1.2, title().opacity(1, 1.2));
  yield* beat(
    1.4,
    all(tokenGroup().opacity(1, 1.0, easeOutCubic), tokenGroup().y(-400, 1.2, easeOutCubic)),
  );
  yield* beat(1.8, scoreGroup().opacity(1, 1.6, easeInOutCubic));
  yield* beat(1.2, scoreRowHighlight().opacity(1, 0.8));
  yield* beat(1.4, q1Caption().opacity(1, 1.2));
  yield* beat(1.0, sSubRaw().opacity(1, 0.8));

  // 00:08 — hold the raw q1 score gap for four seconds.
  yield* holdTo(12);
  yield* beat(1.5, scaleFormula().opacity(1, 1.2));
  yield* beat(1.5, scaleDetail().opacity(1, 1.2));
  yield* holdTo(20);

  // 00:20 — divide every score by sqrt(d_k); q1 becomes [3, 0, 0, 0].
  yield* beat(
    1.2,
    all(
      scaleFormula().fill(theme.highlight, 0.6),
      scoreRowHighlight().lineWidth(5, 0.6),
    ),
  );
  yield* beat(
    2.2,
    all(
      ...scoreOrigTexts.map(ref => ref().opacity(0, 1.6)),
      ...scoreScaledTexts.map(ref => ref().opacity(1, 1.6)),
      sSubRaw().opacity(0, 1.0),
      sSubScaled().opacity(1, 1.0),
    ),
  );
  yield* beat(
    1.0,
    all(q1ScaledCaption().opacity(1, 0.8), q1Caption().opacity(0, 0.8)),
  );
  yield* beat(2.2, scaleRule().opacity(1, 1.6));
  yield* beat(1.2, scoreRowHighlight().lineWidth(2, 0.8));
  yield* holdTo(34);

  // 00:34 — cut to row-wise softmax: reveal A one row at a time.
  yield* beat(0.5, weightGroup().opacity(1, 0.4));
  yield* beat(
    0.8,
    all(arrowGroup().opacity(1, 0.6), arrowLine().end(1, 0.8, easeOutCubic)),
  );
  yield* beat(
    1.0,
    all(
      weightRow1Highlight().opacity(1, 0.5),
      ...rowIndices(0).flatMap(index => [
        weightRects[index]().opacity(1, 0.7),
        weightTexts[index]().opacity(1, 0.7),
      ]),
    ),
  );
  yield* holdTo(37);
  yield* beat(
    1.0,
    all(
      ...rowIndices(1).flatMap(index => [
        weightRects[index]().opacity(1, 0.7),
        weightTexts[index]().opacity(1, 0.7),
      ]),
    ),
  );
  yield* holdTo(40);
  yield* beat(
    1.0,
    all(
      ...rowIndices(2).flatMap(index => [
        weightRects[index]().opacity(1, 0.7),
        weightTexts[index]().opacity(1, 0.7),
      ]),
    ),
  );
  yield* holdTo(43);
  yield* beat(
    1.0,
    all(
      ...rowIndices(3).flatMap(index => [
        weightRects[index]().opacity(1, 0.7),
        weightTexts[index]().opacity(1, 0.7),
      ]),
    ),
  );
  yield* holdTo(46);
  bottomCaption().text('逐行 softmax 完成：每行权重和为 1');
  yield* beat(2.0, bottomCaption().opacity(1, 1.6));

  // 00:48 — emphasis: t1 is concentrated, t3 is uniform.
  yield* beat(
    1.2,
    all(weightRow1Highlight().opacity(1, 0.6), weightRow3Highlight().opacity(1, 0.6)),
  );
  yield* beat(
    1.6,
    all(aRow1Label().opacity(1, 1.0), aRow3Label().opacity(1, 1.0)),
  );
  yield* beat(
    1.6,
    all(
      ...rowIndices(1).flatMap(index => [
        weightRects[index]().opacity(0.3, 1.2),
        weightTexts[index]().opacity(0.3, 1.2),
      ]),
      ...rowIndices(3).flatMap(index => [
        weightRects[index]().opacity(0.3, 1.2),
        weightTexts[index]().opacity(0.3, 1.2),
      ]),
    ),
  );
  yield* holdTo(56);

  // 01:02 — converge to A and hold; O = A V is deliberately left out.
  yield* beat(
    1.4,
    all(
      ...rowIndices(1).flatMap(index => [
        weightRects[index]().opacity(1, 1.0),
        weightTexts[index]().opacity(1, 1.0),
      ]),
      ...rowIndices(3).flatMap(index => [
        weightRects[index]().opacity(1, 1.0),
        weightTexts[index]().opacity(1, 1.0),
      ]),
    ),
  );
  yield* beat(0.4, bottomCaption().opacity(0, 0.4));
  bottomCaption().text('A 的每一行：一个 query 对 4 个 key 的权重分配');
  yield* beat(2.2, bottomCaption().opacity(1, 1.6));

  yield* holdTo(62);
  yield* beat(
    1.0,
    all(
      scoreGroup().opacity(0, 0.8),
      arrowGroup().opacity(0, 0.8),
      tokenGroup().opacity(0, 0.8),
      aRow1Label().opacity(0, 0.8),
      aRow3Label().opacity(0, 0.8),
    ),
  );
  yield* beat(
    1.0,
    all(
      weightGroup().x(0, 1.0, easeInOutCubic),
      weightGroup().scale(1.08, 1.0, easeInOutCubic),
    ),
  );
  yield* beat(0.4, bottomCaption().opacity(0, 0.4));
  bottomCaption().text('A：每一行和为 1；本段停在 A');
  yield* beat(0.6, bottomCaption().opacity(1, 0.6));
  yield* holdTo(68);

  if (Math.abs(now - 68) > 0.001) {
    throw new Error(`scene duration mismatch: ${now}s`);
  }
});
