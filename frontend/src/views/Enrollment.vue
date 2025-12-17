<template>
	<AppContainer>
		<AppHeader />

		<div class="stack-16">
			<!-- Header -->
			<div class="pageHead">
				<div class="stack-8">
					<h1 class="h1">Challenge</h1>

					<div v-if="challenge" class="sub">
						<b>{{ challenge.name }}</b>
						<span v-if="challenge.duration_days"> • {{ challenge.duration_days }} days</span>
					</div>

					<div v-if="enrollment" class="meta">
						Enrollment: {{ enrollment.name }} • Status: <b>{{ enrollment.status }}</b>
					</div>
				</div>

			</div>

			<!-- State wrapper -->
			<BaseCard>
				<UiState :loading="loading" :error="!!error" :empty="!loading && !error && !enrollment"
					loading-title="Loading enrollment…" loading-text="Fetching challenge and your progress."
					empty-title="Enrollment not found"
					empty-text="This enrollment might be invalid or you don’t have access."
					error-title="Couldn’t load enrollment" :error-text="error || 'Please try again.'" @retry="load" />

				<div v-if="!loading && !error && enrollment" class="stack-16">
					<!-- Today Check-in -->
					<BaseCard class="innerCard" :padded="true">
						<div class="row">
							<div class="stack-8">
								<div class="line">
									<span class="label">Today:</span>
									<span class="value">
										<b>{{ enrollment.today_checked ? "Done ✅" : "Not yet" }}</b>
									</span>
								</div>

								<div v-if="challenge?.description" class="desc">
									{{ challenge.description }}
								</div>
							</div>

							<BaseButton variant="primary" :loading="checking" :disabled="enrollment.today_checked"
								@click="checkin">
								<span v-if="enrollment.today_checked">✅ Done</span>
								<span v-else>Check-in</span>
							</BaseButton>
						</div>
					</BaseCard>

					<!-- Progress -->
					<BaseCard class="innerCard" :padded="true">
						<div class="stack-12">
							<div class="progressHead">
								<h2 class="h2">Your Progress</h2>
								<div class="pct"><b>{{ percent }}%</b></div>
							</div>

							<div class="progressMeta">
								<span>{{ checkedDays }} / {{ totalDays }} days</span>
								<span class="caption">{{ progressText }}</span>
							</div>

							<div class="bar">
								<div class="barFill" :style="{ width: percent + '%', background: barColor }" />
							</div>

							<div class="stats">
								<div class="stat">
									<div class="caption"><span aria-hidden="true">✅</span> Total Check-ins</div>
									<div class="statVal">{{ totalCheckins }}</div>
								</div>

								<div class="stat">
									<div class="caption"><span aria-hidden="true">🔥</span> Current Streak</div>
									<div class="statVal">{{ currentStreak }}</div>
								</div>
							</div>
						</div>
					</BaseCard>

					<!-- Embedded leaderboard preview -->
					<div class="stack-12">
						<div class="sectionHead">
							<div class="titleWithIcon">
								<span class="icon" aria-hidden="true">🏆</span>
								<h2 class="h2">Leaderboard</h2>
							</div>

							<RouterLink class="ctaLink" :to="`/enrollment/${enrollment.enrollment_id}/leaderboard`">
								<span class="ctaIcon" aria-hidden="true">📊</span>
								View full
								<span class="arrow" aria-hidden="true">→</span>
							</RouterLink>
						</div>

						<Leaderboard :enrollment-id="enrollment.enrollment_id" embedded />
					</div>

					<!-- Recent logs -->
					<div class="stack-12">
						<h2 class="h2">Recent logs</h2>

						<div v-if="recentLogs.length === 0" class="caption">
							No logs yet.
						</div>

						<BaseCard class="innerCard" :padded="true">
							<div class="sectionHead">
								<div class="titleWithIcon">
									<span class="icon" aria-hidden="true">🗓️</span>
									<h2 class="h2">Recent logs</h2>
								</div>
							</div>

							<div v-if="recentLogs.length === 0" class="caption">
								No logs yet.
							</div>

							<ul v-else class="logList">
								<li v-for="l in recentLogs" :key="l.daily_log_id" class="logRow">
									<span class="logDot" aria-hidden="true">✅</span>
									<span class="logDate"> {{ l.date || "—" }}</span>
								</li>
							</ul>
						</BaseCard>
					</div>
				</div>
			</BaseCard>
		</div>
	</AppContainer>
</template>

<script setup>
import Leaderboard from "./Leaderboard.vue";

import { onMounted, ref, computed } from "vue";
import { useRoute } from "vue-router";
import api from "../lib/api";

import AppContainer from "@/components/ui/AppContainer.vue";
import AppHeader from "@/components/ui/AppHeader.vue";
import BaseCard from "@/components/ui/BaseCard.vue";
import BaseButton from "@/components/ui/BaseButton.vue";
import UiState from "@/components/ui/UiState.vue";

const route = useRoute();

const loading = ref(true);
const checking = ref(false);
const error = ref("");

const enrollment = ref(null);
const challenge = ref(null);
const recentLogs = ref([]);

// progress state
const checkedDays = ref(0);
const totalDays = ref(0);

const percent = computed(() => {
	if (!totalDays.value) return 0;
	return Math.min(100, Math.round((checkedDays.value / totalDays.value) * 100));
});

const barColor = computed(() => {
	// بدون طراحی سنگین، فقط readable
	if (percent.value >= 70) return "rgba(34,197,94,0.9)";
	if (percent.value >= 35) return "rgba(245,158,11,0.9)";
	return "rgba(239,68,68,0.9)";
});

