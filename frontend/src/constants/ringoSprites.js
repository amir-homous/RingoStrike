export const RINGO_SPRITE_KEYS = Object.freeze([
  "idle",
  "welcome",
  "talking",
  "explaining",
  "thinking",
  "encouraging",
  "warning",
  "concerned",
  "happy",
  "celebration",
  "achievement",
  "proud",
  "sad",
  "sleeping",
  "focus",
  "victory",
]);

export const RINGO_SPRITES = Object.freeze({
  idle: new URL("@/assets/ringo/idle.png", import.meta.url).href,
  welcome: new URL("@/assets/ringo/welcome.png", import.meta.url).href,
  talking: new URL("@/assets/ringo/talking.png", import.meta.url).href,
  explaining: new URL("@/assets/ringo/explaining.png", import.meta.url).href,
  thinking: new URL("@/assets/ringo/thinking.png", import.meta.url).href,
  encouraging: new URL("@/assets/ringo/encouraging.png", import.meta.url).href,
  warning: new URL("@/assets/ringo/warning.png", import.meta.url).href,
  concerned: new URL("@/assets/ringo/concerned.png", import.meta.url).href,
  happy: new URL("@/assets/ringo/happy.png", import.meta.url).href,
  celebration: new URL("@/assets/ringo/celebration.png", import.meta.url).href,
  achievement: new URL("@/assets/ringo/achievement.png", import.meta.url).href,
  proud: new URL("@/assets/ringo/proud.png", import.meta.url).href,
  sad: new URL("@/assets/ringo/sad.png", import.meta.url).href,
  sleeping: new URL("@/assets/ringo/sleeping.png", import.meta.url).href,
  focus: new URL("@/assets/ringo/focus.png", import.meta.url).href,
  victory: new URL("@/assets/ringo/victory.png", import.meta.url).href,
});

export function resolveRingoSprite(spriteKey) {
  const key = RINGO_SPRITE_KEYS.includes(spriteKey) ? spriteKey : "idle";

  return {
    key,
    src: RINGO_SPRITES[key] || RINGO_SPRITES.idle || "",
  };
}