import { createSSRApp } from 'vue'
import App from './App.vue'
import { VueSvgIconPlugin } from '@yzfe/vue3-svgicon'
import '@yzfe/svgicon/lib/svgicon.css'
import uviewPlus from 'uview-plus'
import './styles/flex.css'

export function createApp () {
  const app = createSSRApp(App)
  app.use(uviewPlus)
  app.use(VueSvgIconPlugin, {
    tagName: 'icon'
  })
  return {
    app,
  }
}
