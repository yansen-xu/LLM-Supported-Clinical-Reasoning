import { createApp } from 'vue'
import './assets/responsive.css'

// 全局变量用于版本切换
window.__APP_MODE__ = 'analysis' // 默认为analysis模式

const loadVersion = async (mode = null) => {
  let appMode = mode || process.env.VUE_APP_MODE || 'analysis'
  
  // 混合模式下总是从analysis开始
  if (appMode === 'analysis' && !mode) {
    // 清除旧的evaluation登录状态，确保以analysis模式启动
    localStorage.removeItem('evaluation_username');
    localStorage.removeItem('evaluation_user_info');
    localStorage.removeItem('evaluation_current_case_id');
  }
  
  window.__APP_MODE__ = appMode
  
  switch (appMode) {
    case 'analysis':
      return import(/* webpackChunkName: "analysis-version" */ './components/analysis/main')
    case 'evaluation':
    case 'evaluation_LLM':
    case 'evaluation_8084':
      return import(/* webpackChunkName: "evaluation-version" */ './components/evaluation/main')
    default:
      throw new Error(`Unknown VUE_APP_MODE: ${appMode}`)
  }
}

// Expose version switch function to global for switching between versions
window.__SWITCH_VERSION__ = async (mode) => {
  try {
    const module = await loadVersion(mode)
    const { createVersionApp } = module
    
    // Clear old app and styles
    const app = document.getElementById('app')
    
    // Remove all style tags added by dynamic imports
    const styleTags = document.querySelectorAll('style[data-vite-inspector]');
    styleTags.forEach(tag => tag.remove());
    
    // Clear app content
    app.innerHTML = ''
    app.className = '' // Clear any classes
    
    // Clear global state
    window.cData = null;
    window.collectData = null;
    
    // Create and mount new app
    const newApp = createVersionApp(createApp)
    newApp.config.errorHandler = (err) => {
      console.error('Global error:', err)
    }
    newApp.mount('#app')
  } catch (error) {
    console.error('Version switch failed:', error)
  }
}

loadVersion()
  .then(module => {
    const { createVersionApp } = module
    const app = createVersionApp(createApp)

    app.config.errorHandler = (err) => {
      console.error('Global error:', err)
    }
    app.mount('#app')
  })
  .catch(error => {
    console.error('Version loading failed:', error)
    document.getElementById('app').innerHTML = 'System loading failed, please refresh'
  })