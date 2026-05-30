<script setup>
import { ref, onMounted } from "vue";

import api from "@/lib/api";

import BaseCard from "@/components/ui/BaseCard.vue";

const loading = ref(false);
const saved = ref(false);

const form = ref({
  bio: "",
  avatar_url: "",
  profile_visibility: "public",
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
  try {
    const response = await api.get("/me/profile");

    const profile = response.data.profile;

    form.value.bio = profile.bio || "";
    form.value.avatar_url =
      profile.avatar_url || "";

    form.value.profile_visibility =
      profile.profile_visibility || "public";
  } catch (err) {
    console.error(err);
  }
}

async function saveProfile() {
  console.log("SAVE CLICKED");
  loading.value = true;
  saved.value = false;

  try {
    await api.patch("/api/me/profile/settings", {
      bio: form.value.bio,
      avatar_url: form.value.avatar_url,
      profile_visibility: form.value.profile_visibility,
    });

    saved.value = true;
    emit("saved");

    setTimeout(() => {
      saved.value = false;
    }, 2000);

  } catch (err) {
    console.error(err);
  } finally {
    loading.value = false;
  }
}

onMounted(loadProfile);
</script>

<template>
  <BaseCard class="settings-card">
    <div class="top">
      <div>
        <h2>Profile Settings</h2>

        <p class="caption">
          Customize your public identity.
        </p>
      </div>
    </div>

    <div class="field">
      <label>Choose Avatar</label>

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
      <label>Bio</label>

      <textarea v-model="form.bio" rows="4" placeholder="Tell your progression story..." />
    </div>
<br>
    <div class="field">
      <label>Profile Visibility</label>

      <select v-model="form.profile_visibility">
        <option value="public">
          Public
        </option>

        <option value="private">
          Private
        </option>
      </select>
    </div>

    <div class="actions">
  <button
    class="cancel-btn"
    @click="$emit('close')"
  >
    Cancel
  </button>

  <button
    class="save-btn"
    :disabled="loading"
    @click="saveProfile"
  >
    {{
      loading
        ? "Saving..."
        : saved
        ? "Saved"
        : "Save Profile"
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