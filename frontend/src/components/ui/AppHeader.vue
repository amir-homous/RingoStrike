<template>
  <header class="hdr">
    <div class="brand">RingoStrike</div>

    <nav class="nav">
      <RouterLink class="link" :class="{active: isActive('/dashboard')}" to="/dashboard">Dashboard</RouterLink>
      <RouterLink class="link" :class="{active: isActive('/join')}" to="/join">Join</RouterLink>
      <RouterLink class="link" :class="{active: isActive('/leaderboard')}" to="/leaderboard">Leaderboard</RouterLink>
    </nav>
  </header>
</template>

<script setup>
import { useRoute } from 'vue-router'
const route = useRoute()

function isActive(prefix){
  return route.path === prefix || route.path.startsWith(prefix + '/')
}
</script>

<style scoped>
.hdr{
  display:flex;
  align-items:center;
  justify-content: space-between;
  gap: var(--s-16);
  padding: var(--s-12) var(--s-16);
  border: 1px solid var(--border);
  border-radius: var(--r-12);
  background: rgba(255,255,255,0.04);
  margin-bottom: var(--s-24);
}
.brand{ font-weight: 800; letter-spacing: -0.02em; }
.nav{ display:flex; gap: var(--s-8); flex-wrap: wrap; justify-content:flex-end; }
.link{
  padding: 8px 10px;
  border-radius: 10px;
  border: 1px solid transparent;
  color: var(--muted);
}
.link:hover{ background: rgba(255,255,255,0.05); text-decoration:none; }
.link.active{
  color: rgba(255,255,255,0.92);
  border-color: rgba(99,102,241,0.35);
  background: rgba(99,102,241,0.18);
}
</style>
