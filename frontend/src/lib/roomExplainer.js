// B37 (D83, D84): the "What am I looking at?" box under Ringo's first card.

// D84: say "with others" only when the data supports it: the challenge has at least one other
// active member (members_count from GET /challenges/{id}). No number is ever shown.
export function challengeLineKey(membersCount) {
  return Number(membersCount) >= 2 ? "challengesWithOthers" : "challenges";
}

// The rows, in pin order: 1 the corner, 2 the challenge icons, 3 the steps (paws).
export const EXPLAINER_ROWS = ["corner", "challenges", "steps"];

// Shown once, on the first arrival from onboarding, until "Got it" (remembered per user).
export function shouldShowExplainer({ firstRun, seen }) {
  return Boolean(firstRun) && !seen;
}
