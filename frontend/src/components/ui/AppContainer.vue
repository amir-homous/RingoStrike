<template>
  <div class="app">
    <div class="container">
      <slot />
    </div>
  </div>
</template>

<style scoped>
.app{
  min-height: 100vh;
  width: 100%;
  max-width: 100%;
  box-sizing: border-box;
  padding: var(--s-24) var(--px);
  background: var(--bg);
  overflow-x: clip;
}
.container{
  width: 100%;
  min-width: 0;
  max-width: var(--container);
  margin: 0 auto;
}
</style>
