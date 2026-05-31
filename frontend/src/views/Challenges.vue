<template>
  <AppContainer>
    <AppHeader />

    <div class="challengesPage">
      <section class="heroCard">
        <div class="heroGlow"></div>

        <div class="heroContent">
          <div class="heroMain">
            <div class="eyebrow">
              <span class="pulseDot"></span>
              Challenge Discovery
            </div>

            <h1 class="heroTitle">
              Choose your next progression path.
            </h1>

            <p class="heroText">
              Start with a curated launch challenge, build daily momentum,
              and turn consistency into visible progression identity.
            </p>

            <div class="heroPills">
              <span class="heroPill">Consistency</span>
              <span class="heroPill">Momentum</span>
              <span class="heroPill">XP Growth</span>
              <span class="heroPill">Social Standings</span>
            </div>
          </div>

          <div class="heroStats">
            <div class="heroStat">
              <span class="statValue">{{ items.length }}</span>
              <span class="statLabel">Available</span>
            </div>

            <div class="heroStat joined">
              <span class="statValue">{{ joinedCount }}</span>
              <span class="statLabel">Joined</span>
            </div>

            <div class="heroStat invite">
              <span class="statValue">{{ inviteOnlyCount }}</span>
              <span class="statLabel">Invite-only</span>
            </div>
          </div>
        </div>
      </section>

      <section class="discoveryPanel">
        <div class="toolbar">
          <div>
            <div class="eyebrow compact">Launch Defaults</div>
            <h2 class="sectionTitle">Available Challenges</h2>
            <p class="sectionText">
              Pick one path first. RingoStrike works best when your daily loop is simple,
              visible, and easy to repeat.
            </p>
          </div>

          <div class="actions">
            <BaseButton
              variant="secondary"
              :loading="loading"
              @click="load"
            >
              Refresh
            </BaseButton>
          </div>
        </div>

        <div class="controls">
          <div class="searchBox">
            <span aria-hidden="true">⌕</span>
            <input
              v-model="search"
              type="search"
              placeholder="Search challenges..."
            />
          </div>

          <div class="segmentedControl" aria-label="Challenge filter">
            <button
              type="button"
              :class="{ active: filter === 'all' }"
              @click="setFilter('all')"
            >
              All
            </button>

            <button
              type="button"
              :class="{ active: filter === 'available' }"
              @click="setFilter('available')"
            >
              Available
            </button>

            <button
              type="button"
              :class="{ active: filter === 'joined' }"
              @click="setFilter('joined')"
            >
              Joined
            </button>

            <button
              type="button"
              :class="{ active: filter === 'invite' }"
              @click="setFilter('invite')"
            >
              Invite-only
            </button>
          </div>
        </div>

        <BaseCard class="listCard">
          <UiState
            :loading="loading"
            :error="!!loadError"
            :empty="!loading && !loadError && filteredItems.length === 0"
            loading-title="Loading challenges…"
            loading-text="Fetching available progression paths."
            empty-title="No matching challenges"
            empty-text="Try another filter or refresh the challenge list."
            error-title="Couldn’t load challenges"
            :error-text="loadError || 'Please try again.'"
            @retry="load"
          />

          <div
            v-if="!loading && !loadError && filteredItems.length"
            class="list"
          >
            <div
              v-for="ch in visibleItems"
              :key="ch.challenge_id"
              class="challengeShell"
            >
              <ChallengeCard
                :challenge="ch"
                :loading="joiningId === ch.challenge_id"
                :show-join="!ch.is_joined"
                :show-checkin="false"
                @join="join(ch)"
              />

              <div
                v-if="(isInviteOnly(ch) || ch.needs_code) && !ch.is_joined"
                class="inviteBox"
              >
                <div class="inviteCopy">
                  <label
                    class="capLabel"
                    :for="`code-${ch.challenge_id}`"
                  >
                    Invite code required
                  </label>

                  <div class="caption">
                    This path is private to a group. Enter your code to unlock access.
                  </div>
                </div>

                <div class="inviteControls">
                  <input
                    :id="`code-${ch.challenge_id}`"
                    v-model="codes[ch.challenge_id]"
                    class="input"
                    placeholder="Enter code..."
                    @keyup.enter="join(ch)"
                  />

                  <BaseButton
                    variant="secondary"
                    :loading="joiningId === ch.challenge_id"
                    @click="join(ch)"
                  >
                    Unlock
                  </BaseButton>
                </div>
              </div>

              <div
                v-if="errors[ch.challenge_id]"
                class="err"
              >
                {{ humanizeError(errors[ch.challenge_id]) }}
              </div>
            </div>

            <button
              v-if="hasHiddenItems"
              type="button"
              class="showMoreButton"
              @click="showAll = !showAll"
            >
              <span>
                {{ showAll ? "Show fewer" : `Show ${filteredItems.length - itemLimit} more` }}
              </span>

              <span aria-hidden="true">
                {{ showAll ? "↑" : "↓" }}
              </span>
            </button>
          </div>
        </BaseCard>
      </section>
    </div>
  </AppContainer>
