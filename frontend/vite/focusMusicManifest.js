// B31: `virtual:focus-music` lists the audio files under public/Musics at dev start and at build.
// Adding a track needs no code change: drop the file in its folder (dev reloads, a build picks it up).
// Only audio extensions are listed; .txt, README, .gitkeep and other files are ignored.
import { readdirSync, statSync } from "node:fs";
import { join, relative, sep } from "node:path";

const VIRTUAL_ID = "virtual:focus-music";
const RESOLVED_ID = `\0${VIRTUAL_ID}`;
const AUDIO = /\.(mp3|ogg|m4a|wav)$/i;

export function listAudio(root) {
  const out = [];
  const walk = (dir) => {
    let entries = [];
    try {
      entries = readdirSync(dir);
    } catch {
      return;
    }
    for (const name of entries) {
      if (name.startsWith(".")) continue;
      const full = join(dir, name);
      let stat;
      try {
        stat = statSync(full);
      } catch {
        continue;
      }
      if (stat.isDirectory()) walk(full);
      else if (stat.isFile() && stat.size > 0 && AUDIO.test(name)) out.push(relative(root, full).split(sep).join("/"));
    }
  };
  walk(root);
  return out.sort();
}

export default function focusMusicManifest({ dir }) {
  let server = null;
  return {
    name: "ringo-focus-music-manifest",
    resolveId(id) {
      return id === VIRTUAL_ID ? RESOLVED_ID : null;
    },
    load(id) {
      if (id !== RESOLVED_ID) return null;
      return `export default ${JSON.stringify(listAudio(dir))};\n`;
    },
    configureServer(devServer) {
      server = devServer;
      server.watcher.add(dir);
      const refresh = (file) => {
        if (!file.startsWith(dir)) return;
        const mod = server.moduleGraph.getModuleById(RESOLVED_ID);
        if (mod) server.moduleGraph.invalidateModule(mod);
        server.ws.send({ type: "full-reload" });
      };
      server.watcher.on("add", refresh);
      server.watcher.on("unlink", refresh);
    },
  };
}
