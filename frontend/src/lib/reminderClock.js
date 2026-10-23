// B34 (#406, D68): the reminder clock next to Ringo. Pure state rule, checked by test:living-space.

export const CLOCK_STATE = Object.freeze({
  NONE: "", // no reminder: the clock is not in the room
  SET: "set", // a reminder later today: a calm clock
  RINGING: "ringing", // a reminder is due: it rings (shake, amber glow; reduced motion: glow only)
});

export function reminderClockState({ due = 0, later = 0 } = {}) {
  if ((Number(due) || 0) > 0) return CLOCK_STATE.RINGING;
  if ((Number(later) || 0) > 0) return CLOCK_STATE.SET;
  return CLOCK_STATE.NONE;
}
