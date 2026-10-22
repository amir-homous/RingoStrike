// B31: the focus view's media (background image, music) and its pause math.
// Pure helpers: the component passes in the file lists (Vite glob and music manifest).

// Path key -> media folder name (images in src/assets/focus-backgrounds, music in public/Musics).
export const PATH_FOLDERS = {
  career: "Work",
  creativity: "Creative",
  fitness: "Fitness",
  learning: "Learning",
  sleep: "Sleep",
};

export const AUDIO_EXTENSIONS = ["mp3", "ogg", "m4a", "wav"];
export const IMAGE_EXTENSIONS = ["webp", "png", "jpg", "jpeg"];

export function pathFolder(pathKey) {
  return PATH_FOLDERS[String(pathKey || "").trim().toLowerCase()] || "";
}

function extension(name) {
  const match = /\.([a-z0-9]+)$/i.exec(String(name || ""));
  return match ? match[1].toLowerCase() : "";
}

export function isAudioFile(name) {
  const base = String(name || "").split("/").pop();
  return !base.startsWith(".") && AUDIO_EXTENSIONS.includes(extension(base));
}

// Music: `{Folder}/{challengeKey}/*` -> `{Folder}/*` -> the root `Default*` files.
// `files` are paths relative to public/Musics ("Work/a.mp3", "Default_x.mp3"); non-audio entries are ignored.
export function resolveMusic(files, { pathKey = "", challengeKey = "" } = {}) {
  const audio = (Array.isArray(files) ? files : []).filter(isAudioFile).sort();
  const folder = pathFolder(pathKey);
  const inDir = (dir) => audio.filter((file) => {
    const parts = file.split("/");
    return parts.slice(0, -1).join("/").toLowerCase() === dir.toLowerCase();
  });
  const levels = [];
  if (folder && challengeKey) levels.push(inDir(`${folder}/${challengeKey}`));
  if (folder) levels.push(inDir(folder));
  levels.push(inDir("").filter((file) => /^default/i.test(file)));
  return levels.find((list) => list.length) || [];
}

// Image: `{Folder}/{challengeKey}` -> `{Folder}/default` -> root `default` -> null (plain card).
// `images` maps a path relative to focus-backgrounds ("Work/default.webp") to its URL.
export function resolveBackground(images, { pathKey = "", challengeKey = "" } = {}) {
  const map = images && typeof images === "object" ? images : {};
  const byStem = {};
  for (const [file, url] of Object.entries(map)) {
    if (!IMAGE_EXTENSIONS.includes(extension(file)) || !url) continue;
    const stem = file.replace(/\.[^./]+$/, "").toLowerCase();
    // The first extension in IMAGE_EXTENSIONS order wins for the same name.
    const rank = IMAGE_EXTENSIONS.indexOf(extension(file));
    if (!byStem[stem] || rank < byStem[stem].rank) byStem[stem] = { url, rank };
  }
  const folder = pathFolder(pathKey).toLowerCase();
  const stems = [];
  if (folder && challengeKey) stems.push(`${folder}/${String(challengeKey).toLowerCase()}`);
  if (folder) stems.push(`${folder}/default`);
  stems.push("default");
  for (const stem of stems) if (byStem[stem]) return byStem[stem].url;
  return null;
}

// "./foo/../assets/focus-backgrounds/Work/a.webp" -> "Work/a.webp" (keys from import.meta.glob).
export function globToRelative(globbed, marker = "focus-backgrounds/") {
  const out = {};
  for (const [key, url] of Object.entries(globbed || {})) {
    const index = key.indexOf(marker);
    if (index >= 0) out[key.slice(index + marker.length)] = url;
  }
  return out;
}

// Pause math. The timer stays timestamp-based: elapsed = (now or pausedAt) - startedAt - pausedMs.
export function focusElapsedMs(state, now = Date.now()) {
  const { startedAt, pausedAt = null, pausedMs = 0 } = state || {};
  if (!startedAt) return 0;
  const end = pausedAt || now;
  return Math.max(0, end - startedAt - Math.max(0, pausedMs || 0));
}

export function pauseFocus(state, now = Date.now()) {
  if (!state?.startedAt || state.pausedAt) return state;
  return { ...state, pausedAt: now };
}

export function resumeFocus(state, now = Date.now()) {
  if (!state?.startedAt || !state.pausedAt) return state;
  return { startedAt: state.startedAt, pausedAt: null, pausedMs: (state.pausedMs || 0) + Math.max(0, now - state.pausedAt) };
}

// The stored focus record: a bare number (B27) or JSON with the pause fields.
export function parseFocusState(raw) {
  if (raw == null || raw === "") return null;
  const number = Number(raw);
  if (Number.isFinite(number) && number > 0) return { startedAt: number, pausedAt: null, pausedMs: 0 };
  try {
    const value = JSON.parse(raw);
    const startedAt = Number(value?.startedAt);
    if (!Number.isFinite(startedAt) || startedAt <= 0) return null;
    const pausedAt = Number(value.pausedAt);
    const pausedMs = Number(value.pausedMs);
    return {
      startedAt,
      pausedAt: Number.isFinite(pausedAt) && pausedAt >= startedAt ? pausedAt : null,
      pausedMs: Number.isFinite(pausedMs) && pausedMs > 0 ? pausedMs : 0,
    };
  } catch {
    return null;
  }
}

export function serializeFocusState(state) {
  if (!state?.startedAt) return null;
  if (!state.pausedAt && !state.pausedMs) return String(state.startedAt);
  return JSON.stringify({ startedAt: state.startedAt, pausedAt: state.pausedAt || null, pausedMs: state.pausedMs || 0 });
}

// Mute is a device preference (localStorage), guarded like every other storage access.
export const MUTE_KEY = "ringostrike_focus_music_muted";

function local(storage) {
  if (storage) return storage;
  try {
    return typeof window !== "undefined" ? window.localStorage : null;
  } catch {
    return null;
  }
}

export function readMusicMuted(storage) {
  try {
    return local(storage)?.getItem(MUTE_KEY) === "1";
  } catch {
    return false;
  }
}

export function writeMusicMuted(muted, storage) {
  try {
    const target = local(storage);
    if (!target) return;
    if (muted) target.setItem(MUTE_KEY, "1");
    else target.removeItem(MUTE_KEY);
  } catch {
    // ignore
  }
}
