<template>
  <div id="app">
    <template v-if="$route.name === 'Login'">
      <router-view />
    </template>
    <el-container v-else>
      <el-header>
        <div class="header-content">
          <div class="logo-container">
            <el-icon class="logo-icon"><TrendCharts /></el-icon>
          </div>
          <h1 class="system-title">货仓机器人激光充电和能效管理云平台</h1>
          
          <div class="user-actions" v-if="isAuthenticated">
            <span class="username">
              <el-icon><User /></el-icon>
              {{ currentUser.username }} ({{ currentUser.role === 'admin' ? '管理员' : '普通用户' }})
            </span>
            <el-dropdown @command="handleCommand">
              <span class="el-dropdown-link">
                <el-icon><Setting /></el-icon>
              </span>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item command="logout">退出登录</el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </div>
        </div>
      </el-header>
      <el-container>
        <el-aside width="200px">
          <el-menu
            router
            :default-active="$route.path"
            class="el-menu-vertical">
            <el-menu-item index="/dashboard">
              <el-icon><Monitor /></el-icon>
              <span>系统概览</span>
            </el-menu-item>
            <el-menu-item index="/stations">
              <el-icon><Location /></el-icon>
              <span>充电桩管理</span>
            </el-menu-item>
            <el-menu-item index="/robots" v-if="isAdmin">
              <el-icon><Cpu /></el-icon>
              <span>机器人管理</span>
            </el-menu-item>
            <el-menu-item index="/orders">
              <el-icon><Document /></el-icon>
              <span>充电订单</span>
            </el-menu-item>
            <el-menu-item index="/energy-efficiency">
              <el-icon><TrendCharts /></el-icon>
              <span>能效分析</span>
            </el-menu-item>
            <el-menu-item index="/system" v-if="isAdmin">
              <el-icon><Setting /></el-icon>
              <span>系统设置</span>
            </el-menu-item>
            <el-menu-item index="/test-api" v-if="isAdmin">
              <el-icon><Connection /></el-icon>
              <span>API测试</span>
            </el-menu-item>
          </el-menu>
        </el-aside>
        <el-main>
          <router-view></router-view>
        </el-main>
      </el-container>
    </el-container>
    
    <!-- 错误覆盖层修复元素 - 仅开发环境 -->
    <div v-if="isDev" class="error-overlay-fix"></div>
  </div>
</template>

<script>
import { computed, onMounted, onUnmounted, ref } from 'vue'
import { useStore } from 'vuex'
import { useRouter } from 'vue-router'
import { ElMessageBox } from 'element-plus'
import { Monitor, Location, Cpu, Document, TrendCharts, Setting, Connection, User } from '@element-plus/icons-vue'
// 开发环境下导入错误处理样式
import '@/assets/css/error-overlay-fix.css'

export default {
  name: 'App',
  components: {
    Monitor,
    Location,
    Cpu,
    Document,
    TrendCharts,
    Setting,
    Connection,
    User
  },
  setup() {
    const store = useStore()
    const router = useRouter()
    
    const isAuthenticated = computed(() => store.getters.isAuthenticated)
    const currentUser = computed(() => store.getters.currentUser || {})
    const isAdmin = computed(() => store.getters.isAdmin)
    const isDev = ref(process.env.NODE_ENV === 'development')
    
    const handleCommand = (command) => {
      if (command === 'logout') {
        ElMessageBox.confirm(
          '确定要退出登录吗？',
          '提示',
          {
            confirmButtonText: '确定',
            cancelButtonText: '取消',
            type: 'warning'
          }
        ).then(() => {
          store.dispatch('logout')
          router.push('/login')
        }).catch(() => {})
      }
    }
    
    // 处理ResizeObserver错误的定时器引用
    let errorOverlayCheckTimer = null
    
    // 组件挂载时设置错误覆盖层处理
    onMounted(() => {
      if (isDev.value) {
        // 处理webpack-dev-server错误覆盖层
        const handleErrorOverlays = () => {
          try {
            const overlays = document.querySelectorAll('div[id^="webpack-dev-server-client-overlay"]');
            overlays.forEach(overlay => {
              // 查找包含ResizeObserver错误的覆盖层
              if (overlay.textContent && overlay.textContent.includes('ResizeObserver')) {
                // 添加自定义类以隐藏
                overlay.classList.add('hide-resize-observer-errors');
                // 或直接设置样式
                overlay.style.display = 'none';
              }
            });
          } catch (e) {
            // 忽略错误
          }
        };
        
        // 立即处理一次
        handleErrorOverlays();
        
        // 设置定时检查
        errorOverlayCheckTimer = setInterval(handleErrorOverlays, 500);
        
        // 监听DOM变化
        try {
          const observer = new MutationObserver((mutations) => {
            mutations.forEach(mutation => {
              if (mutation.addedNodes.length) {
                handleErrorOverlays();
              }
            });
          });
          
          // 开始观察body的变化
          observer.observe(document.body, { childList: true, subtree: true });
        } catch (e) {
          console.warn('无法设置MutationObserver:', e);
        }
      }
    });
    
    // 组件卸载时清理
    onUnmounted(() => {
      if (errorOverlayCheckTimer) {
        clearInterval(errorOverlayCheckTimer);
        errorOverlayCheckTimer = null;
      }
    });
    
    return {
      isAuthenticated,
      currentUser,
      isAdmin,
      isDev,
      handleCommand
    }
  }
}
</script>

<style>
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  height: 100vh;
}

.el-header {
  background: linear-gradient(135deg, #409EFF, #2c6bdb);
  color: white;
  line-height: 60px;
  padding: 0 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.header-content {
  display: flex;
  align-items: center;
  height: 100%;
}

.logo-container {
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: rgba(255, 255, 255, 0.2);
  border-radius: 50%;
  width: 40px;
  height: 40px;
  margin-right: 15px;
}

.logo-icon {
  font-size: 24px;
}

.system-title {
  margin: 0;
  font-size: 20px;
  font-weight: 600;
  letter-spacing: 1px;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.2);
  flex-grow: 1;
}

.user-actions {
  display: flex;
  align-items: center;
}

.username {
  margin-right: 15px;
  font-size: 14px;
  display: flex;
  align-items: center;
}

.username .el-icon {
  margin-right: 5px;
}

.el-dropdown-link {
  cursor: pointer;
  display: flex;
  align-items: center;
}

.el-dropdown-link .el-icon {
  font-size: 18px;
}

.el-aside {
  background-color: #f5f7fa;
  box-shadow: 2px 0 5px rgba(0, 0, 0, 0.05);
}

.el-menu {
  border-right: none;
}

/* 错误覆盖层修复样式 */
.error-overlay-fix {
  position: fixed;
  z-index: 9999;
  pointer-events: none;
}
</style>
