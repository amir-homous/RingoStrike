<template>
  <div style="padding:32px; max-width:900px; margin:auto">
    <div style="display:flex; justify-content:space-between; align-items:flex-start; gap:16px">
      <div>
        <h1 style="margin:0 0 6px 0">Dashboard</h1>
        <p v-if="user" style="opacity:.7; margin:0">
          Welcome, <b>{{ user.name }}</b> — {{ date }}
        </p>
      </div>


      <button
        @click="doLogout"
        :disabled="loggingOut"
        style="padding:10px 14px; border-radius:10px; border:1px solid #ddd; background:#fff; cursor:pointer"
      >
        <span v-if="loggingOut">...</span>
        <span v-else>Logout</span>
      </button>
      <a :href="base + 'challenges'" style="display:inline-block; margin-top:10px">
  Browse Challenges
</a>

    </div>

    <div v-if="loading" style="margin-top:24px">Loading...</div>

    <div v-else style="margin-top:16px">
      <div v-if="challenges.length === 0" style="margin-top:24px">
        No active challenges.
      </div>

      <div
        v-for="c in challenges"
        :key="c.enrollment_id"
        style="
          border:1px solid #ddd;
          border-radius:12px;
          padding:16px;
          margin-top:16px;
          display:flex;
          justify-content:space-between;
          align-items:center;
          gap:16px;
        "
      >
        <div style="min-width:0">
          <h3 style="margin:0 0 4px 0; white-space:nowrap; overflow:hidden; text-overflow:ellipsis;">
            {{ c.enrollment_name }}
          </h3>
          <div style="font-size:14px; opacity:.7">
            Status: {{ c.status }} • Today: <b>{{ c.today_checked ? "Done" : "Not yet" }}</b>
          </div>
        </div>

        <a
          :href="base + 'enrollment/' + c.enrollment_id"
          style="margin-right:10px; text-decoration:none"
        >
          Open →
        </a>


        <button
          :disabled="c.today_checked || checkingId === c.enrollment_id"
          @click="checkin(c.enrollment_id)"
          style="padding:10px 16px; border-radius:10px; border:none; cursor:pointer"
        >
          <span v-if="c.today_checked">✅ Done</span>
          <span v-else-if="checkingId === c.enrollment_id">...</span>
          <span v-else>Check-in</span>
        </button>
      </div>

      <div v-if="error" style="margin-top:18px; color:#b00020">
        {{ error }}
      </div>
    </div>
  </div>
</template>

<script setup>

import { ref, onMounted } from "vue";
import api from "../lib/api";

const base = import.meta.env.BASE_URL;

const loading = ref(true);
const loggingOut = ref(false);
const checkingId = ref(null);
const error = ref("");

const user = ref(null);
const date = ref("");
const challenges = ref([]);

async function loadDashboard() {
  error.value = "";
  loading.value = true;
  try {
    const { data } = await api.get("/me/dashboard");
    user.value = data.user;
    date.value = data.date;
    challenges.value = data.challenges || [];
  } catch (e) {
    // اگر لاگین نیستی یا کوکی مشکل داشت:
    error.value = e?.message || String(e);
  } finally {
    loading.value = false;
  }
}

async function checkin(enrollmentId) {
  try {
    checkingId.value = enrollmentId;
    await api.post(`/me/challenges/${enrollmentId}/checkin`);
    await loadDashboard();
  } finally {
    checkingId.value = null;
  }
}

async function doLogout() {
  try {
    loggingOut.value = true;
    await api.post("/logout");

    // ✅ مهم: با BASE_URL سازگار (ringostrike)
    window.location.href = `${import.meta.env.BASE_URL}login`;
  } finally {
    loggingOut.value = false;
  }
}

onMounted(loadDashboard);
</script>
