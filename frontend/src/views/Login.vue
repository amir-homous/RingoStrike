<template>
  <div style="padding: 24px; font-family: sans-serif;">
    <h2>Login</h2>

    <p>برای لاگین، این لینک رو بزن:</p>

    <a :href="loginUrl" target="_blank" rel="noreferrer">
      Open Telegram Login
    </a>

    <p style="margin-top: 16px; opacity: 0.8;">
      بعد از تایید در تلگرام، خودکار به همین سایت برمی‌گردی.
    </p>
  </div>
</template>

<script setup>
import { computed } from "vue";
import { useRoute } from "vue-router";

const route = useRoute();

const backendBaseRaw =
  import.meta.env.VITE_API_BASE || "http://localhost:5005";

const backendBase = String(backendBaseRaw).replace(/\/+$/, ""); // remove trailing /

const next = route.query.next || "/dashboard";

const loginUrl = computed(
  () => `${backendBase}/login?next=${encodeURIComponent(next)}`
);
</script>
