/**
 * 自定义错误处理工具
 * 用于处理和抑制开发环境中的特定错误
 */

// 处理并隐藏ResizeObserver错误
export const suppressResizeObserverErrors = () => {
  // 覆盖原生控制台错误输出
  const originalConsoleError = console.error;
  console.error = function(message, ...args) {
    // 过滤掉ResizeObserver的错误
    if (typeof message === 'string' && 
        (message.includes('ResizeObserver') || 
         message.includes('ResizeObserver loop limit exceeded') || 
         message.includes('ResizeObserver loop completed with undelivered notifications'))) {
      // 忽略这些错误
      return;
    }
    originalConsoleError.apply(console, [message, ...args]);
  };

  // 修改window.onerror以过滤ResizeObserver错误
  const originalOnError = window.onerror;
  window.onerror = function(message, source, lineno, colno, error) {
    // 过滤掉ResizeObserver的错误
    if (message && typeof message === 'string' && message.includes('ResizeObserver')) {
      // 阻止错误冒泡
      return true;
    }
    // 对于其他错误，调用原始的onerror
    return originalOnError ? originalOnError(message, source, lineno, colno, error) : false;
  };

  // 修改webpack-dev-server的错误覆盖层
  try {
    // 查找webpack-dev-server的错误覆盖层元素
    const findAndRemoveOverlay = () => {
      const overlays = document.querySelectorAll('div[id^="webpack-dev-server-client-overlay"]');
      overlays.forEach(overlay => {
        // 检查覆盖层内容是否包含ResizeObserver错误
        if (overlay.textContent && overlay.textContent.includes('ResizeObserver')) {
          // 隐藏覆盖层
          overlay.style.display = 'none';
          // 或者完全移除
          overlay.parentNode.removeChild(overlay);
        }
      });
    };

    // 定期检查并移除错误覆盖层
    setInterval(findAndRemoveOverlay, 1000);

    // 使用MutationObserver监听DOM变化
    const observer = new MutationObserver((mutations) => {
      mutations.forEach((mutation) => {
        if (mutation.addedNodes.length) {
          findAndRemoveOverlay();
        }
      });
    });

    // 开始观察body的变化
    observer.observe(document.body, { childList: true, subtree: true });
  } catch (e) {
    console.warn('无法修改webpack-dev-server的错误覆盖层:', e);
  }
};

// 应用所有错误抑制措施
export const applyErrorSuppressions = () => {
  // 只在开发环境中应用
  if (process.env.NODE_ENV === 'development') {
    suppressResizeObserverErrors();
  }
};

export default {
  suppressResizeObserverErrors,
  applyErrorSuppressions
}; 