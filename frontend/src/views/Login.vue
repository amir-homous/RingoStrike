<template>
  <AppContainer>
    <div class="stack-16">
      <BaseCard>
        <div class="stack-12">
          <h1 class="h1">Login</h1>

          <p class="caption">
            برای لاگین از طریق تلگرام، دکمه زیر رو بزن. بعد از تایید، به سایت برمی‌گردی.
          </p>

          <div class="hr" />

          <div class="steps">
            <div class="step">
              <div class="dot">1</div>
              <div>
                <div class="stitle">Open Telegram Login</div>
                <div class="caption">
                  یک تب جدید باز میشه و داخل تلگرام تایید می‌کنی.
                </div>
              </div>
            </div>

            <div class="step">
              <div class="dot">2</div>
              <div>
                <div class="stitle">Return to the app</div>
                <div class="caption">
                  بعد از تایید، خودکار به همین سایت برمی‌گردی.
                </div>
              </div>
            </div>
          </div>

          <div class="actions">
            <!-- لینک تبدیل به دکمه استاندارد -->
            <a :href="loginUrl" target="_blank" rel="noreferrer" class="linkReset">
              <BaseButton variant="primary">
                Open Telegram Login
              </BaseButton>
            </a>

            <RouterLink :to="nextPath" class="linkReset">
              <BaseButton variant="secondary">
                Continue (if already logged in)
              </BaseButton>
            </RouterLink>
          </div>

          <div class="meta">
            <div class="caption">Next:</div>
            <code class="code">{{ nextPath }}</code>
          </div>
        </div>
      </BaseCard>
    </div>
  </AppContainer>
</template>

<script setup>
import { computed } from "vue";
import { useRoute } from "vue-router";

import AppContainer from "@/components/ui/AppContainer.vue";
import BaseCard from "@/components/ui/BaseCard.vue";
import BaseButton from "@/components/ui/BaseButton.vue";

const route = useRoute();

const backendBaseRaw = import.meta.env.VITE_API_BASE || "http://localhost:5005";
const backendBase = String(backendBaseRaw).replace(/\/+$/, ""); // remove trailing /

const next = route.query.next || "/dashboard";
const nextPath = computed(() => (typeof next === "string" ? next : "/dashboard"));

const loginUrl = computed(
  () => `${backendBase}/login?next=${encodeURIComponent(nextPath.value)}`
);
</script>

<style scoped>
.actions{
  display: flex;
  gap: var(--s-12);
  flex-wrap: wrap;
}

/* کارت مرحله‌ها */
.steps{
  display: grid;
  gap: var(--s-12);
}

.step{
  display: grid;
  grid-template-columns: 28px 1fr;
  gap: var(--s-12);
  align-items: start;
  padding: var(--s-12);
  border-radius: var(--r-12);
  border: 1px solid rgba(255,255,255,0.08);
  background: rgba(255,255,255,0.03);
}

.dot{
  width: 28px;
  height: 28px;
  border-radius: 999px;
  display: grid;
  place-items: center;
  font-weight: 800;
  background: rgba(99,102,241,0.18);
  border: 1px solid rgba(99,102,241,0.35);
}

.stitle{
  font-weight: 750;
}

.meta{
  display: flex;
  align-items: center;
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

/* برای اینکه a/RouterLink استایل خودشون رو به Button خراب نکنن */
.linkReset{
  text-decoration: none !important;
}
</style>
