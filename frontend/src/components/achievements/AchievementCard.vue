<template><article class="card"><p class="title">{{ item.title }}</p><p class="caption">{{ item.description }}</p><span class="tag" :class="item.rarity">{{ item.rarity }}</span></article></template>
<script setup>defineProps({item:Object})</script>
<style scoped>.card{padding:10px;border:1px solid rgba(255,255,255,.12);border-radius:10px;background:rgba(255,255,255,.03)}.title{margin:0 0 4px;font-weight:650}.tag{font-size:11px;text-transform:capitalize;color:var(--muted2)}.tag.epic,.tag.legendary{color:rgba(199,210,254,.95)}</style>
