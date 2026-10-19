// B10: backend reward_sequence English and its i18n keys. Kept free of Vue and aliases so tests can import it.

// Fixed English copy sent by backend reward_sequence steps (mission_service._build_reward_sequence),
// mapped to i18n keys so FA mode does not show English.
export const BACKEND_STEP_COPY = {
  "Nice work.": "ringoRewardSequence.backend.niceWorkTitle",
  "You did the small step. That counts.": "ringoRewardSequence.backend.smallStepText",
  "You added another small win to today.": "ringoRewardSequence.backend.addedWinText",
  "This mission is marked done.": "ringoRewardSequence.backend.missionDoneText",
  "XP earned": "ringoRewardSequence.backend.xpTitle",
  "Today is safe.": "ringoRewardSequence.backend.todaySafeTitle",
  "You did enough for today. Anything else is optional.": "ringoRewardSequence.backend.todaySafeText",
  "Bonus momentum.": "ringoRewardSequence.backend.bonusTitle",
  "Today was already safe. This was optional extra progress.": "ringoRewardSequence.backend.bonusText",
  "Choose your pace.": "ringoRewardSequence.backend.paceTitle",
  "You can stop here, or continue only if you have energy.": "ringoRewardSequence.backend.paceText",
};

// Backend sentences are English. Mapped ones are translated; an unmapped one is shown as is in EN
// but never in another locale: there the title becomes the generic localized line and the body is
// dropped (B10).
export function localizeBackendCopy(value, translate, { role = "text" } = {}) {
  const text = String(value || "").trim();
  if (!text) return value;
  const key = BACKEND_STEP_COPY[text];
  if (key) return translate(key);
  if ((translate.locale || "en") === "en") return value;
  return role === "title" ? translate("ringoRewardSequence.fallbackTitle") : "";
}
