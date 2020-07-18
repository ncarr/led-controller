const path = require('path')
module.exports = {
  "transpileDependencies": [
    "vuetify"
  ],
  configureWebpack: {
    resolve: {
      alias: {
        // Force @apollo/client 3
        'apollo-client': '@apollo/client/core',
        'apollo-cache-inmemory': '@apollo/client/core',
        'apollo-link': '@apollo/client/core',
        'apollo-link-http': '@apollo/client/core',
        'apollo-link-http-common': '@apollo/client/core',
        'apollo-link-ws': '@apollo/client/link/ws',
        'apollo-link-context': '@apollo/client/link/context',
        'apollo-utilities': '@apollo/client/utilities'
      }
    }
  },
  chainWebpack: config => {
    // Patch Observable support at compile time (vuejs/vue-apollo#981)
    config.module
      .rule('polyfill')
        .test(/vue-apollo\.esm\.js$/)
        .pre()
        .use('string-replace')
          .loader('string-replace-loader')
          .options({
            search: /this\.observer\.currentResult\(\)/g,
            replace: 'this.observer.getCurrentResult ? this.observer.getCurrentResult() : this.observer.currentResult()'
          })
  },
  pluginOptions: {
    apollo: {
      lintGQL: true
    }
  }
}