const totalCheckins = computed(() => {
	const t = enrollment.value?.total_checkins ?? enrollment.value?.totalCheckins ?? null;
	if (t != null) return t;
	return checkedDays.value;
});

const currentStreak = computed(() => {
	const s = enrollment.value?.current_streak ?? enrollment.value?.currentStreak ?? null;
	if (s != null) return s;
	return "—";
});

const progressText = computed(() => {
	if (!challenge.value?.duration_days) return "Progress is based on your check-ins.";
	return `Keep going — ${Math.max(0, challenge.value.duration_days - checkedDays.value)} days left.`;
});

async function load() {
	loading.value = true;
	error.value = "";

	try {
		const id = route.params.id;

		const { data } = await api.get(`/me/enrollments/${id}`);
		enrollment.value = data.enrollment;
		challenge.value = data.challenge;
		recentLogs.value = data.recent_logs || [];

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
		error.value = "";
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

<style scoped>
.pageHead {
	display: flex;
	justify-content: space-between;
	align-items: flex-start;
	gap: var(--s-16);
	flex-wrap: wrap;
}

.sub {
	opacity: 0.85;
}

.meta {
	opacity: 0.7;
	font-size: var(--cap);
}




.topLink:hover {
	background: rgba(255, 255, 255, 0.06);
	color: rgba(255, 255, 255, 0.92);
}

.innerCard {
	background: rgba(255, 255, 255, 0.02);
	border: 1px solid rgba(255, 255, 255, 0.08);
	box-shadow: none;
}

.row {
	display: flex;
	justify-content: space-between;
	align-items: center;
	gap: var(--s-16);
	flex-wrap: wrap;
}

.line {
	display: flex;
	gap: var(--s-8);
	align-items: baseline;
	flex-wrap: wrap;
}

.label {
	color: var(--muted);
}

.value {
	color: rgba(255, 255, 255, 0.92);
}

.desc {
	opacity: 0.85;
}

.progressHead {
	display: flex;
	justify-content: space-between;
	align-items: baseline;
	gap: var(--s-12);
}

.progressMeta {
	display: flex;
	justify-content: space-between;
	align-items: baseline;
	gap: var(--s-12);
	flex-wrap: wrap;
	opacity: 0.85;
}

.pct {
	font-variant-numeric: tabular-nums;
}

.bar {
	height: 12px;
	border-radius: 999px;
	background: rgba(255, 255, 255, 0.08);
	overflow: hidden;
	border: 1px solid rgba(255, 255, 255, 0.08);
}

.barFill {
	height: 100%;
	border-radius: 999px;
	transition: width 180ms ease;
}

.stats {
	display: flex;
	gap: var(--s-12);
	flex-wrap: wrap;
}

.stat {
	min-width: 160px;
	padding: 10px 12px;
	border-radius: var(--r-12);
	border: 1px solid rgba(255, 255, 255, 0.08);
	background: rgba(255, 255, 255, 0.03);
}

.statVal {
	font-size: 18px;
	font-weight: 800;
	margin-top: 2px;
	font-variant-numeric: tabular-nums;
}

.sectionHead {
	display: flex;
	justify-content: space-between;
	align-items: baseline;
	gap: var(--s-12);
	flex-wrap: wrap;
}

.link {
	color: rgba(255, 255, 255, 0.85);
	text-decoration: none;
	border-bottom: 1px dashed rgba(255, 255, 255, 0.35);
}

.link:hover {
	color: rgba(255, 255, 255, 0.95);
	border-bottom-color: rgba(255, 255, 255, 0.6);
}

.logs {
	margin: 0;
	padding-left: 18px;
}

.logItem {
	padding: 6px 0;
	opacity: 0.9;
}

.titleWithIcon {
	display: flex;
	align-items: center;
	gap: var(--s-8);
}

.icon {
	width: 28px;
	height: 28px;
	display: grid;
	place-items: center;
	border-radius: 10px;
	background: rgba(255, 255, 255, 0.05);
	border: 1px solid rgba(255, 255, 255, 0.10);
}

.ctaLink {
	display: inline-flex;
	align-items: center;
	gap: var(--s-8);
	padding: 8px 10px;
	border-radius: 10px;
	border: 1px solid rgba(255, 255, 255, 0.10);
	background: rgba(255, 255, 255, 0.03);
	color: rgba(255, 255, 255, 0.88);
	text-decoration: none;
	font-weight: 650;
}

.ctaLink:hover {
	background: rgba(255, 255, 255, 0.06);
	border-color: rgba(255, 255, 255, 0.18);
}

.ctaIcon {
	width: 22px;
	height: 22px;
	display: grid;
	place-items: center;
	border-radius: 8px;
	background: rgba(99, 102, 241, 0.18);
	border: 1px solid rgba(99, 102, 241, 0.30);
}

.arrow {
	opacity: 0.9;
}

.logList{
  margin: var(--s-12) 0 0 0;
  padding: 0;
  list-style: none;
  display: grid;
  gap: var(--s-8);
}

.logRow{
  display:flex;
  align-items:center;
  gap: var(--s-10);
  padding: 10px 12px;
  border-radius: var(--r-12);
  border: 1px solid rgba(255,255,255,0.08);
  background: rgba(255,255,255,0.03);
}

.logDot{
  width: 26px;
  height: 26px;
  display:grid;
  place-items:center;
  border-radius: 10px;
  background: rgba(34,197,94,0.14);
  border: 1px solid rgba(34,197,94,0.28);
}

.logDate{
  font-weight: 650;
  font-variant-numeric: tabular-nums;
}

</style>