</template>

<script setup>
import { computed, onMounted, ref } from "vue";
import { useRouter } from "vue-router";
import api from "@/lib/api";

import AppContainer from "@/components/ui/AppContainer.vue";
import AppHeader from "@/components/ui/AppHeader.vue";
import BaseCard from "@/components/ui/BaseCard.vue";
import BaseButton from "@/components/ui/BaseButton.vue";
import UiState from "@/components/ui/UiState.vue";
import ChallengeCard from "@/components/challenges/ChallengeCard.vue";

const router = useRouter();

const loading = ref(true);
const loadError = ref("");

const items = ref([]);
const joiningId = ref(null);

const codes = ref({});
const errors = ref({});

const search = ref("");
const filter = ref("all");
const showAll = ref(false);

const itemLimit = 6;

const joinedCount = computed(() => {
  return items.value.filter((item) => item.is_joined).length;
});

const inviteOnlyCount = computed(() => {
  return items.value.filter((item) => isInviteOnly(item) || item.needs_code).length;
});

function isInviteOnly(challenge) {
  return String(challenge.visibility || "").toLowerCase() === "invite-only";
}

const filteredItems = computed(() => {
  const query = search.value.trim().toLowerCase();

  return items.value.filter((item) => {
    const title = String(item.name || item.enrollment_name || item.challenge_name || "").toLowerCase();
    const description = String(item.description || "").toLowerCase();
    const visibility = String(item.visibility || "").toLowerCase();

    const matchesSearch =
      !query ||
      title.includes(query) ||
      description.includes(query) ||
      visibility.includes(query);

    if (!matchesSearch) return false;

    if (filter.value === "available") return !item.is_joined;
    if (filter.value === "joined") return Boolean(item.is_joined);
    if (filter.value === "invite") return isInviteOnly(item) || item.needs_code;

    return true;
  });
});

const visibleItems = computed(() => {
  if (showAll.value) return filteredItems.value;
  return filteredItems.value.slice(0, itemLimit);
});

const hasHiddenItems = computed(() => {
  return filteredItems.value.length > itemLimit;
});

function setFilter(value) {
  filter.value = value;
  showAll.value = false;
}

function humanizeError(msg) {
  if (!msg) return "";
  if (msg === "invite_code_required") return "Invite code is required.";
  if (msg === "join_code_required") return "Invite code is required.";
  if (msg === "invalid_join_code") return "Invalid invite code.";
  if (msg === "invalid_join_code_type") return "Invite code must be text.";
  if (msg === "join_code_too_long") return "Invite code is too long.";
  if (msg === "challenge_private") return "This challenge is private.";
  if (msg === "challenge_inactive") return "This challenge is not active.";
  if (typeof msg === "string") return msg.replaceAll("_", " ");
  return String(msg);
}

async function load() {
  loading.value = true;
  loadError.value = "";
  errors.value = {};

  try {
    const { data } = await api.get("/challenges");
    items.value = data.items || [];
  } catch (e) {
    loadError.value = e?.response?.data?.error || e?.message || String(e);
    items.value = [];
  } finally {
    loading.value = false;
  }
}

async function join(challenge) {
  errors.value[challenge.challenge_id] = "";
  joiningId.value = challenge.challenge_id;

  const needsCode = isInviteOnly(challenge) || challenge.needs_code;

  try {
    let payload = {};

    if (needsCode) {
      const code = (codes.value[challenge.challenge_id] || "").trim();

      if (!code) {
        errors.value[challenge.challenge_id] = "invite_code_required";
        joiningId.value = null;
        return;
      }

      payload = { join_code: code };
    }

    const { data } = await api.post(`/challenges/${challenge.challenge_id}/join`, payload);

    if (data?.enrollment_id) {
      router.push(`/enrollment/${data.enrollment_id}`);
      return;
    }

    await load();
  } catch (e) {
    const msg = e?.response?.data?.error || e?.message || String(e);
    errors.value[challenge.challenge_id] = msg;
  } finally {
    joiningId.value = null;
  }
}

