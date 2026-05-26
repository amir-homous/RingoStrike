<template>
  <AppContainer>
    <AppHeader />

    <div class="stack-16">
      <!-- Header -->
      <div class="pageHead">
        <div class="stack-8">
          <h1 class="h1">Dashboard</h1>
          <p v-if="user" class="caption">
            Welcome, <b>{{ user.name }}</b> — {{ date }}
          </p>
        </div>

        <div class="headActions">
          <RouterLink class="ghostLink" to="/challenges">Browse Challenges</RouterLink>

          <BaseButton
            variant="secondary"
            :loading="loggingOut"
            @click="doLogout"
          >
            Logout
          </BaseButton>
        </div>
      </div>

      <BaseCard>
        <UiState
          :loading="loading"
          :error="!!error"
          :empty="!loading && !error && challenges.length === 0"
          loading-title="Loading dashboard…"
          loading-text="Fetching your active challenges."
          empty-title="No active challenges yet"
          empty-text="Join a challenge to start checking in daily."
          error-title="Couldn’t load dashboard"
          :error-text="error || 'Please try again.'"
          @retry="loadDashboard"
        >
          <template #action>
            <RouterLink class="ctaLink" to="/challenges">
              <span aria-hidden="true">🧩</span>
              Browse challenges
              <span aria-hidden="true">→</span>
            </RouterLink>
          </template>
        </UiState>

        <!-- List -->
        <div v-if="!loading && !error && challenges.length" class="list">
          <BaseCard
            v-for="c in challenges"
            :key="c.enrollment_id"
            class="itemCard"
            :padded="true"
          >
            <div class="row">
              <div class="left">
                <div class="titleRow">
                  <h2 class="h2 title">
                    {{ c.enrollment_name }}
                  </h2>

                  <div class="badges">
                    <span class="badge">
                      <span aria-hidden="true">{{ c.status === "Active" ? "🟢" : "⚪️" }}</span>
                      {{ c.status || "—" }}
                    </span>

                    <span class="badge" :class="c.today_checked ? 'b-ok' : 'b-wait'">
                      <span aria-hidden="true">{{ c.today_checked ? "✅" : "⏳" }}</span>
                      Today: <b>{{ c.today_checked ? "Done" : "Not yet" }}</b>
                    </span>
                  </div>
                </div>
              </div>

              <div class="right">
                <RouterLink class="openLink" :to="`/enrollment/${c.enrollment_id}`">
                  Open →
                </RouterLink>

                <BaseButton
                  variant="primary"
                  :loading="checkingId === c.enrollment_id"
                  :disabled="c.today_checked"
                  @click="checkin(c.enrollment_id)"
                >
                  <span v-if="c.today_checked">✅ Done</span>
                  <span v-else>Check-in</span>
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
import { ref, onMounted } from "vue";
import { useRouter } from "vue-router";
import api from "../lib/api";

import AppContainer from "@/components/ui/AppContainer.vue";
import AppHeader from "@/components/ui/AppHeader.vue";
import BaseCard from "@/components/ui/BaseCard.vue";
import BaseButton from "@/components/ui/BaseButton.vue";
import UiState from "@/components/ui/UiState.vue";

const router = useRouter();

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
    // گرفتن لیست چالش‌ها و استت‌های کاربر در یک درخواست (بهینه)
    const { data } = await api.get("/me/challenges");
    
    // مقداردهی استت‌های کاربر از پاسخ جدید
    if (data.user) {
       user.value = {
         ...data.user,
         // اگر در جای دیگر از کد نیاز به اطلاعات پایه داری، اینجا ست کن
       };
    }

    // اصلاح اینجا: در بک‌اِند اسمش challenges است نه items
    challenges.value = data.challenges || [];
    
    date.value = data.date || new Date().toLocaleDateString();
  } catch (e) {
    console.error(e);
    error.value = e?.response?.data?.error || e?.message || String(e);
  } finally {
    loading.value = false;
  }
}


async function checkin(enrollmentId) {
  try {
    checkingId.value = enrollmentId;
    await api.post(`/me/challenges/${enrollmentId}/checkin`);
    await loadDashboard();
  } catch (e) {
    error.value = e?.response?.data?.error || e?.message || String(e);
  } finally {
    checkingId.value = null;
  }
}

async function doLogout() {
  try {
    loggingOut.value = true;
    await api.post("/auth/logout");

    // ✅ SPA navigate
    router.push("/login");
  } finally {
    loggingOut.value = false;
  }
}

onMounted(loadDashboard);
</script>

<style scoped>
.pageHead{
  display:flex;
  justify-content: space-between;
  align-items: flex-end;
  gap: var(--s-16);
  flex-wrap: wrap;
}

.headActions{
  display:flex;
  gap: var(--s-12);
  align-items: center;
  flex-wrap: wrap;
}

.ghostLink{
  color: rgba(255,255,255,0.86);
  text-decoration: none;
  padding: 8px 10px;
  border-radius: 10px;
  border: 1px solid rgba(255,255,255,0.10);
  background: rgba(255,255,255,0.03);
}
.ghostLink:hover{ background: rgba(255,255,255,0.06); }

.ctaLink{
  display:inline-flex;
  align-items:center;
  gap: var(--s-8);
  padding: 8px 10px;
  border-radius: 10px;
  border: 1px solid rgba(99,102,241,0.28);
  background: rgba(99,102,241,0.14);
  color: rgba(255,255,255,0.92);
  text-decoration: none;
  font-weight: 650;
}
.ctaLink:hover{ background: rgba(99,102,241,0.20); }

.list{
  margin-top: var(--s-16);
  display: grid;
  gap: var(--s-12);
}

.itemCard{
  background: rgba(255,255,255,0.02);
  border: 1px solid rgba(255,255,255,0.08);
  box-shadow: none;
}

.row{
  display:flex;
  justify-content: space-between;
  align-items: center;
  gap: var(--s-16);
  flex-wrap: wrap;
}

.left{ min-width: 0; flex: 1; }

.titleRow{
  display:flex;
  flex-direction: column;
  gap: var(--s-8);
}

.title{
  margin: 0;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.badges{
  display:flex;
  gap: var(--s-8);
  flex-wrap: wrap;
  align-items:center;
}

.badge{
  font-size: var(--cap);
  color: rgba(255,255,255,0.86);
  padding: 6px 10px;
  border-radius: 999px;
  border: 1px solid rgba(255,255,255,0.10);
  background: rgba(255,255,255,0.03);
  display:inline-flex;
  gap: 6px;
  align-items:center;
}

.b-ok{
  border-color: rgba(34,197,94,0.28);
  background: rgba(34,197,94,0.10);
}
.b-wait{
  border-color: rgba(245,158,11,0.28);
  background: rgba(245,158,11,0.10);
}

.right{
  display:flex;
  gap: var(--s-12);
  align-items:center;
  flex-wrap: wrap;
}

.openLink{
  color: rgba(255,255,255,0.86);
  text-decoration: none;
  padding: 8px 10px;
  border-radius: 10px;
  border: 1px solid rgba(255,255,255,0.10);
  background: rgba(255,255,255,0.03);
}
.openLink:hover{ background: rgba(255,255,255,0.06); }
</style>
