<template>
    <div>
      <label for="file-upload" class="button">
        Select file
      </label>
      <input
        id="file-upload"
        type="file"
        ref="fileInput"
        style="display: none;"
        @change="handleFileSelected"
      />
    </div>
  </template>
  
  <script setup lang="ts">
  import { ref } from 'vue'
  
  function handleFileSelected() {
    const fileInput = ref<HTMLInputElement | null>(null)
  
    if (fileInput.value && fileInput.value.files) {
      const selectedFile = fileInput.value.files[0]
      // Do something with the selected file
    }
  }
  </script>
  
  <style scoped>
  .button {
    display: inline-block;
    padding: 8px 16px;
    font-size: 14px;
    font-weight: 600;
    line-height: 1;
    text-align: center;
    color: #fff;
    background-color: #007aff;
    border-radius: 4px;
    cursor: pointer;
  }
  </style>