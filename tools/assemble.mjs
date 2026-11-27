// Builds public/index.html from src/index.template.html + src/game/game-NN.js.
// The game script is served as ONE inline <script>: the game's own anti-cheat hashes that inline script
// and counts inline scripts, so it must not be split into separate <script src> files.
import { readFileSync, writeFileSync, readdirSync, mkdirSync } from "node:fs";
import { createHash } from "node:crypto";
const root = new URL("..", import.meta.url);
const read = (p) => readFileSync(new URL(p, root));
const manifest = JSON.parse(read("src/game/manifest.json"));
const MARK = Buffer.from("/*@@ASHGROVE_GAME_SCRIPT@@*/");
const tpl = read("src/index.template.html");
const at = tpl.indexOf(MARK);
if (at < 0 || tpl.indexOf(MARK, at + 1) >= 0) throw new Error("template must contain the game-script marker exactly once");
const game = Buffer.concat(manifest.parts.map((p) => read(p)));
const html = Buffer.concat([tpl.subarray(0, at), game, tpl.subarray(at + MARK.length)]);
writeFileSync(new URL("public/index.html", root), html);
const sha = (b) => createHash("sha256").update(b).digest("hex");
const same = sha(html) === manifest.index_html_sha256;
console.log(`public/index.html: ${html.length} bytes, game script ${game.length} bytes, ${same ? "matches" : "DIFFERS FROM"} the recorded release build`);

// Binary assets (loading-screen art) are stored as base64 text in src/binary/*.json
// ({ "public/relative/path": "<base64>" }) and decoded into public/ here.
const binDir = new URL("src/binary/", root);
let n = 0;
for (const f of readdirSync(binDir).filter((x) => x.endsWith(".json"))) {
  const entries = JSON.parse(readFileSync(new URL(f, binDir), "utf8"));
  for (const [rel, b64] of Object.entries(entries)) {
    const out = new URL("public/" + rel, root);
    mkdirSync(new URL(".", out), { recursive: true });
    writeFileSync(out, Buffer.from(b64, "base64"));
    n++;
  }
}
console.log(`decoded ${n} binary assets into public/`);
