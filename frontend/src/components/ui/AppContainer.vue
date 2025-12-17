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
  padding: var(--s-24) var(--px);
}
.container{
  max-width: var(--container);
  margin: 0 auto;
}
</style>
