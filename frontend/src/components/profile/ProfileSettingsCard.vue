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

    <div class="form">
      <div class="field">
        <label>Avatar URL</label>

        <input
          v-model="form.avatar_url"
          type="text"
          placeholder="/player.png"
        />
      </div>

      <div class="field">
        <label>Bio</label>

        <textarea
          v-model="form.bio"
          rows="4"
          placeholder="Tell your progression story..."
        />
      </div>

      <div class="field">
        <label>Profile Visibility</label>

        <select
          v-model="form.profile_visibility"
        >
          <option value="public">
            Public
          </option>

          <option value="private">
            Private
          </option>
        </select>
      </div>

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

      <button
        class="secondary-btn"
        @click="$emit('close')"
      >
        Cancel
      </button>


    </div>
  </BaseCard>
</template>

<style scoped>
.settings-card{
  padding:24px;
}

.top{
  margin-bottom:20px;
}

.caption{
  opacity:.65;
  margin-top:6px;
}

.form{
  display:flex;
  flex-direction:column;
  gap:18px;
}

.field{
  display:flex;
  flex-direction:column;
  gap:8px;
}

label{
  font-size:.9rem;
  opacity:.82;
}

input,
textarea,
select{
  width:100%;
  border:none;
  outline:none;
  border-radius:14px;
  padding:14px;
  background:rgba(255,255,255,.05);
  color:white;
  border:1px solid rgba(255,255,255,.08);
}

textarea{
  resize:vertical;
}

.save-btn{
  margin-top:8px;
  border:none;
  border-radius:14px;
  padding:14px;
  cursor:pointer;
  background:rgba(99,102,241,.22);
  color:white;
  transition:.18s ease;
}

.save-btn:hover{
  background:rgba(99,102,241,.32);
}

select{
  appearance:none;
  background:rgba(255,255,255,.05);
  color:white;
}

select option{
  background:#171717;
  color:white;
  background:rgba(255,255,255,.1);
}


</style>