import { createRouter, createWebHistory } from 'vue-router'
import store from '../store'
import { ElMessage } from 'element-plus'

const routes = [
  {
    path: '/',
    redirect: '/dashboard'
  },
  {
    path: '/login',
    name: 'Login',
    component: () => import('../views/Login.vue'),
    meta: { requiresAuth: false }
  },
  {
    path: '/dashboard',
    name: 'Dashboard',
    component: () => import('../views/Dashboard.vue'),
    meta: { 
      requiresAuth: true,
      roles: ['admin', 'user']
    }
  },
  {
    path: '/stations',
    name: 'Stations',
    component: () => import('../views/Stations.vue'),
    meta: { 
      requiresAuth: true,
      roles: ['admin', 'user']
    }
  },
  {
    path: '/robots',
    name: 'Robots',
    component: () => import('../views/Robots.vue'),
    meta: { 
      requiresAuth: true,
      roles: ['admin']
    }
  },
  {
    path: '/orders',
    name: 'Orders',
    component: () => import('../views/Orders.vue'),
    meta: { 
      requiresAuth: true,
      roles: ['admin', 'user']
    }
  },
  {
    path: '/system',
    name: 'System',
    component: () => import('../views/System.vue'),
    meta: { 
      requiresAuth: true,
      roles: ['admin']
    }
  },
  {
    path: '/test-api',
    name: 'TestApi',
    component: () => import('../views/TestApi.vue'),
    meta: { 
      requiresAuth: true,
      roles: ['admin']
    }
  },
  {
    path: '/energy-efficiency',
    name: 'EnergyEfficiency',
    component: () => import('../views/EnergyEfficiency.vue'),
    meta: { 
      requiresAuth: true,
      roles: ['admin', 'user']
    }
  },
  {
    path: '/:pathMatch(.*)*',
    redirect: '/dashboard'
  }
]

const router = createRouter({
  history: createWebHistory(process.env.BASE_URL),
  routes
})

// 全局前置守卫
router.beforeEach(async (to, from, next) => {
  // 检查路由是否需要认证
  const requiresAuth = to.matched.some(record => record.meta.requiresAuth !== false)
  
  if (requiresAuth) {
    // 检查用户是否已登录
    const isAuthenticated = await store.dispatch('checkAuth')
    
    if (!isAuthenticated) {
      // 未登录，重定向到登录页
      ElMessage.warning('请先登录')
      next({ name: 'Login', query: { redirect: to.fullPath } })
      return
    }
    
    // 检查用户角色是否有权限访问
    const userRole = store.getters.userRole
    const requiredRoles = to.matched.flatMap(record => record.meta.roles || [])
    
    if (requiredRoles.length > 0 && !requiredRoles.includes(userRole)) {
      // 用户角色没有权限访问该路由
      ElMessage.error('您没有权限访问该页面')
      next(from.path || '/')
      return
    }
  }
  
  // 用户已登录且访问登录页，重定向到首页
  if (to.name === 'Login' && store.getters.isAuthenticated) {
    next({ path: '/' })
    return
  }
  
  next()
})

export default router 