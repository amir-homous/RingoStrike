// B10: one shared number formatter for copy. FA shows Persian digits, EN Latin digits
// (Intl.NumberFormat(locale)). Kept free of Vue so tests can import it.

export function formatNumber(value, locale = "en") {
  const number = Number(value);
  if (value === null || value === undefined || value === "" || !Number.isFinite(number)) {
    return value ?? "";
  }
  return new Intl.NumberFormat(locale || "en").format(number);
}

// Named params with every number formatted for the locale (strings are left as they are).
export function formatNamed(named, locale) {
  if (!named || typeof named !== "object" || Array.isArray(named)) return named;
  return Object.fromEntries(
    Object.entries(named).map(([key, value]) => [key, typeof value === "number" ? formatNumber(value, locale) : value]),
  );
}

// Wraps vue-i18n's t: numbers in named params are formatted, and a numeric `count` also
// selects the plural form (EN "1 object | {count} objects"; FA keeps one form).
export function numberAwareT(t, getLocale) {
  return (key, named, plural) => {
    if (!named || typeof named !== "object" || Array.isArray(named)) {
      return plural === undefined ? t(key, named) : t(key, named, plural);
    }
    const formatted = formatNamed(named, getLocale());
    const count = plural ?? (typeof named.count === "number" ? named.count : undefined);
    return count === undefined ? t(key, formatted) : t(key, formatted, count);
  };
}
