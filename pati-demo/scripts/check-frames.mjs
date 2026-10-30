// Renderiza frames de verificação em out/frames/.
// Uso: node scripts/check-frames.mjs [segundos...]   (padrão: 2 7 13 21 30 37)
import path from "node:path";
import fs from "node:fs";
import { bundle } from "@remotion/bundler";
import { renderStill, selectComposition } from "@remotion/renderer";

const seconds = process.argv.slice(2).map(Number);
const times = seconds.length ? seconds : [2, 7, 13, 21, 30, 37];
const browserExecutable = process.env.REMOTION_BROWSER || undefined;

const root = path.resolve(path.dirname(new URL(import.meta.url).pathname), "..");
const outDir = path.join(root, "out", "frames");
fs.mkdirSync(outDir, { recursive: true });

const serveUrl = await bundle({ entryPoint: path.join(root, "src", "index.ts") });
const composition = await selectComposition({ serveUrl, id: "PatiDemo", browserExecutable });
for (const t of times) {
  const frame = Math.min(composition.durationInFrames - 1, Math.round(t * composition.fps));
  const output = path.join(outDir, `frame-${String(t).replace(".", "_")}s.png`);
  await renderStill({ serveUrl, composition, frame, output, browserExecutable });
  console.log("ok", output);
}
