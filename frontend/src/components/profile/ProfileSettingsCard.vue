<script setup>
import { ref, onMounted } from "vue";
import { useI18n } from "vue-i18n";

import api from "@/lib/api";

import BaseCard from "@/components/ui/BaseCard.vue";
import {
  createTelegramConnectCode,
  disconnectTelegram,
  loadProfileSettings,
  loadTelegramSettings,
  saveProfileSettings,
  saveTelegramSettings,
} from "@/views/profileFlow";

const loading = ref(false);
const saved = ref(false);
const error = ref("");
const telegramLoading = ref(false);
const telegramSaving = ref(false);
const telegramSaved = ref(false);
const telegramError = ref("");
const connectCode = ref(null);
const { t } = useI18n();

const form = ref({
  bio: "",
  avatar_url: "",
  profile_visibility: "public",
});

const telegramSettings = ref({
  connected: false,
  telegram_username: "",
  reminders_enabled: false,
  daily_checkin_enabled: true,
  streak_risk_enabled: true,
  weekly_summary_enabled: false,
  bot_username: "",
  bot_link: "",
});

const emit = defineEmits([
  "close",
  "saved",
]);

const avatars = [
  "/avatars/avatar-1.png",
  "/avatars/avatar-2.png",
  "/avatars/avatar-3.png",
  "/avatars/avatar-4.png",
  "/avatars/avatar-5.png",
  "/avatars/avatar-6.png",
  "/avatars/avatar-7.png",
  "/avatars/avatar-8.png",
  "/avatars/avatar-9.png",
  "/avatars/avatar-10.png",
  "/avatars/avatar-11.png",
  "/avatars/avatar-12.png",
  "/avatars/avatar-13.png",
  "/avatars/avatar-14.png",
  "/avatars/avatar-15.png",
  "/avatars/avatar-16.png",



];


async function loadProfile() {
  error.value = "";

  try {
    form.value = await loadProfileSettings(api);
  } catch (err) {
    error.value = err.response?.data?.error || t("profileComponents.loadError");
  }
}

async function saveProfile() {
  loading.value = true;
  saved.value = false;
  error.value = "";

  try {
    await saveProfileSettings(api, form.value);

    saved.value = true;
    emit("saved");

    setTimeout(() => {
      saved.value = false;
    }, 2000);

  } catch (err) {
    error.value = err.response?.data?.error || t("profileComponents.saveError");
  } finally {
    loading.value = false;
  }
}

async function loadTelegram() {
  telegramLoading.value = true;
  telegramError.value = "";

  try {
    const settings = await loadTelegramSettings(api);

    if (settings) {
      telegramSettings.value = {
        ...telegramSettings.value,
        ...settings,
      };
    }
  } catch (err) {
    telegramError.value = err.response?.data?.error || t("profileComponents.telegramLoadError");
  } finally {
    telegramLoading.value = false;
  }
}

async function generateConnectCode() {
  telegramSaving.value = true;
  telegramError.value = "";
  connectCode.value = null;

  try {
    connectCode.value = await createTelegramConnectCode(api);
  } catch (err) {
    telegramError.value = err.response?.data?.error || t("profileComponents.telegramConnectError");
  } finally {
    telegramSaving.value = false;
  }
}

async function saveTelegram() {
  telegramSaving.value = true;
  telegramSaved.value = false;
  telegramError.value = "";

  try {
    const settings = await saveTelegramSettings(api, telegramSettings.value);

    if (settings) {
      telegramSettings.value = {
        ...telegramSettings.value,
        ...settings,
      };
    }

    telegramSaved.value = true;

    setTimeout(() => {
      telegramSaved.value = false;
    }, 2000);
  } catch (err) {
    telegramError.value = err.response?.data?.error || t("profileComponents.telegramSaveError");
  } finally {
    telegramSaving.value = false;
  }
}

async function disconnectTelegramAccount() {
  telegramSaving.value = true;
  telegramError.value = "";
  connectCode.value = null;

  try {
    const settings = await disconnectTelegram(api);

    if (settings) {
      telegramSettings.value = {
        ...telegramSettings.value,
        ...settings,
      };
    }
  } catch (err) {
    telegramError.value = err.response?.data?.error || t("profileComponents.telegramDisconnectError");
  } finally {
    telegramSaving.value = false;
  }
}

onMounted(() => {
  loadProfile();
  loadTelegram();
});
</script>

<template>
  <BaseCard class="settings-card">
    <div class="top">
      <div>
        <h2>{{ t("profileComponents.settingsTitle") }}</h2>

        <p class="caption">
          {{ t("profileComponents.settingsCaption") }}
        </p>
      </div>
    </div>

    <div class="field">
      <label>{{ t("profileComponents.chooseAvatar") }}</label>

      <div class="avatar-grid">
        <img v-for="avatar in avatars" :key="avatar" :src="avatar" class="avatar-option" :class="{
          active:
            form.avatar_url === avatar
        }" @click="
        form.avatar_url = avatar
        " />
      </div>
    </div>

    <div class="field">
      <label>{{ t("profileComponents.bio") }}</label>

      <textarea v-model="form.bio" rows="4" :placeholder="t('profileComponents.bioPlaceholder')" />
    </div>
