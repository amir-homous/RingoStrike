import { defineConfig, loadEnv } from "vite";
import vue from "@vitejs/plugin-vue";
import { fileURLToPath, URL } from "node:url";
import focusMusicManifest from "./vite/focusMusicManifest.js";

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), "");

  return {
    base: env.VITE_BASE || "/",
    plugins: [vue(), focusMusicManifest({ dir: fileURLToPath(new URL("./public/Musics", import.meta.url)) })],
    resolve: {
      alias: {
        "@": fileURLToPath(new URL("./src", import.meta.url)),
      },
    },
  };
});
