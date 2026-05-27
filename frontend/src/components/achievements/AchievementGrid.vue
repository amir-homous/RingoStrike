<template><div class="grid"><AchievementCard v-for="a in items" :key="a.key" :item="a" /></div></template>
<script setup>import AchievementCard from './AchievementCard.vue';defineProps({items:{type:Array,default:()=>[]}})</script>
<style scoped>.grid{display:grid;gap:8px;grid-template-columns:repeat(auto-fit,minmax(180px,1fr))}</style>
