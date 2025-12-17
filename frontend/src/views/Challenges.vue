<template>
  <AppContainer>
    <AppHeader />

    <div class="stack-16">
      <!-- Page header -->
      <div class="pageHead">
        <div class="stack-8">
          <h1 class="h1">Challenges</h1>
          <div class="caption">
            Browse public / invite-only challenges and join.
          </div>
        </div>

        <div class="actions">
          <BaseButton variant="secondary" :loading="loading" @click="load">
            Refresh
          </BaseButton>
        </div>
      </div>

      <!-- State / content -->
      <BaseCard>
        <UiState :loading="loading" :error="!!loadError" :empty="!loading && !loadError && items.length === 0"
          loading-title="Loading challenges…" loading-text="Fetching available challenges."
          empty-title="No challenges available" empty-text="Create one or ask for an invite code."
          error-title="Couldn’t load challenges" :error-text="loadError || 'Please try again.'" @retry="load" />

        <div v-if="!loading && !loadError && items.length" class="list">
          <BaseCard v-for="ch in items" :key="ch.challenge_id" class="itemCard" :padded="true">
            <div class="row">
              <!-- left -->
              <div class="content">
                <div class="titleRow">
                  <h2 class="h2 title">{{ ch.name }}</h2>

                  <div class="badges">
                    <span class="badge">
                      <span aria-hidden="true">{{ ch.visibility === "public" ? "🔓" : "🔒" }}</span>
                      {{ ch.visibility || "—" }}
                    </span>

                    <span class="badge">
                      <span aria-hidden="true">{{ ch.status === "active" ? "🟢" : "⚪️" }}</span>
                      {{ ch.status || "—" }}
                    </span>

                    <span class="badge">
                      <span aria-hidden="true">🗓️</span>
                      {{ ch.duration_days ? `${ch.duration_days} days` : "—" }}
                    </span>
                  </div>
                </div>

                <p v-if="ch.description" class="desc">
                  {{ ch.description }}
                </p>

                <div class="social">
                  <span class="members">
                    <span aria-hidden="true">👥</span>
                    <b>{{ ch.members_count || 0 }}</b> members
                  </span>

                  <span v-if="ch.members_preview?.length" class="caption">
                    • e.g. {{ ch.members_preview.join(", ") }}
                  </span>
                  <span v-else class="caption">• Be the first!</span>
                </div>

                <!-- Invite code -->
                <div v-if="ch.needs_code && !ch.is_joined" class="inviteBox">
                  <label class="capLabel" :for="`code-${ch.challenge_id}`">
                    <span aria-hidden="true">🔑</span> Invite code
                  </label>

                  <div class="inviteRow">
                    <input :id="`code-${ch.challenge_id}`" v-model="codes[ch.challenge_id]" class="input"
                      placeholder="Enter code" autocomplete="off" inputmode="text" />

                    <span class="hint caption">
                      Required
                    </span>
                  </div>

                  <div v-if="errors[ch.challenge_id]" class="err">
                    {{ humanizeError(errors[ch.challenge_id]) }}
                  </div>
                </div>

                <!-- per-item error (non invite) -->
                <div v-else-if="errors[ch.challenge_id]" class="err">
                  {{ humanizeError(errors[ch.challenge_id]) }}
                </div>
              </div>

              <!-- right -->
              <div class="side">
                <BaseButton v-if="!ch.is_joined" variant="primary" :loading="joiningId === ch.challenge_id"
                  @click="join(ch)">
                  Join 🚀
                </BaseButton>

                <BaseButton v-else variant="secondary" @click="open(ch)">
                  Joined ✅ Open
                </BaseButton>
              </div>
            </div>
          </BaseCard>
        </div>
      </BaseCard>
    </div>
  </AppContainer>
</template>

<script setup>
import { onMounted, ref } from "vue";
import { useRouter } from "vue-router";
import api from "../lib/api";

import AppContainer from "@/components/ui/AppContainer.vue";
import AppHeader from "@/components/ui/AppHeader.vue";
import BaseCard from "@/components/ui/BaseCard.vue";
import BaseButton from "@/components/ui/BaseButton.vue";
import UiState from "@/components/ui/UiState.vue";

const router = useRouter();

const loading = ref(true);
const loadError = ref("");

const items = ref([]);
const joiningId = ref(null);

const codes = ref({});
const errors = ref({});

