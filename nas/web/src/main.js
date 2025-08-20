import { createApp } from 'vue'
import './style.css'
import App from './App.vue'
import router from './router'
import axios from 'axios';
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
// 第二种方案：设置全局 baseURL
axios.defaults.baseURL = 'http://localhost:5000';


createApp(App).use(router).use(ElementPlus).mount('#app')
