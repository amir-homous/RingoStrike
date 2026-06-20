const actionIconModules = import.meta.glob(
  "../assets/action-icons/{done,remind-later,make-smaller,make-bigger,too-tired,skip,finish-today,view-choices,protect-today,hide-choices,optional-step,explore-paths}.png",
  { eager: true, import: "default" },
);

const ACTION_ICON_ALIASES = {
  complete: "done",
  doneCta: "done",
  remind: "remind-later",
  remindLater: "remind-later",
  makeSmaller: "make-smaller",
  makeBigger: "make-bigger",
  fullVersion: "make-bigger",
  useFullVersion: "make-bigger",
  tiny: "make-smaller",
  tryTiny: "make-smaller",
  tooTired: "too-tired",
  finish: "finish-today",
  finishToday: "finish-today",
  viewChoices: "view-choices",
  protect: "protect-today",
  protectToday: "protect-today",
  hideChoices: "hide-choices",
  optionalStep: "optional-step",
  explorePaths: "explore-paths",
};

export function resolveActionIcon(key) {
  const raw = String(key || "").trim();
  if (!raw) return "";

  const candidates = actionIconCandidates(raw);
  for (const candidate of candidates) {
    const match = Object.entries(actionIconModules).find(([path]) => {
      return path.toLowerCase().endsWith(`/${candidate}.png`);
    });
    if (match?.[1]) return match[1];
  }

  return "";
}

function actionIconCandidates(key) {
  const normalized = key
    .toLowerCase()
    .replace(/_/g, "-")
    .replace(/[^a-z0-9-]+/g, "-")
    .replace(/-+/g, "-")
    .replace(/^-|-$/g, "");

  return Array.from(new Set([
    ACTION_ICON_ALIASES[key],
    ACTION_ICON_ALIASES[normalized],
    normalized,
  ].filter(Boolean)));
}