function humanizeError(msg) {
  if (!msg) return "";
  if (msg === "invite_code_required") return "Invite code is required.";
  if (typeof msg === "string") return msg.replaceAll("_", " ");
  return String(msg);
}

async function load() {
  loading.value = true;
  loadError.value = "";

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

async function join(ch) {
  errors.value[ch.challenge_id] = "";
  joiningId.value = ch.challenge_id;

  try {
    if (ch.needs_code) {
      const code = (codes.value[ch.challenge_id] || "").trim();
      if (!code) {
        errors.value[ch.challenge_id] = "invite_code_required";
        return;
      }
      await api.post(`/challenges/${ch.challenge_id}/join`, { join_code: code });
    } else {
      await api.post(`/challenges/${ch.challenge_id}/join`, {});
    }

    await load();
  } catch (e) {
    const msg = e?.response?.data?.error || e?.message || String(e);
    errors.value[ch.challenge_id] = msg;
  } finally {
    joiningId.value = null;
  }
}

function open(ch) {
  // ✅ SPA navigation (بدون refresh)
  router.push(`/enrollment/${ch.enrollment_id}`);
}

onMounted(load);
</script>

<style scoped>
.pageHead {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  gap: var(--s-16);
  flex-wrap: wrap;
}

.actions {
  display: flex;
  gap: var(--s-12);
  align-items: center;
  flex-wrap: wrap;
}

.ghostLink {
  color: rgba(255, 255, 255, 0.85);
  text-decoration: none;
  padding: 8px 10px;
  border-radius: 10px;
  border: 1px solid rgba(255, 255, 255, 0.10);
  background: rgba(255, 255, 255, 0.03);
}

.ghostLink:hover {
  background: rgba(255, 255, 255, 0.06);
}

.list {
  margin-top: var(--s-16);
  display: grid;
  gap: var(--s-12);
}

.itemCard {
  background: rgba(255, 255, 255, 0.02);
  border: 1px solid rgba(255, 255, 255, 0.08);
  box-shadow: none;
}

.row {
  display: flex;
  gap: var(--s-16);
  align-items: flex-start;
  justify-content: space-between;
  flex-wrap: wrap;
}

.content {
  min-width: 0;
  flex: 1;
  display: grid;
  gap: var(--s-10);
}

.side {
  display: flex;
  gap: var(--s-10);
  align-items: center;
  flex-shrink: 0;
}

.titleRow {
  display: flex;
  gap: var(--s-12);
  align-items: flex-start;
  justify-content: space-between;
  flex-wrap: wrap;
}

.title {
  margin: 0;
}

.badges {
  display: flex;
  gap: var(--s-8);
  flex-wrap: wrap;
  align-items: center;
}

.badge {
  font-size: var(--cap);
  color: rgba(255, 255, 255, 0.85);
  padding: 6px 10px;
  border-radius: 999px;
  border: 1px solid rgba(255, 255, 255, 0.10);
  background: rgba(255, 255, 255, 0.03);
  display: inline-flex;
  gap: 6px;
  align-items: center;
}

.desc {
  margin: 0;
  opacity: 0.9;
  line-height: 1.55;
}

.social {
  display: flex;
  gap: var(--s-8);
  flex-wrap: wrap;
  align-items: baseline;
  opacity: 0.9;
}

.members {
  display: inline-flex;
  gap: 6px;
  align-items: center;
}

.inviteBox {
  margin-top: 2px;
  padding-top: var(--s-8);
}

.capLabel {
  display: block;
  font-size: var(--cap);
  color: var(--muted2);
  margin-bottom: var(--s-6);
}

.inviteRow {
  display: flex;
  gap: var(--s-8);
  align-items: center;
  flex-wrap: wrap;
}

.input {
  width: 260px;
  max-width: 100%;
  padding: 10px 12px;
  border-radius: 10px;
  border: 1px solid rgba(255, 255, 255, 0.12);
  background: rgba(0, 0, 0, 0.25);
  color: rgba(255, 255, 255, 0.92);
  outline: none;
}

.input:focus {
  border-color: rgba(99, 102, 241, 0.45);
  box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.18);
}

.hint {
  opacity: 0.8;
}

.err {
  margin-top: var(--s-8);
  color: rgba(255, 80, 80, 0.95);
  font-size: var(--cap);
}
</style>
