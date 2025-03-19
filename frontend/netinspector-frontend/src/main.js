// src/main.js
import { createApp } from 'vue'
import App from './App.vue'
import router from './router'  // 引入路由
import * as ElementPlusIconsVue from '@element-plus/icons-vue'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'



for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
  app.component(key, component)
}
const app = createApp(App)
app.use(router)
app.use(ElementPlus)
app.mount('#app')