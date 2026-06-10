<template>
  <figure class="ringoMood" :class="[`size-${size}`, { framed, floating }]">
    <span class="moodGlow" aria-hidden="true"></span>
    <img
      v-if="resolved.src"
      :src="resolved.src"
      :alt="altText"
      loading="lazy"
    />
  </figure>
</template>

<script setup>
import { computed } from "vue";
import { useI18n } from "vue-i18n";

import { resolveRingoSprite } from "@/constants/ringoSprites";

const props = defineProps({
  mood: { type: String, default: "idle" },
  alt: { type: String, default: "" },
  size: {
    type: String,
    default: "md",
    validator: (value) => ["sm", "md", "lg"].includes(value),
  },
  framed: { type: Boolean, default: true },
  floating: { type: Boolean, default: false },
});

const { t } = useI18n();

const resolved = computed(() => resolveRingoSprite(props.mood));

const altText = computed(() => {
  return props.alt || t("ringoCoach.eyebrow");
});
</script>

<style scoped>
.ringoMood {
  position: relative;
  isolation: isolate;
  flex: 0 0 auto;
  display: grid;
  place-items: end center;
  margin: 0;
  overflow: hidden;
}

.ringoMood.framed {
  border: 1px solid rgba(255, 255, 255, 0.12);
  border-radius: 24px;
  background:
    radial-gradient(circle at 50% 20%, rgba(110, 229, 255, 0.18), transparent 46%),
    rgba(255, 255, 255, 0.045);
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.08);
}

.ringoMood.floating {
  transform: translateY(-2px);
}

.ringoMood.size-sm {
  width: 94px;
  height: 94px;
  border-radius: 22px;
}

.ringoMood.size-md {
  width: 130px;
  height: 130px;
}

.ringoMood.size-lg {
  width: 172px;
  height: 172px;
}

.moodGlow {
  position: absolute;
  inset: 18%;
  z-index: -1;
  border-radius: 999px;
  background: rgba(110, 229, 255, 0.18);
  filter: blur(20px);
}

.ringoMood img {
  width: 100%;
  height: 100%;
  object-fit: contain;
  object-position: center bottom;
}

@media (max-width: 560px) {
  .ringoMood.size-md,
  .ringoMood.size-lg {
    width: 112px;
    height: 112px;
  }
}
</style>
