<template>
  <AppContainer>
    <AppHeader />

    <div class="stack-16">
      <BaseCard>
        <div class="stack-12">
          <div class="titleRow">
            <div class="titleWithIcon">
              <span class="icon" aria-hidden="true">🔐</span>
              <h1 class="h1">Login</h1>
            </div>

            <div class="pill">
              <span aria-hidden="true">📲</span>
              Telegram
            </div>
          </div>

          <p class="caption">
            برای لاگین از طریق تلگرام، دکمه زیر رو بزن. بعد از تایید، به اپ برمی‌گردی.
          </p>

          <div class="callout">
            <div class="cIcon" aria-hidden="true">🛡️</div>
            <div class="stack-4">
              <div class="ctitle">Tip</div>
              <div class="caption">
                اگر بعد از برگشتن لاگین نشدی، یک بار صفحه رو Refresh کن.
              </div>
            </div>
          </div>

          <div class="hr" />

          <div class="steps">
            <div class="step">
              <div class="dot">1</div>
              <div>
                <div class="stitle">Open Telegram Login</div>
                <div class="caption">یک تب جدید باز میشه و داخل تلگرام تایید می‌کنی.</div>
              </div>
            </div>

            <div class="step">
              <div class="dot">2</div>
              <div>
                <div class="stitle">Return to the app</div>
                <div class="caption">بعد از تایید، برگرد همینجا و ادامه بده.</div>
              </div>
            </div>
          </div>

          <div class="actions">
            <a :href="loginUrl" target="_blank" rel="noreferrer" class="linkReset">
              <BaseButton variant="primary">
                <span aria-hidden="true">🚀</span>
                Open Telegram Login
              </BaseButton>
            </a>

            <RouterLink :to="nextPath" class="linkReset">
              <BaseButton variant="secondary">
                <span aria-hidden="true">➡️</span>
                Continue
              </BaseButton>
            </RouterLink>
          </div>

          <details class="details">
            <summary class="caption">Advanced</summary>
            <div class="meta">
              <div class="caption">Next route:</div>
              <code class="code">{{ nextPath }}</code>
            </div>
          </details>
        </div>
      </BaseCard>
    </div>
  </AppContainer>
</template>

<script setup>
import { computed } from "vue";
import { useRoute } from "vue-router";

import AppContainer from "@/components/ui/AppContainer.vue";
import AppHeader from "@/components/ui/AppHeader.vue";
import BaseCard from "@/components/ui/BaseCard.vue";
import BaseButton from "@/components/ui/BaseButton.vue";

const route = useRoute();

const backendBaseRaw = import.meta.env.VITE_API_BASE || "http://localhost:5005";
const backendBase = String(backendBaseRaw).replace(/\/+$/, "");

const next = route.query.next || "/dashboard";
const nextPath = computed(() => (typeof next === "string" ? next : "/dashboard"));

const loginUrl = computed(() => {
  return `${backendBase}/login?next=${encodeURIComponent(nextPath.value)}`;
});
</script>

<style scoped>
.titleRow{
  display:flex;
  justify-content: space-between;
  align-items: center;
  gap: var(--s-12);
  flex-wrap: wrap;
}

.titleWithIcon{
  display:flex;
  align-items:center;
  gap: var(--s-10);
}

.icon{
  width: 34px;
  height: 34px;
  display:grid;
  place-items:center;
  border-radius: 12px;
  background: rgba(255,255,255,0.05);
  border: 1px solid rgba(255,255,255,0.10);
}

.pill{
  display:inline-flex;
  align-items:center;
  gap: 6px;
  padding: 6px 10px;
  border-radius: 999px;
  border: 1px solid rgba(255,255,255,0.10);
  background: rgba(255,255,255,0.03);
  color: rgba(255,255,255,0.88);
  font-size: var(--cap);
  font-weight: 650;
}

.callout{
  display:flex;
  gap: var(--s-12);
  align-items:flex-start;
  padding: var(--s-12);
  border-radius: var(--r-12);
  border: 1px solid rgba(245,158,11,0.28);
  background: rgba(245,158,11,0.10);
}

.cIcon{
  width: 30px;
  height: 30px;
  display:grid;
  place-items:center;
  border-radius: 12px;
  background: rgba(245,158,11,0.16);
  border: 1px solid rgba(245,158,11,0.30);
}

.ctitle{
  font-weight: 750;
}

.actions{
  display:flex;
  gap: var(--s-12);
  flex-wrap: wrap;
}

.steps{
  display:grid;
  gap: var(--s-12);
}

.step{
  display:grid;
  grid-template-columns: 28px 1fr;
  gap: var(--s-12);
  align-items:start;
  padding: var(--s-12);
  border-radius: var(--r-12);
  border: 1px solid rgba(255,255,255,0.08);
  background: rgba(255,255,255,0.03);
}

.dot{
  width: 28px;
  height: 28px;
  border-radius: 999px;
  display:grid;
  place-items:center;
  font-weight: 800;
  background: rgba(99,102,241,0.18);
  border: 1px solid rgba(99,102,241,0.35);
}

.stitle{ font-weight: 750; }

.details{
  margin-top: var(--s-4);
  padding-top: var(--s-8);
}

.meta{
  margin-top: var(--s-8);
  display:flex;
  align-items:center;
  gap: var(--s-8);
  flex-wrap: wrap;
}

.code{
  font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace;
  font-size: 12px;
  padding: 4px 8px;
  border-radius: 10px;
  border: 1px solid rgba(255,255,255,0.10);
  background: rgba(255,255,255,0.05);
}

.linkReset{
  text-decoration: none !important;
}
</style>
