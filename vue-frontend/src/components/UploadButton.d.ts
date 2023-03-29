declare module '*.vue' {
    import Vue from 'vue';
    export default Vue;
  }
  
  declare module '@/components/UploadButton.vue' {
    import { Vue } from 'vue/types/vue';
    export default Vue;
  }