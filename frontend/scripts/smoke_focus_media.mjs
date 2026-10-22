// B31 (#401): focus media and pause, dependency-free.
// Music and image fallback chains, the music manifest, pause duration math and the mute preference.
import assert from "node:assert/strict";
import { mkdirSync, mkdtempSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";

import {
  MUTE_KEY,
  PATH_FOLDERS,
  focusElapsedMs,
  globToRelative,
  isAudioFile,
  parseFocusState,
  pathFolder,
  pauseFocus,
  readMusicMuted,
  resolveBackground,
  resolveMusic,
  resumeFocus,
  serializeFocusState,
  writeMusicMuted,
} from "../src/lib/focusMedia.js";
import { listAudio } from "../vite/focusMusicManifest.js";

function runFolders() {
  assert.deepEqual(PATH_FOLDERS, { career: "Work", creativity: "Creative", fitness: "Fitness", learning: "Learning", sleep: "Sleep" });
  assert.equal(pathFolder("career"), "Work");
  assert.equal(pathFolder(" Sleep "), "Sleep");
  assert.equal(pathFolder("unknown"), "");
  assert.equal(pathFolder(""), "");
}

function runMusic() {
  const files = [
    "Default_atlasaudio-chill.mp3",
    "README.txt",
    "Work/.gitkeep",
    "Work/focus-a.mp3",
    "Work/focus-b.OGG",
    "Work/notes.txt",
    "Work/deep-work/one.m4a",
    "Sleep/.gitkeep",
    "Fitness/run.wav",
    "other.mp3",
  ];
  assert.ok(isAudioFile("a.MP3") && isAudioFile("x/y.wav") && isAudioFile("b.m4a") && isAudioFile("c.ogg"));
  assert.ok(!isAudioFile(".gitkeep") && !isAudioFile("README") && !isAudioFile("x.txt") && !isAudioFile("Work/.hidden.mp3"));

  // 1. The challenge folder wins.
  assert.deepEqual(resolveMusic(files, { pathKey: "career", challengeKey: "deep-work" }), ["Work/deep-work/one.m4a"]);
  // 2. Then the path folder (audio only, never .txt or .gitkeep).
  assert.deepEqual(resolveMusic(files, { pathKey: "career", challengeKey: "no-such" }), ["Work/focus-a.mp3", "Work/focus-b.OGG"]);
  assert.deepEqual(resolveMusic(files, { pathKey: "fitness" }), ["Fitness/run.wav"]);
  // 3. Then the root Default* files (an empty folder with only .gitkeep falls through).
  assert.deepEqual(resolveMusic(files, { pathKey: "sleep" }), ["Default_atlasaudio-chill.mp3"]);
  assert.deepEqual(resolveMusic(files, { pathKey: "" }), ["Default_atlasaudio-chill.mp3"]);
  assert.deepEqual(resolveMusic(files, { pathKey: "learning", challengeKey: "x" }), ["Default_atlasaudio-chill.mp3"]);
  // 4. No track at all: an empty list (the mute button is hidden).
  assert.deepEqual(resolveMusic(["README.txt", "Work/.gitkeep", "other.mp3"], { pathKey: "career" }), []);
  assert.deepEqual(resolveMusic(null, { pathKey: "career" }), []);
  // Folder names are matched without case.
  assert.deepEqual(resolveMusic(["work/a.mp3"], { pathKey: "career" }), ["work/a.mp3"]);
}

function runManifest() {
  const root = mkdtempSync(join(tmpdir(), "focus-music-"));
  for (const dir of ["Work", "Sleep", "Work/deep-work"]) mkdirSync(join(root, dir), { recursive: true });
  const files = {
    "Default_x.mp3": "a",
    "README.txt": "a",
    "license.txt": "a",
    "Work/.gitkeep": "",
    "Work/a.mp3": "a",
    "Work/B.WAV": "a",
    "Work/deep-work/c.ogg": "a",
    "Work/empty.mp3": "",
    "Sleep/.gitkeep": "",
    "Sleep/d.m4a": "a",
    "Sleep/cover.png": "a",
  };
  for (const [name, body] of Object.entries(files)) writeFileSync(join(root, name), body);
  // Only non-empty audio files, with forward slashes, sorted. Adding a file needs no code change.
  assert.deepEqual(listAudio(root), ["Default_x.mp3", "Sleep/d.m4a", "Work/B.WAV", "Work/a.mp3", "Work/deep-work/c.ogg"]);
  writeFileSync(join(root, "Sleep/e.mp3"), "a");
  assert.ok(listAudio(root).includes("Sleep/e.mp3"));
  assert.deepEqual(listAudio(join(root, "missing")), []);
}

function runBackground() {
  const globbed = {
    "../../assets/focus-backgrounds/default.webp": "/a/default.webp",
    "../../assets/focus-backgrounds/Work/default.png": "/a/work-default.png",
    "../../assets/focus-backgrounds/Work/deep-work.webp": "/a/deep-work.webp",
    "../../assets/focus-backgrounds/Work/deep-work.jpg": "/a/deep-work.jpg",
    "../../assets/focus-backgrounds/Sleep/notes.txt": "/a/notes.txt",
  };
  const images = globToRelative(globbed);
  assert.deepEqual(Object.keys(images).sort(), ["Sleep/notes.txt", "Work/deep-work.jpg", "Work/deep-work.webp", "Work/default.png", "default.webp"]);
  // 1. {Folder}/{challengeKey} (webp before jpg for the same name).
  assert.equal(resolveBackground(images, { pathKey: "career", challengeKey: "deep-work" }), "/a/deep-work.webp");
  // 2. {Folder}/default.
  assert.equal(resolveBackground(images, { pathKey: "career", challengeKey: "other" }), "/a/work-default.png");
  // 3. The root default.
  assert.equal(resolveBackground(images, { pathKey: "sleep", challengeKey: "x" }), "/a/default.webp");
  assert.equal(resolveBackground(images, {}), "/a/default.webp");
  // 4. Nothing: null (the plain card).
  assert.equal(resolveBackground({ "Sleep/notes.txt": "/a/n.txt" }, { pathKey: "sleep" }), null);
  assert.equal(resolveBackground(null, { pathKey: "sleep" }), null);
}

function runPause() {
  const t0 = 1_000_000;
  let state = { startedAt: t0, pausedAt: null, pausedMs: 0 };
  assert.equal(focusElapsedMs(state, t0 + 65_000), 65_000);
  // Pause at 1:05; the clock stays frozen while paused.
  state = pauseFocus(state, t0 + 65_000);
  assert.equal(state.pausedAt, t0 + 65_000);
  assert.equal(focusElapsedMs(state, t0 + 400_000), 65_000);
  // Pausing twice changes nothing.
  assert.equal(pauseFocus(state, t0 + 500_000), state);
  // Resume after 10 minutes: those 10 minutes never count.
  state = resumeFocus(state, t0 + 665_000);
  assert.deepEqual(state, { startedAt: t0, pausedAt: null, pausedMs: 600_000 });
  assert.equal(focusElapsedMs(state, t0 + 685_000), 85_000);
  // Resume while running changes nothing.
  assert.equal(resumeFocus(state, t0 + 700_000), state);
  // A second pause adds up; Done while paused uses the frozen time.
  state = resumeFocus(pauseFocus(state, t0 + 700_000), t0 + 760_000);
  assert.equal(state.pausedMs, 660_000);
  const pausedAgain = pauseFocus(state, t0 + 800_000);
  assert.equal(Math.floor(focusElapsedMs(pausedAgain, t0 + 9_999_999) / 1000), 140);
  // Clock skew (now before start) never goes negative; no start is 0.
  assert.equal(focusElapsedMs({ startedAt: t0 }, t0 - 5000), 0);
  assert.equal(focusElapsedMs(null), 0);

  // Storage: a B27 bare number still reads; the pause round-trips; garbage is ignored.
  assert.deepEqual(parseFocusState(String(t0)), { startedAt: t0, pausedAt: null, pausedMs: 0 });
  assert.equal(serializeFocusState({ startedAt: t0, pausedAt: null, pausedMs: 0 }), String(t0));
  assert.deepEqual(parseFocusState(serializeFocusState(pausedAgain)), pausedAgain);
  assert.equal(parseFocusState(null), null);
  assert.equal(parseFocusState("not json"), null);
  assert.equal(parseFocusState('{"startedAt":-1}'), null);
  assert.deepEqual(parseFocusState(JSON.stringify({ startedAt: t0, pausedAt: t0 - 1, pausedMs: -5 })), { startedAt: t0, pausedAt: null, pausedMs: 0 });
  assert.equal(serializeFocusState(null), null);
}

function runMute() {
  const data = new Map();
  const storage = {
    getItem: (key) => (data.has(key) ? data.get(key) : null),
    setItem: (key, value) => data.set(key, String(value)),
    removeItem: (key) => data.delete(key),
  };
  assert.equal(readMusicMuted(storage), false, "music is on by default");
  writeMusicMuted(true, storage);
  assert.equal(data.get(MUTE_KEY), "1");
  assert.equal(readMusicMuted(storage), true, "mute is remembered");
  writeMusicMuted(false, storage);
  assert.equal(data.has(MUTE_KEY), false);
  assert.equal(readMusicMuted(storage), false);
  // Blocked storage never throws.
  const blocked = { getItem: () => { throw new Error("blocked"); }, setItem: () => { throw new Error("blocked"); }, removeItem: () => { throw new Error("blocked"); } };
  assert.equal(readMusicMuted(blocked), false);
  writeMusicMuted(true, blocked);
  // No window (Node): reads false, writes are ignored.
  assert.equal(readMusicMuted(), false);
  writeMusicMuted(true);
}

runFolders();
runMusic();
runManifest();
runBackground();
runPause();
runMute();
console.log("focus media smoke passed");
