import App from './App.vue'

export function createVersionApp(appCreator) {
    const app = appCreator(App)

    app.config.globalProperties.$versionType = 'evaluation'

    return app
}