<br>
    <div class="field">
      <label>{{ t("profileComponents.visibility") }}</label>

      <select v-model="form.profile_visibility">
        <option value="public">
          {{ t("common.public") }}
        </option>

        <option value="private">
          {{ t("common.private") }}
        </option>
      </select>
    </div>

    <div class="telegram-section">
      <div class="telegram-heading">
        <div>
          <h3>{{ t("profileComponents.telegramTitle") }}</h3>

          <p class="caption">
            {{ t("profileComponents.telegramCaption") }}
          </p>
        </div>

        <span
          class="status-pill"
          :class="{ active: telegramSettings.connected }"
        >
          {{
            telegramSettings.connected
              ? t("profileComponents.telegramConnected")
              : t("profileComponents.telegramNotConnected")
          }}
        </span>
      </div>

      <p
        v-if="telegramSettings.connected && telegramSettings.telegram_username"
        class="telegram-meta"
      >
        @{{ telegramSettings.telegram_username }}
      </p>

      <p v-if="telegramLoading" class="telegram-meta">
        {{ t("common.loading") }}
      </p>

      <div class="toggle-list">
        <label class="toggle-row">
          <input
            v-model="telegramSettings.reminders_enabled"
            type="checkbox"
          />
          <span>{{ t("profileComponents.telegramRemindersEnabled") }}</span>
        </label>

        <label class="toggle-row">
          <input
            v-model="telegramSettings.daily_checkin_enabled"
            type="checkbox"
          />
          <span>{{ t("profileComponents.telegramDailyCheckinEnabled") }}</span>
        </label>

        <label class="toggle-row">
          <input
            :checked="false"
            type="checkbox"
            disabled
          />
          <span>
            {{ t("profileComponents.telegramStreakRiskEnabled") }}
            <small>{{ t("profileComponents.telegramComingSoon") }}</small>
          </span>
        </label>

        <label class="toggle-row">
          <input
            :checked="false"
            type="checkbox"
            disabled
          />
          <span>
            {{ t("profileComponents.telegramWeeklySummaryEnabled") }}
            <small>{{ t("profileComponents.telegramComingSoon") }}</small>
          </span>
        </label>
      </div>

      <div v-if="connectCode" class="connect-code">
        <p class="connect-label">
          {{ t("profileComponents.telegramConnectCode") }}
        </p>

        <strong>{{ connectCode.code }}</strong>

        <p class="telegram-meta">
          {{ t("profileComponents.telegramCodeInstruction") }}
        </p>

        <a
          v-if="connectCode.bot_link"
          :href="connectCode.bot_link"
          target="_blank"
          rel="noreferrer"
        >
          {{ t("profileComponents.telegramOpenBot") }}
        </a>
      </div>

      <p v-if="telegramError" class="error-message">
        {{ telegramError }}
      </p>

      <div class="telegram-actions">
        <button
          class="cancel-btn"
          :disabled="telegramSaving"
          @click="generateConnectCode"
        >
          {{ t("profileComponents.telegramGenerateCode") }}
        </button>

        <button
          v-if="telegramSettings.connected"
          class="cancel-btn danger"
          :disabled="telegramSaving"
          @click="disconnectTelegramAccount"
        >
          {{ t("profileComponents.telegramDisconnect") }}
        </button>

        <button
          class="save-btn"
          :disabled="telegramSaving"
          @click="saveTelegram"
        >
          {{
            telegramSaving
              ? t("profileComponents.saving")
              : telegramSaved
              ? t("profileComponents.saved")
              : t("profileComponents.telegramSave")
          }}
        </button>
      </div>
    </div>

    <p v-if="error" class="error-message">
      {{ error }}
    </p>

    <div class="actions">
  <button
    class="cancel-btn"
    @click="$emit('close')"
  >
    {{ t("profileComponents.cancel") }}
  </button>

  <button
    class="save-btn"
    :disabled="loading"
    @click="saveProfile"
  >
    {{
      loading
        ? t("profileComponents.saving")
        : saved
        ? t("profileComponents.saved")
        : t("profileComponents.save")
    }}
  </button>
</div>


  </BaseCard>
</template>

<style scoped>
.settings-card{
  padding:24px;
}

.top{
  margin-bottom:24px;
}

.caption{
  opacity:.65;
  margin-top:6px;
}

.error-message{
  margin:12px 0 0;
  padding:12px 14px;
  border-radius:14px;
  border:1px solid rgba(248,113,113,.28);
  background:rgba(248,113,113,.10);
  color:#fecaca;
  font-size:.9rem;
}

.form{
  display:flex;
  flex-direction:column;
  gap:22px;
}

.field{
  display:flex;
  flex-direction:column;
  gap:8px;
}

label{
  font-size:.9rem;
  font-weight:600;
  opacity:.85;
}

/* ---------- Inputs ---------- */

