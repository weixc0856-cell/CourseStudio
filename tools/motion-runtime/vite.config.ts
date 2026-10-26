import {defineConfig} from 'vite';
import motionCanvas from '@motion-canvas/vite-plugin';

const segment = process.env.MC_SEGMENT;
const validSegment = segment && /^[A-Za-z0-9_-]+$/.test(segment) ? segment : undefined;
const port = Number.parseInt(process.env.MC_PORT ?? '9100', 10);

export default defineConfig({
  plugins: [
    motionCanvas({
      // A single segment project is selected by the runner. With no selection,
      // the editor can open any project in src/projects/.
      project: validSegment
        ? `./src/projects/${validSegment}.ts`
        : './src/projects/*.ts',
    }),
  ],
  server: {
    port: Number.isFinite(port) ? port : 9100,
    strictPort: true,
  },
});
