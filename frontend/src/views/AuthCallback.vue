<template>
  <div style="padding:24px;font-family:sans-serif">
    <h2>Signing you in...</h2>
    <p v-if="error" style="color:red">{{ error }}</p>
  </div>
</template>

<script setup>
import { onMounted, ref } from "vue";
import { useRouter } from "vue-router";

const router = useRouter();
const error = ref("");

onMounted(() => {
  const hash = window.location.hash.startsWith("#") ? window.location.hash.slice(1) : "";
  const params = new URLSearchParams(hash || window.location.search.slice(1));

  const token = params.get("token");
  const next = params.get("next");
  const nextPath = next && next.startsWith("/") ? next : "/dashboard";

  if (!token) {
    error.value = "Missing token";
    return;
  }

  try {
    localStorage.setItem("ringo_token", token);
  } catch {
    error.value = "Could not store auth token";
    return;
  }

  router.replace(nextPath);
});
</script>
