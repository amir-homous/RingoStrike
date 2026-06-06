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

const FALLBACK_SPRITES = Object.freeze({
  talking: "explaining",
  concerned: "warning",
});

const spriteModules = import.meta.glob("../assets/ringo/*.png", {
  eager: true,
  import: "default",
  query: "?url",
});

export const RINGO_SPRITES = Object.freeze(
  Object.entries(spriteModules).reduce((sprites, [path, src]) => {
    const filename = path.split("/").pop() || "";
    const key = filename.replace(".png", "");

    sprites[key] = src;
    return sprites;
  }, {}),
);

export const RINGO_MOOD_CONTEXTS = Object.freeze({
  welcome: "welcome",
  onboardingPath: "thinking",
  onboardingPathSelected: "focus",
  onboardingSuggestion: "encouraging",
  onboardingFallback: "explaining",
  joinCreated: "happy",
  joinExisting: "thinking",
  rewardDefault: "proud",
  rewardAchievement: "achievement",
  rewardUnlock: "celebration",
  rewardStreak: "victory",
  rewardXp: "encouraging",
});

export function resolveRingoSprite(spriteKey) {
  const requestedKey = RINGO_SPRITE_KEYS.includes(spriteKey) ? spriteKey : "idle";
  const fallbackKey = FALLBACK_SPRITES[requestedKey] || "idle";
  const key = RINGO_SPRITES[requestedKey] ? requestedKey : fallbackKey;

  return {
    key,
    src: RINGO_SPRITES[key] || RINGO_SPRITES.idle || "",
  };
}

export function resolveRingoMood(contextKey, fallback = "idle") {
  return RINGO_MOOD_CONTEXTS[contextKey] || fallback;
}
