import {easeInOutCubic, easeOutCubic} from '@motion-canvas/core';

/**
 * Shared visual language for course explainers.
 *
 * McKinsey-inspired orange/white: warm white background, near-black ink,
 * orange for structure and key values, deep amber for secondary emphasis.
 * Keep every scene on these tokens. In particular, always pass
 * `fontFamily={theme.fontFamily}` to `Txt`; the embeddable player does not
 * inherit the editor's font stack and falls back to a serif face otherwise.
 */
export const theme = {
  background: '#FAFAF7',
  ink: '#1A1A1A',
  muted: '#5A5A5A',
  grid: 'rgba(26, 26, 26, 0.10)',
  accent: '#E87722',
  highlight: '#B45309',
  accentSoft: 'rgba(232, 119, 34, 0.12)',
  fontFamily: '"Segoe UI", "Microsoft YaHei", "PingFang SC", system-ui, sans-serif',
  monoFamily: '"Cascadia Mono", "JetBrains Mono", Consolas, monospace',
  fontSize: {
    title: 64,
    body: 42,
    label: 34,
    caption: 28,
  },
} as const;

export const ease = {
  out: easeOutCubic,
  inOut: easeInOutCubic,
} as const;