onMounted(load);
</script>

<style scoped>
.challengesPage {
  display: grid;
  gap: var(--s-16);
}

.heroCard {
  position: relative;
  overflow: hidden;
  border-radius: 28px;
  padding: 30px;
  border: 1px solid rgba(255, 255, 255, 0.10);
  background:
    radial-gradient(circle at 12% 18%, rgba(110, 229, 255, 0.18), transparent 34%),
    radial-gradient(circle at 88% 8%, rgba(195, 90, 214, 0.16), transparent 32%),
    linear-gradient(135deg, rgba(255, 255, 255, 0.085), rgba(255, 255, 255, 0.025));
  box-shadow: 0 28px 90px rgba(0, 0, 0, 0.32);
}

.heroGlow {
  position: absolute;
  inset: -90px;
  background:
    linear-gradient(90deg, transparent, rgba(110, 229, 255, 0.07), transparent),
    radial-gradient(circle, rgba(255, 255, 255, 0.07), transparent 58%);
  pointer-events: none;
}

.heroContent {
  position: relative;
  z-index: 1;
  display: grid;
  grid-template-columns: minmax(0, 1fr) 340px;
  gap: var(--s-24);
  align-items: center;
}

.eyebrow {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  margin: 0 0 7px;
  color: rgba(110, 229, 255, 0.9);
  font-size: 0.72rem;
  font-weight: 850;
  text-transform: uppercase;
  letter-spacing: 0.14em;
}

.eyebrow.compact {
  margin-bottom: 8px;
}

.pulseDot {
  width: 7px;
  height: 7px;
  border-radius: 999px;
  background: #4ade80;
  box-shadow: 0 0 16px rgba(74, 222, 128, 0.7);
}

.heroTitle {
  margin: 0;
  max-width: 820px;
  color: white;
  font-size: clamp(2rem, 4.4vw, 4.2rem);
  line-height: 0.96;
  letter-spacing: -0.06em;
}

.heroText {
  max-width: 720px;
  margin: var(--s-16) 0 0;
  color: rgba(255, 255, 255, 0.72);
  line-height: 1.7;
}

.heroPills {
  display: flex;
  flex-wrap: wrap;
  gap: var(--s-8);
  margin-top: var(--s-20);
}

.heroPill {
  padding: 7px 11px;
  border-radius: 999px;
  color: rgba(255, 255, 255, 0.82);
  background: rgba(255, 255, 255, 0.055);
  border: 1px solid rgba(255, 255, 255, 0.10);
  font-size: 0.78rem;
  font-weight: 750;
}

.heroStats {
  display: grid;
  gap: var(--s-10);
}

.heroStat {
  padding: 16px;
  border-radius: 22px;
  text-align: right;
  background:
    radial-gradient(circle at 0% 0%, rgba(110, 229, 255, 0.10), transparent 38%),
    rgba(0, 0, 0, 0.20);
  border: 1px solid rgba(255, 255, 255, 0.10);
  margin-top: 10px;
}

.heroStat.joined {
  border-color: rgba(74, 222, 128, 0.18);
}

.heroStat.invite {
  border-color: rgba(255, 228, 168, 0.18);
}

.statValue {
  display: block;
  color: white;
  font-size: 2rem;
  line-height: 1;
  font-weight: 900;
  font-variant-numeric: tabular-nums;
}

.statLabel {
  display: block;
  margin-top: 5px;
  color: var(--muted2);
  font-size: 0.76rem;
  font-weight: 800;
  text-transform: uppercase;
  letter-spacing: 0.08em;
}

.discoveryPanel {
  display: grid;
  gap: var(--s-12);
}

.toolbar {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  gap: var(--s-16);
  flex-wrap: wrap;
}

.sectionTitle {
  margin: 0;
  color: rgba(255, 255, 255, 0.94);
  letter-spacing: -0.04em;
}

.sectionText {
  margin: 8px 0 0;
  max-width: 720px;
  color: rgba(255, 255, 255, 0.62);
  line-height: 1.65;
}

.actions {
  display: flex;
  gap: var(--s-12);
  align-items: center;
  flex-wrap: wrap;
}

.controls {
  display: grid;
  grid-template-columns: minmax(240px, 0.8fr) minmax(0, 1.2fr);
  gap: var(--s-12);
  align-items: center;
}

