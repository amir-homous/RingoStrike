<template>
  <article class="card" :class="[item.rarity || 'common', { locked: !item.unlocked }]">
    <div class="mediaWrap" :class="{ off: !item.unlocked }">
      <img class="media" :src="imageSrc" :alt="item.title" @error="onImageError" v-if="!imageError" />
      <div v-else class="fallback" aria-hidden="true">🏆</div>
    </div>

    <div class="content stack-8">
      <div class="top">
        <p class="title">{{ item.title }}</p>
        <span class="rarity" :class="item.rarity">{{ item.rarity || 'common' }}</span>
      </div>
      <p class="caption desc">{{ item.description }}</p>
      <div class="meta">
        <span class="xp">+{{ item.xp_reward || 0 }} XP</span>
        <span class="state" :class="item.unlocked ? 'on' : 'off'">{{ item.unlocked ? 'Unlocked' : 'Locked' }}</span>
      </div>
    </div>
  </article>
</template>

<script setup>
import { computed, ref } from 'vue';

const props = defineProps({ item: { type: Object, required: true } });
const imageError = ref(false);

const imageSrc = computed(() => `/achievements/${props.item.key}.png`);
function onImageError() { imageError.value = true; }
</script>

<style scoped>
.card{display:grid;grid-template-columns:56px 1fr;gap:var(--s-12);padding:12px;border:1px solid rgba(255,255,255,.12);border-radius:12px;background:rgba(255,255,255,.03);transition:border-color .18s ease,background .18s ease,transform .18s ease}
.card:hover{transform:translateY(-1px);background:rgba(255,255,255,.045)}
.card.locked{opacity:.58;filter:saturate(.72)}
.mediaWrap{width:56px;height:56px;border-radius:12px;overflow:hidden;border:1px solid rgba(255,255,255,.16);background:rgba(255,255,255,.05)}
.mediaWrap.off{filter:grayscale(1)}
.media{width:100%;height:100%;object-fit:cover;display:block}
.fallback{width:100%;height:100%;display:grid;place-items:center}
.top{display:flex;justify-content:space-between;align-items:center;gap:8px}
.title{margin:0;font-weight:650;line-height:1.25}
.desc{margin:0}
.meta{display:flex;justify-content:space-between;gap:8px;font-size:var(--cap);color:var(--muted)}
.rarity{font-size:11px;text-transform:capitalize;padding:3px 7px;border-radius:999px;border:1px solid rgba(255,255,255,.2)}
.rarity.common{color:#c7d2fe;border-color:rgba(199,210,254,.35)}
.rarity.rare{color:#7dd3fc;border-color:rgba(125,211,252,.45)}
.rarity.epic{color:#f0abfc;border-color:rgba(240,171,252,.45)}
.rarity.legendary{color:#fcd34d;border-color:rgba(252,211,77,.5)}
.state.on{color:rgba(167,243,208,.95)}
.state.off{color:var(--muted2)}
.xp{font-weight:620}
</style>
