<template><TransitionGroup name="t" tag="div" class="stack"><div class="toast" v-for="a in items" :key="a.id">🏆 {{ a.title }}</div></TransitionGroup></template>
<script setup>defineProps({items:{type:Array,default:()=>[]}})</script>
<style scoped>.stack{position:fixed;left:20px;bottom:20px;display:grid;gap:8px;z-index:30}.toast{padding:10px 12px;border-radius:10px;border:1px solid rgba(251,191,36,.35);background:rgba(24,20,12,.88)}.t-enter-active,.t-leave-active{transition:all .3s ease}.t-enter-from,.t-leave-to{opacity:0;transform:translateY(8px)}</style>
