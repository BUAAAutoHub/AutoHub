<template>
    <v-container>
      <v-breadcrumbs class="mb-4">
        <v-breadcrumbs-item v-for="(file, index) in openedFiles" :key="index" @click="switchToFile(index)">
          {{ file.name }}
        </v-breadcrumbs-item>
      </v-breadcrumbs>
  
      <div v-for="(file, index) in openedFiles" :key="index" v-show="currentIndex === index">
        <!-- 这里放置代码编辑器组件，根据打开的文件切换内容 -->
        <textarea v-model="file.content" rows="10" cols="50"></textarea>
      </div>
    </v-container>
  </template>
  
  <script>
  export default {
    data() {
      return {
        openedFiles: [
          { name: 'File 1', content: 'Content of file 1' },
          { name: 'File 2', content: 'Content of file 2' },
          { name: 'File 3', content: 'Content of file 3' }
        ],
        currentIndex: 0
      };
    },
    methods: {
      switchToFile(index) {
        this.currentIndex = index;
      }
    }
  };
  </script>