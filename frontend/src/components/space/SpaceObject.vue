<template>
  <div class="spaceObject" :class="{ locked: !reward.unlocked }">
    <span class="objectMark" aria-hidden="true">
      {{ objectMark }}
    </span>
    <span class="objectTitle">{{ reward.title }}</span>
  </div>
</template>

<script setup>
import { computed } from "vue";

const props = defineProps({
  reward: { type: Object, required: true },
});

const objectMark = computed(() => {
  const title = String(props.reward?.title || props.reward?.key || "?").trim();
  return title.slice(0, 1).toUpperCase();
});
</script>

<style scoped>
.spaceObject {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  max-width: 100%;
  min-height: 26px;
  padding: 5px 8px;
  border-radius: 9px;
  color: rgba(255, 255, 255, 0.88);
  background: rgba(110, 229, 255, 0.12);
  border: 1px solid rgba(110, 229, 255, 0.24);
  font-size: 0.72rem;
  font-weight: 800;
}

.spaceObject.locked {
  color: rgba(255, 255, 255, 0.48);
  background: rgba(255, 255, 255, 0.035);
  border-color: rgba(255, 255, 255, 0.09);
  filter: grayscale(0.35);
}

.objectMark {
  display: grid;
  place-items: center;
  width: 18px;
  height: 18px;
  flex: 0 0 auto;
  border-radius: 7px;
  color: rgba(6, 11, 20, 0.92);
  background: rgba(255, 255, 255, 0.86);
  font-size: 0.62rem;
  line-height: 1;
}

.locked .objectMark {
  color: rgba(255, 255, 255, 0.50);
  background: rgba(255, 255, 255, 0.12);
}

.objectTitle {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
</style>
