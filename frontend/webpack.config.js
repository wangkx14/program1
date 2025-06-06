const path = require('path');

/**
 * 自定义Webpack插件，用于过滤掉ResizeObserver错误
 */
class FilterResizeObserverErrorsPlugin {
  apply(compiler) {
    // 监听compilation完成事件
    compiler.hooks.done.tap('FilterResizeObserverErrorsPlugin', stats => {
      if (stats.hasErrors()) {
        // 过滤掉ResizeObserver错误
        stats.compilation.errors = stats.compilation.errors.filter(error => {
          if (error && error.message && error.message.includes('ResizeObserver')) {
            // 从错误列表中移除ResizeObserver相关错误
            return false;
          }
          return true;
        });
      }
    });

    // 在将资源发送到客户端之前修改它们
    compiler.hooks.compilation.tap('FilterResizeObserverErrorsPlugin', compilation => {
      // 尝试修改webpack-dev-server的客户端代码
      compilation.hooks.processAssets.tap(
        {
          name: 'FilterResizeObserverErrorsPlugin',
          stage: compilation.PROCESS_ASSETS_STAGE_DERIVED
        },
        assets => {
          // 查找webpack-dev-server的客户端覆盖层资源
          Object.keys(assets).forEach(assetName => {
            if (assetName.includes('webpack-dev-server') && assetName.includes('client')) {
              const asset = assets[assetName];
              if (asset && asset.source) {
                let source = asset.source();
                if (typeof source === 'string' && source.includes('ResizeObserver')) {
                  // 在客户端代码中注入过滤ResizeObserver错误的逻辑
                  source = source.replace(
                    /(function\s+showProblems\s*\([^)]*\)\s*\{)/,
                    '$1\n' +
                    '  // Filter out ResizeObserver errors\n' +
                    '  problems = problems.filter(function(problem) {\n' +
                    '    return !(problem && problem.message && problem.message.includes("ResizeObserver"));\n' +
                    '  });\n' +
                    '  if (problems.length === 0) return;\n'
                  );
                  // 更新资源
                  assets[assetName] = {
                    source: () => source,
                    size: () => source.length
                  };
                }
              }
            }
          });
        }
      );
    });
  }
}

// 导出webpack配置
module.exports = {
  // 这个配置会与Vue CLI的配置合并
  configureWebpack: {
    plugins: [
      new FilterResizeObserverErrorsPlugin()
    ],
    // 开发服务器配置
    devServer: {
      client: {
        overlay: {
          errors: true,
          warnings: false,
          // 自定义覆盖层过滤器
          runtimeErrors: (error) => {
            if (error && error.message && error.message.includes('ResizeObserver')) {
              return false; // 不显示ResizeObserver错误
            }
            return true; // 显示其他错误
          }
        }
      }
    }
  }
}; 