<template>
  <div class="avatar" :style="bgStyle">
    <img v-if="src && !error" :src="src" :alt="name" @error="error=true" />
    <span v-else>{{ initials }}</span>
  </div>
</template>
<script setup>
import { computed, ref } from 'vue';
const props = defineProps({ src:String, name:{type:String,default:'Player'} });
const error = ref(false);
const initials = computed(()=> props.name.split(' ').map(p=>p[0]).join('').slice(0,2).toUpperCase());
const bgStyle = computed(()=> ({ background:`linear-gradient(140deg, rgba(99,102,241,.35), rgba(56,189,248,.28))` }));
</script>
<style scoped>.avatar{width:72px;height:72px;border-radius:16px;display:grid;place-items:center;border:1px solid rgba(255,255,255,.16);overflow:hidden;font-weight:700}img{width:100%;height:100%;object-fit:cover}</style>
