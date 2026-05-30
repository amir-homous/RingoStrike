<template>
  <div class="avatar" :class="sizeClass">
    <img
      v-if="src && !error"
      :src="src"
      :alt="name"
      @error="error = true"
    />
    <span v-else>
      {{ initials }}
    </span>
  </div>
</template>


<script setup>
import { computed, ref } from 'vue';

const props = defineProps({
  src: String,
  name: { type: String, default: 'Player' },

  size: {
    type: String,
    default: 'md' // sm | md | lg | xl
  }
});

const error = ref(false);

const initials = computed(() =>
  props.name
    .split(' ')
    .map(p => p[0])
    .join('')
    .slice(0, 2)
    .toUpperCase()
);

const sizeClass = computed(() => `avatar--${props.size}`);
</script>

<style scoped>
.avatar{
  display:grid;
  place-items:center;

  border-radius:14px;

  overflow:hidden;

  font-weight:700;

  border:1px solid rgba(255,255,255,.16);

  background: linear-gradient(
    140deg,
    rgba(99,102,241,.35),
    rgba(56,189,248,.28)
  );
}

/* ---------- sizes ---------- */

.avatar--sm{
  width:36px;
  height:36px;
  border-radius:10px;
  font-size:.75rem;
}

.avatar--md{
  width:56px;
  height:56px;
  border-radius:14px;
  font-size:.9rem;
}

.avatar--lg{
  width:84px;
  height:84px;
  border-radius:18px;
  font-size:1.1rem;
}

.avatar--xl{
  width:110px;
  height:110px;
  border-radius:22px;
  font-size:1.3rem;
}

/* image */
img{
  width:100%;
  height:100%;
  object-fit:cover;
}
</style>