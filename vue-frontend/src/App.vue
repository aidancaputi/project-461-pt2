<script setup lang="ts">
import HelloWorld from './components/HelloWorld.vue'
import SearchBar from './components/SearchBar.vue'
import UploadButton from './components/UploadButton.vue'
function handleFileSelected(file: File) {
  // Do something with the selected file
}
</script>

<template>
  <header>
    <img alt="461 logo" class="logo" src="./assets/461.jpg" width="125" height="125" />

    <div class="wrapper">
      <HelloWorld msg="461 Project Vue Frontend" />
    </div>
  </header>

  <main>
    <SearchBar />
  </main>

  <div>
    <h1>Upload File</h1>
    <UploadButton
      accept=".pdf,.doc,.docx"
      multiple
      @file-selected="handleFileSelected"
    />
  </div>
  
</template>

<style scoped>
header {
  line-height: 1.5;
}

.logo {
  display: block;
  margin: 0 auto 2rem;
}

@media (min-width: 1024px) {
  header {
    display: flex;
    place-items: center;
    padding-right: calc(var(--section-gap) / 2);
  }

  .logo {
    margin: 0 2rem 0 0;
  }

  header .wrapper {
    display: flex;
    place-items: flex-start;
    flex-wrap: wrap;
  }
}
</style>
