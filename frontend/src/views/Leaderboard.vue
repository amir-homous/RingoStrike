<script setup>
import { ref, onMounted } from "vue";
import { useRoute } from "vue-router";
import api from "../lib/api";

const route = useRoute();
const enrollmentId = route.params.id;

const overall = ref([]);
const today = ref([]);
const loading = ref(true);

const props = defineProps({
    enrollmentId: {
        type: String,
        required: false
    }
});

const id = props.enrollmentId || route.params.id;

onMounted(async () => {
    try {
        const res = await api.get(`/me/enrollments/${id}/leaderboard`);

        overall.value = res.data.overall || [];
        today.value = res.data.today || [];
    } catch (err) {
        console.error("Leaderboard error:", err);
    } finally {
        loading.value = false;
    }
});
</script>

<template>
    <div class="leaderboard">
        <h2>Leaderboard</h2>

        <div v-if="loading">Loading...</div>

        <table v-else>
            <thead>
                <tr>
                    <th>#</th>
                    <th>User</th>
                    <th>Total Check-ins</th>
                </tr>
            </thead>
            <tbody>
                <tr v-for="(row, index) in overall" :key="row.enrollment_id">
                    <td>{{ index + 1 }}</td>
                    <td>{{ row.name }}</td>
                    <td>{{ row.total_checkins }}</td>
                </tr>
            </tbody>
        </table>
    </div>
</template>