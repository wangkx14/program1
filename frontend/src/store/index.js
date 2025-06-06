import { createStore } from 'vuex'
import axios from 'axios'
import loadingModule from './modules/loading'

const API_URL = 'http://localhost:5000'  // 使用固定的后端URL

export default createStore({
  modules: {
    loading: loadingModule
  },
  state: {
    user: JSON.parse(localStorage.getItem('user')) || null,
    token: localStorage.getItem('token') || null
  },
  mutations: {
    setUser(state, user) {
      state.user = user
      localStorage.setItem('user', JSON.stringify(user))
    },
    setToken(state, token) {
      state.token = token
      localStorage.setItem('token', token)
    },
    clearUser(state) {
      state.user = null
      state.token = null
      localStorage.removeItem('user')
      localStorage.removeItem('token')
    }
  },
  actions: {
    async login({ commit }, { username, password }) {
      try {
        console.log('尝试登录:', { username })
        
        const response = await axios.post(`${API_URL}/api/auth/login`, {
          username,
          password
        })
        
        const { user, access_token } = response.data
        console.log('登录成功，获取到token和用户信息:', { user, token_length: access_token?.length })
        
        commit('setUser', user)
        commit('setToken', access_token)
        
        // 添加默认认证头
        axios.defaults.headers.common['Authorization'] = `Bearer ${access_token}`
        
        return user
      } catch (error) {
        console.error('Login failed:', error.response || error)
        throw new Error(
          error.response?.data?.error || 
          error.message || 
          '登录失败，请检查网络连接'
        )
      }
    },
    logout({ commit }) {
      // 移除默认认证头
      delete axios.defaults.headers.common['Authorization']
      commit('clearUser')
    },
    async checkAuth({ state, commit }) {
      // 如果本地有token但没有用户信息，尝试获取用户信息
      if (state.token && !state.user) {
        try {
          console.log('尝试使用token获取用户信息')
          
          // 设置认证头
          axios.defaults.headers.common['Authorization'] = `Bearer ${state.token}`
          
          const response = await axios.get(`${API_URL}/api/auth/me`, {
            headers: {
              Authorization: `Bearer ${state.token}`
            }
          })
          commit('setUser', response.data)
          return true
        } catch (error) {
          console.error('获取用户信息失败:', error)
          // 移除默认认证头
          delete axios.defaults.headers.common['Authorization']
          commit('clearUser')
          return false
        }
      }
      
      // 如果有token，设置默认认证头
      if (state.token) {
        axios.defaults.headers.common['Authorization'] = `Bearer ${state.token}`
      }
      
      return !!state.token
    }
  },
  getters: {
    isAuthenticated: state => !!state.token,
    currentUser: state => state.user,
    isAdmin: state => state.user?.role === 'admin',
    userRole: state => state.user?.role || ''
  }
}) 