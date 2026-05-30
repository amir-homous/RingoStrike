<template>
  <div
    v-if="open"
    class="overlay"
  >
    <div class="modal">
      <div class="header">
        <h2>Edit Profile</h2>

        <button
          class="close"
          @click="$emit('close')"
        >
          ✕
        </button>
      </div>

      <div class="content">
        <div class="field">
          <label>Name</label>

          <input
            v-model="localName"
            type="text"
          />
        </div>

        <div class="field">
          <label>Bio</label>

          <textarea
            v-model="localBio"
            rows="4"
          />
        </div>

        <div class="field">
          <label>Avatar URL</label>

          <input
            v-model="localAvatar"
            type="text"
          />
        </div>

        <div class="field">
          <label>Profile Visibility</label>

          <select v-model="localVisibility">
            <option value="public">
              Public
            </option>

            <option value="private">
              Private
            </option>
          </select>
        </div>
      </div>

      <div class="footer">
        <button
          class="save"
          @click="submit"
        >
          Save Changes
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import {
  ref,
  watch,
} from "vue";

const props = defineProps({
  open: Boolean,
  profile: Object,
});

const emit = defineEmits([
  "close",
  "save",
]);

const localName = ref("");
const localBio = ref("");
const localAvatar = ref("");
const localVisibility = ref("public");

watch(
  () => props.profile,
  (profile) => {
    if (!profile) return;

    localName.value =
      profile.name || "";

    localBio.value =
      profile.bio || "";

    localAvatar.value =
      profile.avatar_url || "";

    localVisibility.value =
      profile.profile_visibility ||
      "public";
  },
  {
    immediate: true,
  }
);

function submit() {
  emit("save", {
    name: localName.value,
    bio: localBio.value,
    avatar_url: localAvatar.value,
    visibility: localVisibility.value,
  });
}
</script>

<style scoped>
.overlay{
  position:fixed;
  inset:0;
  background:rgba(0,0,0,.55);
  backdrop-filter:blur(8px);
  display:grid;
  place-items:center;
  z-index:1000;
}

.modal{
  width:min(520px,92vw);
  background:#121212;
  border:1px solid rgba(255,255,255,.08);
  border-radius:24px;
  padding:24px;
  box-shadow:0 20px 80px rgba(0,0,0,.45);
}

.header{
  display:flex;
  justify-content:space-between;
  align-items:center;
  margin-bottom:20px;
}

.close{
  border:0;
  background:none;
  color:white;
  cursor:pointer;
  font-size:18px;
}

.content{
  display:grid;
  gap:18px;
}

.field{
  display:grid;
  gap:8px;
}

label{
  opacity:.72;
  font-size:.9rem;
}

input,
textarea,
select{
  width:100%;
  border-radius:14px;
  border:1px solid rgba(255,255,255,.08);
  background:rgba(255,255,255,.04);
  color:white;
  padding:12px;
}

.footer{
  margin-top:24px;
  display:flex;
  justify-content:flex-end;
}

.save{
  border:1px solid rgba(255,255,255,.1);
  background:rgba(255,255,255,.08);
  color:white;
  border-radius:14px;
  padding:12px 18px;
  cursor:pointer;
}
</style>