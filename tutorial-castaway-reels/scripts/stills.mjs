// Renderiza quadros avulsos para conferência.
// Uso: node scripts/stills.mjs <CompositionId> <frame> [frame...]  -> out/stills/<id>_<frame>.png
import { bundle } from "@remotion/bundler";
import { renderStill, selectComposition } from "@remotion/renderer";
import fs from "node:fs";
import path from "node:path";

const [id, ...frames] = process.argv.slice(2);
const browserExecutable = process.env.REMOTION_BROWSER || undefined;
const serveUrl = await bundle({ entryPoint: path.resolve("src/index.ts") });
const composition = await selectComposition({ serveUrl, id, browserExecutable });
fs.mkdirSync("out/stills", { recursive: true });
for (const f of frames) {
  const output = `out/stills/${id}_${String(f).padStart(4, "0")}.png`;
  await renderStill({ serveUrl, composition, frame: Number(f), output, browserExecutable, scale: 0.5 });
  console.log(output);
}