input,
textarea,
select{
  width:100%;

  border:none;
  outline:none;

  border-radius:14px;
  padding:14px 16px;

  background:rgba(255,255,255,.05);
  color:white;

  border:1px solid rgba(255,255,255,.08);

  transition:
    border-color .18s ease,
    background .18s ease,
    box-shadow .18s ease;
}

input:focus,
textarea:focus,
select:focus{
  border-color:rgba(99,102,241,.7);

  box-shadow:
    0 0 0 3px
    rgba(99,102,241,.18);
}

textarea{
  resize:vertical;
  min-height:110px;
}

/* ---------- Select ---------- */

select{
  appearance:none;
  -webkit-appearance:none;
  -moz-appearance:none;

  background:
    rgba(255,255,255,.05);

  color:white;

  cursor:pointer;
}

input[type="checkbox"]{
  width:18px;
  height:18px;
  accent-color:#6366f1;
}

select option{
  background:#18181b;
  color:white;
}

/* ---------- Avatar Picker ---------- */

.avatar-grid{
  display:flex;
  flex-wrap:wrap;
  gap:12px;
}

.avatar-option{
  width:50px;
  height:50px;

  flex:0 0 auto;

  border-radius:50%;

  cursor:pointer;

  border:2px solid transparent;

  transition:
    transform .18s ease,
    border-color .18s ease,
    box-shadow .18s ease;
}

.avatar-option:hover{
  transform:scale(1.05);
}

.avatar-option.active{
  border-color:#6366f1;

  box-shadow:
    0 0 0 3px
    rgba(99,102,241,.25);
}

/* ---------- Telegram Settings ---------- */

.telegram-section{
  margin-top:24px;
  padding-top:22px;
  border-top:1px solid rgba(255,255,255,.08);
}

.telegram-heading{
  display:flex;
  align-items:flex-start;
  justify-content:space-between;
  gap:16px;
  margin-bottom:14px;
}

.telegram-heading h3{
  margin:0;
  font-size:1rem;
}

.status-pill{
  flex:0 0 auto;
  border:1px solid rgba(255,255,255,.12);
  border-radius:999px;
  padding:6px 10px;
  background:rgba(255,255,255,.04);
  color:rgba(255,255,255,.72);
  font-size:.78rem;
  font-weight:700;
}

.status-pill.active{
  border-color:rgba(34,197,94,.34);
  background:rgba(34,197,94,.12);
  color:#bbf7d0;
}

.telegram-meta{
  margin:8px 0 0;
  color:rgba(255,255,255,.66);
  font-size:.88rem;
}

.toggle-list{
  display:flex;
  flex-direction:column;
  gap:12px;
  margin-top:16px;
}

.toggle-row{
  display:flex;
  align-items:center;
  gap:10px;
  padding:10px 12px;
  border:1px solid rgba(255,255,255,.08);
  border-radius:14px;
  background:rgba(255,255,255,.04);
}

.toggle-row span{
  display:flex;
  flex-direction:column;
  gap:3px;
  font-size:.9rem;
}

.toggle-row small{
  color:rgba(255,255,255,.48);
  font-size:.76rem;
  font-weight:600;
}

.connect-code{
  margin-top:16px;
  padding:14px;
  border:1px solid rgba(99,102,241,.24);
  border-radius:14px;
  background:rgba(99,102,241,.10);
}

.connect-label{
  margin:0 0 6px;
  color:rgba(255,255,255,.68);
  font-size:.82rem;
}

.connect-code strong{
  display:inline-block;
  letter-spacing:.04em;
}

.connect-code a{
  display:inline-block;
  margin-top:10px;
  color:#c4b5fd;
  font-weight:700;
  text-decoration:none;
}

.telegram-actions{
  display:flex;
  justify-content:flex-end;
  flex-wrap:wrap;
  gap:12px;
  margin-top:16px;
}

.danger{
  border-color:rgba(248,113,113,.28);
  color:#fecaca;
}

/* ---------- Actions ---------- */

.actions{
  display:flex;
  justify-content:flex-end;
  gap:12px;

  margin-top:12px;
}

/* ---------- Cancel ---------- */

.cancel-btn{
  border:1px solid rgba(255,255,255,.12);

  background:
    rgba(255,255,255,.04);

  color:white;

  border-radius:14px;

  padding:12px 18px;

  cursor:pointer;

  transition:.18s ease;
}

.cancel-btn:hover{
  background:
    rgba(255,255,255,.08);
}

/* ---------- Save ---------- */

.save-btn{
  border:none;

  border-radius:14px;

  padding:12px 20px;

  cursor:pointer;

  font-weight:600;

  color:white;

  background:
    linear-gradient(
      135deg,
      rgba(99,102,241,.85),
      rgba(79,70,229,.95)
    );

  transition:
    transform .18s ease,
    opacity .18s ease,
    box-shadow .18s ease;
}

.save-btn:hover{
  transform:translateY(-1px);

  box-shadow:
    0 10px 24px
    rgba(99,102,241,.25);
}

.save-btn:disabled{
  opacity:.65;
  cursor:not-allowed;
  transform:none;
}
</style>
