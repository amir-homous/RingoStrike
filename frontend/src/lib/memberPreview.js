// "Joined by" on challenge cards. UI stopgap: a name that contains "@" (an email typed into the
// free-text name field) is never shown; the backend fix filters names at the source.
export function publicPreviewNames(names, limit = 3) {
  if (!Array.isArray(names)) return [];
  return names
    .map((name) => (typeof name === "string" ? name.trim() : ""))
    .filter((name) => name && !name.includes("@"))
    .slice(0, limit);
}
