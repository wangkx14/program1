// 加载状态管理模块

const state = {
  // 全局加载状态
  isLoading: false,
  // 特定API端点的加载状态
  endpointLoading: {}
}

const mutations = {
  // 设置全局加载状态
  SET_LOADING(state, isLoading) {
    state.isLoading = isLoading
  },
  // 设置特定端点的加载状态
  SET_ENDPOINT_LOADING(state, { endpoint, isLoading }) {
    state.endpointLoading = {
      ...state.endpointLoading,
      [endpoint]: isLoading
    }
  }
}

const actions = {
  // 开始加载
  startLoading({ commit }) {
    commit('SET_LOADING', true)
  },
  // 结束加载
  endLoading({ commit }) {
    commit('SET_LOADING', false)
  },
  // 设置特定端点的加载状态
  setEndpointLoading({ commit }, { endpoint, isLoading }) {
    commit('SET_ENDPOINT_LOADING', { endpoint, isLoading })
  }
}

const getters = {
  // 获取全局加载状态
  isLoading: state => state.isLoading,
  // 获取特定端点的加载状态
  isEndpointLoading: state => endpoint => {
    return !!state.endpointLoading[endpoint]
  }
}

export default {
  namespaced: true,
  state,
  mutations,
  actions,
  getters
} 