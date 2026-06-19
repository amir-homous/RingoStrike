import en from "@/i18n/locales/en";
import fa from "@/i18n/locales/fa";

const LOCALE_CATALOGS = {
  en,
  fa,
};

function normalizedLocale(locale) {
  return String(locale || "en").toLowerCase().startsWith("fa") ? "fa" : "en";
}

function missionKeyCandidates(mission) {
  const rawKey = String(mission?.key || "").trim();
  if (!rawKey) return [];

  const normalizedDash = rawKey.replace(/_/g, "-");
  const normalizedUnderscore = rawKey.replace(/-/g, "_");
  return [...new Set([rawKey, normalizedDash, normalizedUnderscore])];
}

export function getMissionDisplayCopy(mission, locale) {
  const catalog = LOCALE_CATALOGS[normalizedLocale(locale)]?.missionContent || {};
  const key = missionKeyCandidates(mission).find((candidate) => catalog[candidate]);
  const copy = key ? catalog[key] : null;

  return {
    title: copy?.title || mission?.title || "",
    description: copy?.description || mission?.description || "",
    found: Boolean(copy),
  };
}

export function getMissionDisplayTitle(mission, locale) {
  return getMissionDisplayCopy(mission, locale).title;
}

export function getMissionDisplayDescription(mission, locale) {
  return getMissionDisplayCopy(mission, locale).description;
}
