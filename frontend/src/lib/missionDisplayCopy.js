import en from "../i18n/locales/en.js";
import fa from "../i18n/locales/fa.js";

const LOCALE_CATALOGS = {
  en,
  fa,
};

function normalizedLocale(locale) {
  return String(locale || "en").toLowerCase().startsWith("fa") ? "fa" : "en";
}

function slugValue(value) {
  return String(value || "")
    .trim()
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-+|-+$/g, "");
}

function keyedContentCandidates(...values) {
  return [...new Set(values
    .flatMap((value) => {
      const raw = String(value || "").trim();
      if (!raw) return [];

      const dash = raw.replace(/_/g, "-");
      const underscore = raw.replace(/-/g, "_");
      const slug = slugValue(raw);

      return [raw, dash, underscore, slug];
    })
    .filter(Boolean))];
}

function missionKeyCandidates(mission) {
  return keyedContentCandidates(mission?.key);
}

function pathKeyCandidates(path) {
  return keyedContentCandidates(path?.key, path?.title, path?.name);
}

function challengeKeyCandidates(challenge) {
  return keyedContentCandidates(
    challenge?.key,
    challenge?.slug,
    challenge?.name,
    challenge?.challenge_name,
    challenge?.title,
  );
}

export function getPathDisplayCopy(path, locale) {
  const catalog = LOCALE_CATALOGS[normalizedLocale(locale)]?.pathContent || {};
  const key = pathKeyCandidates(path).find((candidate) => catalog[candidate]);
  const copy = key ? catalog[key] : null;

  return {
    title: copy?.title || path?.title || path?.name || "",
    description: copy?.description || path?.description || "",
    found: Boolean(copy),
  };
}

export function getChallengeDisplayCopy(challenge, locale) {
  const catalog = LOCALE_CATALOGS[normalizedLocale(locale)]?.challengeContent || {};
  const key = challengeKeyCandidates(challenge).find((candidate) => catalog[candidate]);
  const copy = key ? catalog[key] : null;

  return {
    name: copy?.name || challenge?.name || challenge?.challenge_name || challenge?.title || "",
    description: copy?.description || challenge?.description || "",
    ringo_intro: copy?.ringo_intro || challenge?.ringo_intro || "",
    found: Boolean(copy),
  };
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
