import { RINGO_SPRITE_KEYS } from "@/constants/ringoSprites";

const SUPPORTED_MOODS = new Set(RINGO_SPRITE_KEYS);

const MOOD_ALIASES = Object.freeze({
  calm: "idle",
  celebrating: "celebration",
  focused: "focus",
  gentle: "happy",
  resting: "sleeping",
});

const STATE_MOOD_FALLBACKS = Object.freeze({
  new_user: "welcome",
  new_user_no_path: "welcome",
  no_active_path: "welcome",
  path_selected_no_challenge: "explaining",
  no_mission_today: "thinking",
  today_not_started: "encouraging",
  today_in_progress: "encouraging",
  today_completed: "celebration",
  today_reminded: "thinking",
  today_skipped: "concerned",
  returning_after_absence: "concerned",
  returning_after_break: "concerned",
  streak_risk: "warning",
  streak_at_risk: "warning",
  low_energy: "sleeping",
  high_momentum: "victory",
});

function normalizedValue(value) {
  return String(value || "")
    .trim()
    .toLowerCase()
    .replace(/[\s-]+/g, "_");
}

export function normalizeRingoMoodKey(value) {
  const normalized = normalizedValue(value);
  const aliased = MOOD_ALIASES[normalized] || normalized;

  return SUPPORTED_MOODS.has(aliased) ? aliased : "";
}

export function moodFromRingoState(state) {
  return normalizeRingoMoodKey(STATE_MOOD_FALLBACKS[normalizedValue(state)]);
}

export function normalizeRingoMood(source, fallback = "idle") {
  const payload = source && typeof source === "object"
    ? source
    : { sprite_key: source };

  return normalizeRingoMoodKey(payload.sprite_key)
    || normalizeRingoMoodKey(payload.sprite)
    || normalizeRingoMoodKey(payload.mood)
    || moodFromRingoState(payload.user_state || payload.state)
    || normalizeRingoMoodKey(fallback)
    || "idle";
}
