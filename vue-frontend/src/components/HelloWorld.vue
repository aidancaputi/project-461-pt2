<script setup lang="ts">
defineProps<{
  msg: string
}>()
</script>

<template>
  <div class="greetings">
    <h1 class="green">{{ msg }}</h1>
    <h3>
      While Aidan and Dheepa are on the backend, the frontend developers are
      <a href="https://www.linkedin.com/in/zane-middaugh-ab87701bb/" target="_blank" rel="noopener">Zane</a> +
      <a href="https://www.linkedin.com/in/joshchristian280/" target="_blank" rel="noopener">Josh</a>.
    </h3>
  </div>
</template>

<style scoped>
h1 {
  font-weight: 500;
  font-size: 2.6rem;
  top: -10px;
}

h3 {
  font-size: 1.2rem;
}

.greetings h1,
.greetings h3 {
  text-align: center;
}

@media (min-width: 1024px) {
  .greetings h1,
  .greetings h3 {
    text-align: left;
  }
}
</style>
