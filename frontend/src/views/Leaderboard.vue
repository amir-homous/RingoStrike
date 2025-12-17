<script setup>
import { ref, onMounted, computed } from "vue";
import { useRoute } from "vue-router";
import api from "../lib/api";

import AppContainer from "@/components/ui/AppContainer.vue";
import AppHeader from "@/components/ui/AppHeader.vue";
import BaseCard from "@/components/ui/BaseCard.vue";
import UiState from "@/components/ui/UiState.vue";

const route = useRoute();

const props = defineProps({
    enrollmentId: { type: String, required: false },
    embedded: { type: Boolean, default: false },   // ✅ جدید
});

const id = computed(() => {
    const pid = props.enrollmentId;
    if (pid) return pid;
    const rid = route.params.id;
    return typeof rid === "string" ? rid : "";
});

const overall = ref([]);
const today = ref([]); // فعلاً نگه می‌داریم برای آینده (Total + Streak/Today)
const loading = ref(true);
const error = ref("");
const errorText = computed(() => {
    if (error.value === "missing_id") return "Invalid leaderboard link (missing enrollment id).";
    return "Try again. If it keeps happening, the API might be down.";
});

async function fetchLeaderboard() {
    loading.value = true;
    error.value = "";

    if (!id.value) {
        error.value = "missing_id";
        loading.value = false;
        return;
    }

    try {
        const res = await api.get(`/me/enrollments/${id.value}/leaderboard`);
        overall.value = res.data?.overall || [];
        today.value = res.data?.today || [];
    } catch (err) {
        console.error("Leaderboard error:", err);
        error.value = "failed";
    } finally {
        loading.value = false;
    }
}


const isEmpty = computed(() => !loading.value && !error.value && overall.value.length === 0);

onMounted(fetchLeaderboard);
</script>

<template>
    <!-- حالت embedded: فقط خود محتوا -->
    <div v-if="embedded" class="stack-16">
        <BaseCard>
            <UiState :loading="loading" :error="!!error" :empty="isEmpty" loading-title="Loading leaderboard…"
                loading-text="Getting the latest rankings." empty-title="No leaderboard data yet"
                empty-text="Once people check in, rankings will show here." error-title="Couldn’t load leaderboard"
                :error-text="errorText" @retry="fetchLeaderboard" />

            <div v-if="!loading && !error && overall.length" class="tableWrap">
                <table class="table">
                    <thead>
                        <tr>
                            <th class="col-rank">#</th>
                            <th>User</th>
                            <th class="col-num">✅ Total</th>
                            <th class="col-num">🔥 Streak</th>
                        </tr>
                    </thead>

                    <tbody>
                        <tr v-for="(row, index) in overall" :key="row.enrollment_id || index">
                            <td class="rank">{{ index + 1 }}</td>
                            <td class="user">
                                <div class="uname">{{ row.name || "Unknown" }}</div>
                                <div class="caption" v-if="row.username">@{{ row.username }}</div>
                            </td>
                            <td class="num">{{ row.total_checkins ?? 0 }}</td>
                            <td class="num">{{ row.current_streak ?? 0 }}</td>
                        </tr>
                    </tbody>
                </table>
            </div>
        </BaseCard>
    </div>

    <!-- حالت page: صفحه کامل -->
    <AppContainer v-else>
        <AppHeader />

        <div class="stack-16">
            <div class="head">
                <div class="titleWithIcon">
                    <span class="icon" aria-hidden="true">🏆</span>
                    <div>
                        <h1 class="h1">Leaderboard</h1>
                        <div class="caption">Total + Streak (milestone 0.1)</div>
                    </div>
                </div>
            </div>

            <BaseCard>
                <UiState :loading="loading" :error="!!error" :empty="isEmpty" loading-title="Loading leaderboard…"
                    loading-text="Getting the latest rankings." empty-title="No leaderboard data yet"
                    empty-text="Once people check in, rankings will show here." error-title="Couldn’t load leaderboard"
                    :error-text="errorText" @retry="fetchLeaderboard" />

                <div v-if="!loading && !error && overall.length" class="tableWrap">
                    <table class="table">
                        <thead>
                            <tr>
                                <th class="col-rank">#</th>
                                <th>User</th>
                                <th class="col-num">✅ Total</th>
                                <th class="col-num">🔥 Streak</th>
                            </tr>
                        </thead>

                        <tbody>
                            <tr v-for="(row, index) in overall" :key="row.enrollment_id || index">
                                <td class="rank">{{ index + 1 }}</td>
                                <td class="user">
                                    <div class="uname">{{ row.name || "Unknown" }}</div>
                                    <div class="caption" v-if="row.username">@{{ row.username }}</div>
                                </td>
                                <td class="num">{{ row.total_checkins ?? 0 }}</td>
                                <td class="num">{{ row.current_streak ?? 0 }}</td>
                            </tr>
                        </tbody>
                    </table>
                </div>
            </BaseCard>
        </div>
    </AppContainer>
</template>


<style scoped>
.head {
    display: flex;
    align-items: flex-end;
    justify-content: space-between;
    gap: var(--s-16);
}

.tableWrap {
    margin-top: var(--s-16);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: var(--r-12);
    overflow: hidden;
    background: rgba(255, 255, 255, 0.02);
}

/* موبایل: جدول می‌تونه اسکرول افقی داشته باشه */
.tableWrap {
    overflow-x: auto;
}

.table {
    width: 100%;
    border-collapse: collapse;
    min-width: 520px;
    /* کمک به ریسپانسیو: موبایل اسکرول می‌گیره ولی نمی‌شکنه */
}

thead th {
    text-align: left;
    font-size: var(--cap);
    color: var(--muted2);
    font-weight: 700;
    padding: 12px 14px;
    background: rgba(255, 255, 255, 0.03);
    border-bottom: 1px solid rgba(255, 255, 255, 0.08);
}

tbody td {
    padding: 12px 14px;
    border-bottom: 1px solid rgba(255, 255, 255, 0.06);
}

tbody tr:hover {
    background: rgba(255, 255, 255, 0.03);
}

.col-rank {
    width: 52px;
}

.col-num {
    width: 110px;
    text-align: right;
}

.rank {
    color: rgba(255, 255, 255, 0.85);
    font-weight: 700;
}

.user {
    max-width: 420px;
}

.uname {
    font-weight: 650;
}

.num {
    text-align: right;
    font-variant-numeric: tabular-nums;
}

.titleWithIcon {
    display: flex;
    align-items: center;
    gap: var(--s-12);
}

.icon {
    width: 34px;
    height: 34px;
    display: grid;
    place-items: center;
    border-radius: 12px;
    background: rgba(255, 255, 255, 0.05);
    border: 1px solid rgba(255, 255, 255, 0.10);
}
</style>