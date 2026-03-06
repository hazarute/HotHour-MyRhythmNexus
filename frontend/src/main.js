import { createApp } from 'vue'
import { createPinia } from 'pinia'
import { createUnhead, headSymbol } from '@unhead/vue'
import App from './App.vue'
import router from './router'
import './style.css'

const app = createApp(App)
const head = createUnhead()

app.use(createPinia())
app.use(router)
app.provide(headSymbol, head)

app.mount('#app')