.searchBox {
  display: flex;
  align-items: center;
  gap: 9px;
  min-height: 44px;
  padding: 0 13px;
  border-radius: 16px;
  color: rgba(255, 255, 255, 0.54);
  background: rgba(255, 255, 255, 0.035);
  border: 1px solid rgba(255, 255, 255, 0.085);
}

.searchBox input {
  width: 100%;
  border: 0;
  outline: 0;
  color: rgba(255, 255, 255, 0.92);
  background: transparent;
}

.searchBox input::placeholder {
  color: rgba(255, 255, 255, 0.42);
}

.segmentedControl {
  justify-self: end;
  display: inline-flex;
  flex-wrap: wrap;
  align-items: center;
  padding: 4px;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid rgba(255, 255, 255, 0.085);
}

.segmentedControl button {
  min-height: 34px;
  padding: 7px 12px;
  border: 0;
  border-radius: 999px;
  color: rgba(255, 255, 255, 0.60);
  background: transparent;
  cursor: pointer;
  font-weight: 850;
}

.segmentedControl button.active {
  color: rgba(255, 255, 255, 0.94);
  background: rgba(110, 229, 255, 0.13);
}

.listCard {
  background:
    radial-gradient(circle at 100% 0%, rgba(110, 229, 255, 0.045), transparent 34%),
    rgba(255, 255, 255, 0.024);
}

.list {
  margin-top: var(--s-16);
  display: grid;
  gap: var(--s-14);
}

.challengeShell {
  display: grid;
  gap: var(--s-8);
}

.inviteBox {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: var(--s-12);
  padding: 14px;
  margin: 0 4px;
  border-radius: 18px;
  border: 1px solid rgba(255, 228, 168, 0.14);
  background:
    radial-gradient(circle at 0% 0%, rgba(255, 228, 168, 0.08), transparent 36%),
    rgba(255, 255, 255, 0.025);
  flex-wrap: wrap;
}

.inviteCopy {
  min-width: 220px;
}

.capLabel {
  display: block;
  color: rgba(255, 228, 168, 0.95);
  font-size: 0.78rem;
  font-weight: 850;
  text-transform: uppercase;
  letter-spacing: 0.10em;
  margin-bottom: 3px;
}

.inviteControls {
  display: flex;
  gap: var(--s-8);
  align-items: center;
  flex-wrap: wrap;
}

.input {
  width: 260px;
  max-width: 100%;
  padding: 11px 12px;
  border-radius: 12px;
  border: 1px solid rgba(255, 255, 255, 0.12);
  background: rgba(0, 0, 0, 0.25);
  color: rgba(255, 255, 255, 0.92);
  outline: none;
}

.input:focus {
  border-color: rgba(110, 229, 255, 0.45);
  box-shadow: 0 0 0 3px rgba(110, 229, 255, 0.14);
}

.err {
  margin: 0 8px;
  color: rgba(255, 100, 100, 0.95);
  font-size: var(--cap);
  font-weight: 700;
}

.caption {
  color: var(--muted2);
  font-size: 0.85rem;
  line-height: 1.45;
}

.showMoreButton {
  justify-self: center;
  display: inline-flex;
  align-items: center;
  gap: var(--s-8);
  min-height: 40px;
  padding: 10px 15px;
  border-radius: 999px;
  color: rgba(255, 255, 255, 0.82);
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid rgba(255, 255, 255, 0.10);
  cursor: pointer;
  font-weight: 850;
  margin-top: 10px;
}

.showMoreButton:hover {
  background: rgba(255, 255, 255, 0.065);
  border-color: rgba(110, 229, 255, 0.25);
}

@media (max-width: 900px) {
  .heroContent,
  .controls {
    grid-template-columns: 1fr;
  }

  .heroStats {
    grid-template-columns: repeat(3, minmax(0, 1fr));
  }

  .heroStat {
    text-align: left;
  }

  .segmentedControl {
    justify-self: start;
  }
}

@media (max-width: 620px) {
  .heroCard {
    padding: 22px;
    border-radius: 22px;
  }

  .heroStats {
    grid-template-columns: 1fr;
  }

  .heroTitle {
    font-size: 2.2rem;
  }

  .segmentedControl {
    width: 100%;
    border-radius: 18px;
  }

  .segmentedControl button {
    flex: 1;
  }

  .inviteControls {
    width: 100%;
  }

  .input {
    width: 100%;
  }
}
</style>