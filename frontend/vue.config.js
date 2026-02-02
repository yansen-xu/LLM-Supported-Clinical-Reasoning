const { defineConfig } = require('@vue/cli-service')

module.exports = defineConfig({
  transpileDependencies: true,
  devServer: {
    proxy: {
      '/api/evaluation_8084': {
        target: 'http://localhost:5003',
        changeOrigin: true,
        secure: false,
        pathRewrite: {
          '^/api/evaluation_8084': '/api/evaluation'
        }
      },
      '/api/evaluation_LLM': {
        target: 'http://localhost:5002',
        changeOrigin: true,
        secure: false,
        pathRewrite: {
          '^/api/evaluation_LLM': '/api/evaluation'
        }
      },
      '/api/evaluation': {
        target: 'http://localhost:5001',
        changeOrigin: true,
        secure: false
      },
      '/api/llm': {
        target: 'http://localhost:5002',
        changeOrigin: true,
        secure: false
      }
    }
  }
})
