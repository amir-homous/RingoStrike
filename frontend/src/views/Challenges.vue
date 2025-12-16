<template>
  <div style="padding:32px; max-width:900px; margin:auto">
    <!-- Header -->
    <div style="display:flex; justify-content:space-between; align-items:center; gap:16px">
      <div>
        <h1 style="margin:0">Challenges</h1>
        <div style="margin-top:6px; opacity:.7; font-size:14px">
          Browse public / invite-only challenges and join.
        </div>
      </div>

      <div style="display:flex; gap:10px; align-items:center; flex-wrap:wrap">
        <a :href="base + 'dashboard'" style="text-decoration:none">← Back to Dashboard</a>

        <button
          @click="load"
          :disabled="loading"
          style="padding:8px 12px; border-radius:10px; border:1px solid #ddd; background:#fff; cursor:pointer"
        >
          <span v-if="loading">...</span>
          <span v-else>Refresh</span>
        </button>
      </div>
    </div>

    <!-- Loading -->
    <div v-if="loading" style="margin-top:16px">Loading...</div>

    <!-- Content -->
    <div v-else style="margin-top:16px">
      <div v-if="loadError" style="color:#b00020; margin-bottom:14px">
        {{ loadError }}
      </div>

      <div v-if="items.length === 0" style="opacity:.7">
        No challenges available.
      </div>

      <div
        v-for="ch in items"
        :key="ch.challenge_id"
        style="border:1px solid #ddd; border-radius:12px; padding:16px; margin-top:14px"
      >
        <div style="display:flex; justify-content:space-between; align-items:flex-start; gap:16px">
          <!-- Left: content -->
          <div style="min-width:0; flex:1">
            <h3 style="margin:0 0 6px 0">{{ ch.name }}</h3>

            <div style="font-size:14px; opacity:.7">
              {{ ch.visibility }} • {{ ch.status }} •
              <span v-if="ch.duration_days">Duration: {{ ch.duration_days }} days</span>
              <span v-else>Duration: —</span>
            </div>

            <p v-if="ch.description" style="margin:10px 0 0 0; opacity:.85; line-height:1.5">
              {{ ch.description }}
            </p>

            <!-- Social proof -->
            <div style="margin-top:10px; opacity:.85; font-size:14px">
              <b>{{ ch.members_count || 0 }}</b> members
              <span v-if="ch.members_preview?.length" style="opacity:.75">
                • e.g. {{ ch.members_preview.join(", ") }}
              </span>
              <span v-else style="opacity:.75">
                • Be the first!
              </span>
            </div>

            <!-- Invite code input (only when needed AND not joined yet) -->
            <div v-if="ch.needs_code && !ch.is_joined" style="margin-top:12px">
              <label style="display:block; font-size:13px; opacity:.7; margin-bottom:6px">
                Invite code
              </label>
              <input
                v-model="codes[ch.challenge_id]"
                placeholder="Enter code"
                style="padding:10px 12px; border-radius:10px; border:1px solid #ddd; width:260px"
              />
            </div>

            <!-- Per-item error -->
            <div v-if="errors[ch.challenge_id]" style="margin-top:10px; color:#b00020">
              {{ errors[ch.challenge_id] }}
            </div>
          </div>

          <!-- Right: actions -->
          <div style="display:flex; gap:10px; align-items:center; flex-shrink:0">
            <button
              v-if="!ch.is_joined"
              @click="join(ch)"
              :disabled="joiningId === ch.challenge_id"
              style="padding:10px 16px; border-radius:10px; border:none; cursor:pointer"
            >
              <span v-if="joiningId === ch.challenge_id">...</span>
              <span v-else>Join</span>
            </button>

            <button
              v-else
              @click="open(ch)"
              style="padding:10px 16px; border-radius:10px; border:1px solid #ddd; background:#fff; cursor:pointer"
            >
              Joined ✅ Open
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted, ref } from "vue";
import api from "../lib/api";

const base = import.meta.env.BASE_URL;

const loading = ref(true);
const loadError = ref("");

const items = ref([]);
const joiningId = ref(null);

const codes = ref({});
const errors = ref({});

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

    // ✅ حرفه‌ای‌تر: همونجا لیست رو refresh کن تا Joined/Open نمایش داده شود
    await load();
  } catch (e) {
    const msg = e?.response?.data?.error || e?.message || String(e);
    errors.value[ch.challenge_id] = msg;
  } finally {
    joiningId.value = null;
  }
}

function open(ch) {
  // enrollment_id از backend میاد وقتی is_joined=true
  window.location.href = `${base}enrollment/${ch.enrollment_id}`;
}

onMounted(load);
</script>
