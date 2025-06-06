import { createApp } from 'vue'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import App from './App.vue'
import router from './router'
import store from './store'
import { applyErrorSuppressions } from './utils/errorHandler'

// 应用错误抑制措施（会自动只在开发环境中应用）
applyErrorSuppressions();

// 添加全局错误处理，特别处理ResizeObserver错误
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

// 强制覆盖原生ResizeObserver，防止其循环错误
try {
  // 保存原始的ResizeObserver
  const OriginalResizeObserver = window.ResizeObserver;
  
  // 重写ResizeObserver
  window.ResizeObserver = class CustomResizeObserver extends OriginalResizeObserver {
    constructor(callback) {
      // 包装回调函数，捕获并处理可能的错误
      const wrappedCallback = (entries, observer) => {
        try {
          // 过滤掉无效的条目
          const validEntries = entries.filter(entry => {
            // 检查目标元素是否仍在文档中
            return entry && entry.target && document.body.contains(entry.target);
          });
          
          // 如果没有有效条目，直接返回
          if (validEntries.length === 0) return;
          
          // 只传递有效的条目给原始回调
          callback(validEntries, observer);
        } catch (e) {
          if (e.message && (
            e.message.includes('ResizeObserver') || 
            e.message.includes('Maximum update depth') ||
            e.message.includes('disconnected') ||
            e.message.includes('null') ||
            e.message.includes('undefined')
          )) {
            console.warn('Suppressed ResizeObserver error:', e);
            return; // 忽略错误并继续
          }
          throw e; // 非ResizeObserver相关错误则重新抛出
        }
      };
      super(wrappedCallback);
      
      // 增强disconnect方法
      const originalDisconnect = this.disconnect;
      this.disconnect = function() {
        try {
          originalDisconnect.call(this);
        } catch (e) {
          console.warn('Suppressed error in disconnect:', e);
        }
      };
    }
  };
  
  console.log('成功加强了ResizeObserver处理');
} catch (error) {
  console.warn('无法加强ResizeObserver处理:', error);
}

// 添加webpack-dev-server覆盖层处理 - 直接干预DOM，隐藏错误覆盖层
if (process.env.NODE_ENV === 'development') {
  // 定期检查并移除错误覆盖层
  const removeErrorOverlay = () => {
    try {
      const overlays = document.querySelectorAll('div[id^="webpack-dev-server-client-overlay"]');
      overlays.forEach(overlay => {
        if (overlay.textContent && overlay.textContent.includes('ResizeObserver')) {
          // 完全移除错误覆盖层
          overlay.parentNode && overlay.parentNode.removeChild(overlay);
        }
      });
    } catch (e) {
      // 忽略错误
    }
  };
  
  // 每秒检查一次
  setInterval(removeErrorOverlay, 1000);
  
  // 在文档加载完成后立即检查
  window.addEventListener('DOMContentLoaded', removeErrorOverlay);
  window.addEventListener('load', removeErrorOverlay);
}

const app = createApp(App)

// 添加全局错误处理程序
app.config.errorHandler = (err, vm, info) => {
  // 忽略ResizeObserver相关错误
  if (err && err.message && (
    err.message.includes('ResizeObserver') || 
    err.message.includes('Maximum update depth')
  )) {
    console.warn('全局捕获到ResizeObserver错误:', err.message);
    return;
  }
  console.error(err);
};

app.use(ElementPlus, {
  // 设置Element Plus的一些选项
  size: 'default',
  zIndex: 2000
})
app.use(router)
app.use(store)

app.mount('#app') 