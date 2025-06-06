module.exports = {
  devServer: {
    proxy: {
      '/api': {
        target: 'http://localhost:5000',
        changeOrigin: true,
        secure: false,
        logLevel: 'debug',
        headers: {
          Connection: 'keep-alive'
        },
        pathRewrite: {
          '^/api': '/api'
        }
      }
    },
    client: {
      overlay: {
        errors: true,
        warnings: false,
        runtimeErrors: (error) => {
          if (error.message && error.message.includes('ResizeObserver')) {
            return false;
          }
          return true;
        }
      }
    }
  },
  lintOnSave: false,
  configureWebpack: {
    devtool: 'source-map',
    plugins: [
      {
        apply(compiler) {
          compiler.hooks.done.tap('FilterErrorsPlugin', stats => {
            if (stats.hasErrors()) {
              stats.compilation.errors = stats.compilation.errors.filter(error => {
                return !(error.message && error.message.includes('ResizeObserver'));
              });
            }
          });
        }
      }
    ]
  }
} 