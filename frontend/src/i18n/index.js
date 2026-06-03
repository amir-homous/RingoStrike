import { createI18n } from "vue-i18n";
import en from "./locales/en";
import fa from "./locales/fa";

export const SUPPORTED_LOCALES = ["en", "fa"];
export const DEFAULT_LOCALE = "en";
export const LOCALE_STORAGE_KEY = "ringostrike_locale";

function normalizeLocale(value) {
  return SUPPORTED_LOCALES.includes(value) ? value : DEFAULT_LOCALE;
}

export function getInitialLocale() {
  const stored = localStorage.getItem(LOCALE_STORAGE_KEY);
  if (SUPPORTED_LOCALES.includes(stored)) return stored;

  const browserLocale = navigator.language?.slice(0, 2);
  return normalizeLocale(browserLocale);
}

export function getLocaleDirection(locale) {
  return locale === "fa" ? "rtl" : "ltr";
}

export function syncDocumentLocale(locale) {
  const normalized = normalizeLocale(locale);
  document.documentElement.lang = normalized;
  document.documentElement.dir = getLocaleDirection(normalized);
}

const initialLocale = getInitialLocale();

export const i18n = createI18n({
  legacy: false,
  globalInjection: true,
  locale: initialLocale,
  fallbackLocale: DEFAULT_LOCALE,
  messages: {
    en,
    fa,
  },
});

syncDocumentLocale(initialLocale);

export function setLocale(locale) {
  const normalized = normalizeLocale(locale);
  i18n.global.locale.value = normalized;
  localStorage.setItem(LOCALE_STORAGE_KEY, normalized);
  syncDocumentLocale(normalized);
}
