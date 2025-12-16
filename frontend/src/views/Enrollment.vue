<template>
	<div style="padding:32px; max-width:900px; margin:auto">
		<div style="display:flex; justify-content:space-between; align-items:flex-start; gap:16px">
			<div>
				<h1 style="margin:0 0 6px 0">Challenge</h1>
				<div style="opacity:.75" v-if="challenge">
					<b>{{ challenge.name }}</b>
					<span v-if="challenge.duration_days"> • {{ challenge.duration_days }} days</span>
				</div>
				<div style="opacity:.7" v-if="enrollment">
					Enrollment: {{ enrollment.name }} • Status: <b>{{ enrollment.status }}</b>
				</div>
			</div>

			<div style="display:flex; gap:10px">
				<a :href="base + 'dashboard'" style="text-decoration:none">Dashboard</a>
				<a :href="base + 'challenges'" style="text-decoration:none">Challenges</a>
			</div>
		</div>

		<div v-if="loading" style="margin-top:16px">Loading...</div>

		<div v-else style="margin-top:16px">
			<div v-if="error" style="color:#b00020; margin-bottom:14px">
				{{ error }}
			</div>

			<!-- ✅ Today check-in box -->
			<div v-if="enrollment" style="border:1px solid #ddd; border-radius:12px; padding:16px">
				<div style="display:flex; justify-content:space-between; align-items:center; gap:16px">
					<div>
						Today:
						<b>{{ enrollment.today_checked ? "Done ✅" : "Not yet" }}</b>
					</div>

					<button @click="checkin" :disabled="enrollment.today_checked || checking"
						style="padding:10px 16px; border-radius:10px; border:none; cursor:pointer">
						<span v-if="enrollment.today_checked">✅ Done</span>
						<span v-else-if="checking">...</span>
						<span v-else>Check-in</span>
					</button>
				</div>

				<div v-if="challenge?.description" style="margin-top:12px; opacity:.85">
					{{ challenge.description }}
				</div>
			</div>

			<!-- ✅ Personal Progress -->
			<div v-if="enrollment" style="border:1px solid #ddd; border-radius:12px; padding:16px; margin-top:16px">
				<h3 style="margin:0 0 10px 0">Your Progress</h3>

				<div style="display:flex; gap:14px; flex-wrap:wrap; align-items:center">
					<div style="min-width:240px; flex:1">
						<div style="display:flex; justify-content:space-between; font-size:14px; opacity:.8">
							<span>{{ checkedDays }} / {{ totalDays }} days</span>
							<b>{{ percent }}%</b>
						</div>

						<div style="height:12px; border-radius:999px; background:#eee; overflow:hidden; margin-top:8px">
							<div :style="{
								width: percent + '%',
								height: '100%',
								borderRadius: '999px',
								background: percent >= 70 ? '#22c55e' : percent >= 35 ? '#f59e0b' : '#ef4444'
							}"></div>
						</div>

						<div style="margin-top:8px; font-size:13px; opacity:.75">
							{{ progressText }}
						</div>
					</div>

					<div style="display:flex; gap:12px; flex-wrap:wrap">
						<div style="border:1px solid #eee; border-radius:12px; padding:10px 12px; min-width:150px">
							<div style="font-size:12px; opacity:.65">Total Check-ins</div>
							<div style="font-size:18px"><b>{{ totalCheckins }}</b></div>
						</div>

						<div style="border:1px solid #eee; border-radius:12px; padding:10px 12px; min-width:150px">
							<div style="font-size:12px; opacity:.65">Current Streak</div>
							<div style="font-size:18px"><b>{{ currentStreak }}</b></div>
						</div>
					</div>
				</div>
			</div>

			<!-- (Optional) leaderboard stays below if you already added it -->
			<section class="mt-6">

				<Leaderboard :enrollment-id="enrollment.enrollment_id" />

				<router-link :to="`/enrollment/${enrollment.enrollment_id}/leaderboard`">
					View full leaderboard
				</router-link>
			</section>

			<h3 style="margin:18px 0 10px 0">Recent logs</h3>
			<div v-if="recentLogs.length === 0" style="opacity:.7">
				No logs yet.
			</div>
			<ul v-else style="margin:0; padding-left:18px">
				<li v-for="l in recentLogs" :key="l.daily_log_id">
					{{ l.date || "—" }}
				</li>
			</ul>


		</div>
	</div>
</template>

<script setup>
import Leaderboard from "./Leaderboard.vue";

import { onMounted, ref, computed } from "vue";
import { useRoute } from "vue-router";
import api from "../lib/api";

const base = import.meta.env.BASE_URL;
const route = useRoute();

const loading = ref(true);
const checking = ref(false);
const error = ref("");

const enrollment = ref(null);
const challenge = ref(null);
const recentLogs = ref([]);

// ✅ progress state
const checkedDays = ref(0);
const totalDays = ref(0);

const percent = computed(() => {
	if (!totalDays.value) return 0;
	return Math.min(100, Math.round((checkedDays.value / totalDays.value) * 100));
});

const totalCheckins = computed(() => {
	const t = enrollment.value?.total_checkins ?? enrollment.value?.totalCheckins ?? null;
	if (t != null) return t;
	// اگر بک‌اند هنوز اینو نمی‌فرسته، از progress حدس می‌زنیم
	return checkedDays.value;
});

const currentStreak = computed(() => {
	const s = enrollment.value?.current_streak ?? enrollment.value?.currentStreak ?? null;
	if (s != null) return s;
	return "—";
});

const progressText = computed(() => {
	if (!challenge.value?.duration_days) return "Progress is based on your check-ins.";
	return `Keep going — ${challenge.value.duration_days - checkedDays.value} days left.`;
});

async function load() {
	loading.value = true;
	error.value = "";

	try {
		const id = route.params.id;

		// 1) enrollment detail
		const { data } = await api.get(`/me/enrollments/${id}`);
		enrollment.value = data.enrollment;
		challenge.value = data.challenge;
		recentLogs.value = data.recent_logs || [];

		// 2) history summary → برای progress bar دقیق
		const days = challenge.value?.duration_days || 30;
		const hist = await api.get(`/me/challenges/${id}/history?days=${days}`);
		checkedDays.value = hist.data?.summary?.checked_days ?? 0;
		totalDays.value = hist.data?.summary?.total_days ?? days;
	} catch (e) {
		error.value = e?.response?.data?.error || e?.message || String(e);
	} finally {
		loading.value = false;
	}
}

async function checkin() {
	try {
		checking.value = true;
		const id = route.params.id;
		await api.post(`/me/challenges/${id}/checkin`);
		await load();
	} catch (e) {
		error.value = e?.response?.data?.error || e?.message || String(e);
	} finally {
		checking.value = false;
	}
}

onMounted(load);
</script>