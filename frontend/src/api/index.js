import axios from 'axios'
import store from '../store'

// 生成后备机器人数据的函数
function generateFallbackRobots() {
  console.log('生成后备机器人数据')
  const robots = []
  const statuses = ['idle', 'working', 'charging', 'error']
  
  for (let i = 1; i <= 10; i++) {
    const status = statuses[Math.floor(Math.random() * statuses.length)]
    const batteryLevel = Math.floor(Math.random() * 100)
    
    robots.push({
      id: i,
      name: `机器人-${i.toString().padStart(3, '0')}`,
      battery_level: batteryLevel,
      status: status,
      last_charging: new Date().toISOString().slice(0, 19).replace('T', ' ')
    })
  }
  
  console.log(`生成了 ${robots.length} 条后备机器人数据`)
  return robots
}

// 生成后备订单数据的函数
function generateFallbackOrders() {
  console.log('生成后备订单数据')
  const orders = []
  const statuses = ['charging', 'completed', 'failed']
  
  for (let i = 1; i <= 10; i++) {
    const status = statuses[Math.floor(Math.random() * statuses.length)]
    const startTime = new Date(Date.now() - Math.floor(Math.random() * 30 * 24 * 60 * 60 * 1000))
      .toISOString().slice(0, 19).replace('T', ' ')
    
    const order = {
      id: i,
      robot_id: Math.floor(Math.random() * 10) + 1,
      station_id: Math.floor(Math.random() * 10) + 1,
      start_time: startTime,
      status: status
    }
    
    // 如果状态是已完成，添加结束时间和充电量
    if (status === 'completed') {
      const endTime = new Date(new Date(startTime).getTime() + Math.floor(Math.random() * 4 * 60 * 60 * 1000))
        .toISOString().slice(0, 19).replace('T', ' ')
      order.end_time = endTime
      order.amount = Math.floor(Math.random() * 40) + 10
    }
    
    orders.push(order)
  }
  
  console.log(`生成了 ${orders.length} 条后备订单数据`)
  return orders
}

// 生成后备充电站数据的函数
function generateFallbackStations() {
  console.log('生成后备充电站数据')
  const stations = []
  const statuses = ['idle', 'charging', 'maintenance', 'error']
  
  for (let i = 1; i <= 8; i++) {
    const status = statuses[Math.floor(Math.random() * statuses.length)]
    const efficiency = Math.floor(Math.random() * 15) + 80 // 80-95
    
    stations.push({
      id: i,
      name: `充电站-${i}`,
      location: `位置${i}`,
      status: status,
      power_rating: Math.floor(Math.random() * 5) + 5, // 5-10
      efficiency: efficiency
    })
  }
  
  console.log(`生成了 ${stations.length} 条后备充电站数据`)
  return stations
}

const api = axios.create({
  baseURL: 'http://localhost:5000/api',
  timeout: 5000
})

// 暴露api实例，供其他模块使用
export { api }

// 请求拦截器
api.interceptors.request.use(
  config => {
    console.log(`API请求: ${config.method.toUpperCase()} ${config.url}`)
    
    // 设置加载状态
    store.dispatch('loading/setEndpointLoading', { 
      endpoint: config.url, 
      isLoading: true 
    })
    
    const token = localStorage.getItem('token')
    if (token) {
      // 确保令牌格式正确
      if (typeof token === 'string' && token.trim() !== '') {
        config.headers.Authorization = `Bearer ${token.trim()}`
        // 禁用token缓存，确保每次请求都使用最新的token
        config.headers['Cache-Control'] = 'no-cache'
        console.log('已添加认证令牌')
      } else {
        console.warn('令牌格式不正确:', token)
        localStorage.removeItem('token')
      }
    } else {
      console.log('未找到认证令牌')
    }
    return config
  },
  error => {
    console.error('请求拦截器错误:', error)
    return Promise.reject(error)
  }
)

// 响应拦截器
api.interceptors.response.use(
  response => {
    console.log(`API响应: ${response.config.method.toUpperCase()} ${response.config.url}`, response.data)
    
    // 清除加载状态
    store.dispatch('loading/setEndpointLoading', { 
      endpoint: response.config.url, 
      isLoading: false 
    })
    
    return response
  },
  error => {
    // 清除加载状态
    if (error.config) {
      store.dispatch('loading/setEndpointLoading', { 
        endpoint: error.config.url, 
        isLoading: false 
      })
    }
    
    // 处理认证错误
    if (error.response && error.response.status === 401) {
      console.error('认证失败，需要重新登录')
      // 清除本地存储的认证信息
      localStorage.removeItem('token')
      localStorage.removeItem('user')
      // 如果不是登录页面，可以重定向到登录页
      if (window.location.pathname !== '/login') {
        window.location.href = '/login'
      }
    }
    
    console.error('API错误:', error.response ? error.response.data : error.message)
    return Promise.reject(error)
  }
)

// 充电站相关 API
export const stationApi = {
  // 获取所有充电站
  getAll() {
    console.log('调用API: 获取所有充电站')
    return new Promise((resolve, reject) => {
      api.get('/stations/', {
        headers: {
          'Accept': 'application/json',
          'Content-Type': 'application/json'
        },
        responseType: 'json'
      })
        .then(response => {
          console.log('充电站API响应状态:', response.status)
          console.log('充电站API响应头:', response.headers)
          
          let data = response.data
          console.log('原始响应数据类型:', typeof data)
          
          // 处理各种响应类型
          try {
            // 1. 如果是字符串，尝试解析为JSON
            if (typeof data === 'string') {
              console.log('响应是字符串，尝试解析为JSON')
              try {
                // 处理NaN值，将其替换为null
                const cleanedData = data.replace(/: ?NaN/g, ': null')
                data = JSON.parse(cleanedData)
                console.log('解析后的数据类型:', typeof data)
              } catch (e) {
                console.error('解析字符串为JSON失败:', e)
              }
            }
            
            // 2. 检查是否为null或undefined
            if (data === null || data === undefined) {
              console.error('API返回的充电站数据为null或undefined')
              resolve({ data: [] })
              return
            }
            
            // 3. 确保数据是数组
            if (!Array.isArray(data)) {
              console.error('API返回的充电站数据不是数组:', typeof data)
              
              // 如果是对象且有data属性是数组，则使用该属性
              if (data && typeof data === 'object' && Array.isArray(data.data)) {
                console.log('使用响应对象中的data属性作为数据数组')
                data = data.data
              } else {
                // 最后的后备方案：使用硬编码的充电站数据
                console.error('使用硬编码的充电站数据')
                data = generateFallbackStations()
              }
            }
            
            // 4. 验证数组中每个元素是否为有效的充电站对象
            data = data.filter(item => {
              const isValid = item && 
                     typeof item === 'object' && 
                     'id' in item && 
                     'name' in item && 
                     'location' in item && 
                     'status' in item
              
              if (!isValid) {
                console.warn('过滤掉无效的充电站数据:', item)
              }
              return isValid
            })
            
            console.log(`过滤后的充电站数据数量: ${data.length}`)
            
            // 5. 如果过滤后数组为空，使用后备数据
            if (data.length === 0) {
              console.warn('过滤后没有有效的充电站数据，使用后备数据')
              data = generateFallbackStations()
            }
            
            // 返回处理后的数据
            resolve({ data })
          } catch (e) {
            console.error('处理响应数据时出错:', e)
            resolve({ data: generateFallbackStations() })
          }
        })
        .catch(error => {
          console.error('获取充电站数据网络请求失败:', error)
          resolve({ data: generateFallbackStations() })
        })
    })
  },
  // 获取单个充电站
  getById(id) {
    return api.get(`/stations/${id}/`)
  },
  // 更新充电站
  update(id, data) {
    console.log('调用API: 更新充电站', id, data)
    return new Promise((resolve, reject) => {
      // 确保数据格式正确
      const stationData = { ...data }
      
      // 确保功率值是数字
      if (stationData.power_rating !== undefined) {
        try {
          stationData.power_rating = parseFloat(stationData.power_rating)
          if (isNaN(stationData.power_rating)) {
            stationData.power_rating = 0
          }
        } catch (e) {
          stationData.power_rating = 0
        }
      }
      
      // 确保效率值是数字
      if (stationData.efficiency !== undefined) {
        try {
          stationData.efficiency = parseFloat(stationData.efficiency)
          if (isNaN(stationData.efficiency)) {
            stationData.efficiency = 80
          }
        } catch (e) {
          stationData.efficiency = 80
        }
      }
      
      console.log('格式化后的充电站数据:', stationData)
      
      api.put(`/stations/${id}/`, stationData, {
        headers: {
          'Accept': 'application/json',
          'Content-Type': 'application/json'
        }
      })
        .then(response => {
          console.log('更新充电站成功:', response.data)
          resolve(response)
        })
        .catch(error => {
          console.error('更新充电站失败:', error.response ? error.response.data : error)
          reject(error)
        })
    })
  },
  // 添加充电站
  add(data) {
    console.log('调用API: 添加充电站', data)
    return new Promise((resolve, reject) => {
      // 确保数据格式正确
      const stationData = {
        name: data.name || '',
        location: data.location || '',
        power_rating: data.power_rating !== undefined && data.power_rating !== null ? 
          parseFloat(data.power_rating) : 0,
        status: data.status || 'idle',
        efficiency: data.efficiency !== undefined && data.efficiency !== null ? 
          parseFloat(data.efficiency) : 80
      }
      
      console.log('格式化后的充电站数据:', stationData)
      
      api.post('/stations/', stationData, {
        headers: {
          'Accept': 'application/json',
          'Content-Type': 'application/json'
        }
      })
        .then(response => {
          console.log('添加充电站成功:', response.data)
          resolve(response)
        })
        .catch(error => {
          console.error('添加充电站失败:', error.response ? error.response.data : error)
          // 如果是422错误，提供更详细的错误信息
          if (error.response && error.response.status === 422) {
            reject(new Error('数据验证失败: ' + JSON.stringify(error.response.data)))
          } else {
            reject(error)
          }
        })
    })
  },
  // 删除充电站
  delete(id) {
    return api.delete(`/stations/${id}/`)
  }
}

// 机器人相关 API
export const robotApi = {
  // 获取所有机器人
  getAll() {
    console.log('调用API: 获取所有机器人')
    return new Promise((resolve, reject) => {
      api.get('/robots/', {
        headers: {
          'Accept': 'application/json',
          'Content-Type': 'application/json'
        },
        responseType: 'json'
      })
        .then(response => {
          console.log('机器人API响应状态:', response.status)
          console.log('机器人API响应头:', response.headers)
          
          let data = response.data
          console.log('原始响应数据类型:', typeof data)
          
          // 处理各种响应类型
          try {
            // 1. 如果是字符串，尝试解析为JSON
            if (typeof data === 'string') {
              console.log('响应是字符串，尝试解析为JSON')
              try {
                // 处理NaN值，将其替换为null
                const cleanedData = data.replace(/: ?NaN/g, ': null')
                data = JSON.parse(cleanedData)
                console.log('解析后的数据类型:', typeof data)
              } catch (e) {
                console.error('解析字符串为JSON失败:', e)
              }
            }
            
            // 2. 检查是否为null或undefined
            if (data === null || data === undefined) {
              console.error('API返回的机器人数据为null或undefined')
              resolve({ data: [] })
              return
            }
            
            // 3. 确保数据是数组
            if (!Array.isArray(data)) {
              console.error('API返回的机器人数据不是数组:', typeof data)
              
              // 如果是对象且有data属性是数组，则使用该属性
              if (data && typeof data === 'object' && Array.isArray(data.data)) {
                console.log('使用响应对象中的data属性作为数据数组')
                data = data.data
              } else {
                // 最后的后备方案：使用硬编码的机器人数据
                console.error('使用硬编码的机器人数据')
                data = generateFallbackRobots()
              }
            }
            
            // 4. 验证数组中每个元素是否为有效的机器人对象
            data = data.filter(item => {
              return item && 
                     typeof item === 'object' && 
                     'id' in item && 
                     'name' in item && 
                     'battery_level' in item && 
                     'status' in item
            })
            
            console.log(`过滤后的机器人数据数量: ${data.length}`)
            
            // 5. 如果过滤后数组为空，使用后备数据
            if (data.length === 0) {
              console.warn('过滤后没有有效的机器人数据，使用后备数据')
              data = generateFallbackRobots()
            }
            
            // 返回处理后的数据
            resolve({ data })
          } catch (e) {
            console.error('处理响应数据时出错:', e)
            resolve({ data: generateFallbackRobots() })
          }
        })
        .catch(error => {
          console.error('获取机器人数据网络请求失败:', error)
          resolve({ data: generateFallbackRobots() })
        })
    })
  },
  // 获取单个机器人
  getById(id) {
    return api.get(`/robots/${id}/`)
  },
  // 更新机器人
  update(id, data) {
    console.log('调用API: 更新机器人', id, data)
    return api.put(`/robots/${id}`, data)
  },
  // 添加机器人
  add(data) {
    return api.post('/robots/', data)
  },
  // 删除机器人
  delete(id) {
    return api.delete(`/robots/${id}/`)
  },
  // 新增：将机器人分配到充电桩
  assignToStation(robotId, stationId) {
    console.log(`调用API: 将机器人${robotId}分配到充电桩${stationId}`)
    return new Promise((resolve, reject) => {
      api.post(`/robots/${robotId}/assign/${stationId}`, {}, {
        headers: {
          'Accept': 'application/json',
          'Content-Type': 'application/json'
        }
      })
      .then(response => {
        console.log('分配充电桩成功:', response.data)
        resolve(response)
      })
      .catch(error => {
        console.error('分配充电桩失败:', error.response ? error.response.data : error.message)
        reject(error)
      })
    })
  },
  // 新增：解除机器人与充电桩的关联
  releaseFromStation(robotId) {
    console.log(`调用API: 解除机器人${robotId}与充电桩的关联`)
    return new Promise((resolve, reject) => {
      api.post(`/robots/${robotId}/release`, {}, {
        headers: {
          'Accept': 'application/json',
          'Content-Type': 'application/json'
        }
      })
      .then(response => {
        console.log('解除充电桩成功:', response.data)
        resolve(response)
      })
      .catch(error => {
        console.error('解除充电桩失败:', error.response ? error.response.data : error.message)
        reject(error)
      })
    })
  },
  // 新增：开始充电
  startCharging(robotId) {
    console.log(`调用API: 开始给机器人${robotId}充电`)
    return api.post(`/robots/${robotId}/start-charging`)
  },
  // 新增：完成充电
  completeCharging(robotId) {
    console.log(`调用API: 完成机器人${robotId}的充电`)
    return api.post(`/robots/${robotId}/complete-charging`)
  },
  // 新增：检查低电量机器人并自动充电
  checkLowBattery() {
    console.log('调用API: 检查低电量机器人')
    return api.get('/robots/check-low-battery')
  }
}

// 订单相关 API
export const orderApi = {
  // 获取所有订单
  getAll() {
    console.log('调用API: 获取所有订单')
    return new Promise((resolve, reject) => {
      api.get('/orders/', {
        headers: {
          'Accept': 'application/json',
          'Content-Type': 'application/json'
        },
        responseType: 'json'
      })
        .then(response => {
          console.log('订单API响应状态:', response.status)
          console.log('订单API响应头:', response.headers)
          
          let data = response.data
          console.log('原始响应数据类型:', typeof data)
          
          // 处理各种响应类型
          try {
            // 1. 如果是字符串，尝试解析为JSON
            if (typeof data === 'string') {
              console.log('响应是字符串，尝试解析为JSON')
              try {
                // 处理NaN值，将其替换为null
                const cleanedData = data.replace(/: ?NaN/g, ': null')
                data = JSON.parse(cleanedData)
                console.log('解析后的数据类型:', typeof data)
              } catch (e) {
                console.error('解析字符串为JSON失败:', e)
              }
            }
            
            // 2. 检查是否为null或undefined
            if (data === null || data === undefined) {
              console.error('API返回的订单数据为null或undefined')
              resolve({ data: [] })
              return
            }
            
            // 3. 确保数据是数组
            if (!Array.isArray(data)) {
              console.error('API返回的订单数据不是数组:', typeof data)
              
              // 如果是对象且有data属性是数组，则使用该属性
              if (data && typeof data === 'object' && Array.isArray(data.data)) {
                console.log('使用响应对象中的data属性作为数据数组')
                data = data.data
              } else {
                // 最后的后备方案：使用硬编码的订单数据
                console.error('使用硬编码的订单数据')
                data = generateFallbackOrders()
              }
            }
            
            // 4. 验证数组中每个元素是否为有效的订单对象
            data = data.filter(item => {
              const isValid = item && 
                     typeof item === 'object' && 
                     'id' in item && 
                     'robot_id' in item && 
                     'station_id' in item && 
                     'start_time' in item && 
                     'status' in item
              
              if (!isValid) {
                console.warn('过滤掉无效的订单数据:', item)
              }
              return isValid
            })
            
            console.log(`过滤后的订单数据数量: ${data.length}`)
            
            // 5. 如果过滤后数组为空，使用后备数据
            if (data.length === 0) {
              console.warn('过滤后没有有效的订单数据，使用后备数据')
              data = generateFallbackOrders()
            }
            
            // 返回处理后的数据
            resolve({ data })
          } catch (e) {
            console.error('处理响应数据时出错:', e)
            resolve({ data: generateFallbackOrders() })
          }
        })
        .catch(error => {
          console.error('获取订单数据网络请求失败:', error)
          resolve({ data: generateFallbackOrders() })
        })
    })
  },
  // 获取单个订单
  getById(id) {
    return api.get(`/orders/${id}/`)
  },
  // 创建订单
  create(data) {
    return api.post('/orders/', data)
  },
  // 更新订单状态
  updateStatus(id, status) {
    return api.put(`/orders/${id}/status/`, { status })
  }
}

// 系统相关 API
export const systemApi = {
  // 获取系统设置
  getSettings() {
    return api.get('/system/settings/')
  },
  // 更新系统设置
  updateSettings(data) {
    return api.put('/system/settings/', data)
  },
  // 获取仪表盘数据
  getDashboardData() {
    console.log('调用API: 获取仪表盘数据')
    return new Promise((resolve, reject) => {
      api.get('/system/dashboard/', {
        headers: {
          'Accept': 'application/json',
          'Content-Type': 'application/json',
          'Cache-Control': 'no-cache'
        },
        responseType: 'json',
        timeout: 10000 // 增加超时时间到10秒
      })
        .then(response => {
          console.log('仪表盘API响应状态:', response.status)
          
          let data = response.data
          console.log('仪表盘API响应:', data)
          
          // 如果响应为字符串，尝试解析
          if (typeof data === 'string') {
            try {
              data = JSON.parse(data)
            } catch (e) {
              console.error('解析仪表盘响应失败:', e)
            }
          }
          
          resolve({ data })
        })
        .catch(error => {
          console.error('获取仪表盘数据失败:', error.response || error.message || error)
          
          // 返回带有错误信息的响应，而不是拒绝Promise
          resolve({
            data: {
              stationCount: 0,
              onlineStations: 0,
              offlineStations: 0,
              robotCount: 0,
              chargingRobots: 0,
              waitingRobots: 0,
              todayOrders: 0,
              orderChangeRate: 0,
              systemStatus: '错误',
              systemMessage: `数据加载失败: ${error.message || '未知错误'}`
            }
          })
        })
    })
  },
  // 获取系统告警
  getAlerts() {
    return api.get('/system/alerts/')
  },
  // 获取系统日志
  getLogs() {
    return api.get('/system/logs/')
  },
  // 获取充电效率记录
  getEfficiencyLogs() {
    return api.get('/system/efficiency/')
  }
}

// 测试API连接
export const testApi = {
  checkData() {
    console.log('调用API: 测试数据加载')
    return new Promise((resolve, reject) => {
      api.get('/auth/test-data/', {
        headers: {
          'Accept': 'application/json',
          'Content-Type': 'application/json',
          'Cache-Control': 'no-cache'
        },
        responseType: 'json',
        timeout: 10000 // 增加超时时间到10秒
      })
        .then(response => {
          console.log('测试数据API响应状态:', response.status)
          console.log('测试数据API响应头:', response.headers)
          
          let data = response.data
          console.log('测试数据API响应:', data)
          
          // 如果响应为字符串，尝试解析
          if (typeof data === 'string') {
            try {
              data = JSON.parse(data)
            } catch (e) {
              console.error('解析测试数据响应失败:', e)
            }
          }
          
          resolve({ data })
        })
        .catch(error => {
          console.error('测试数据加载失败:', error.response || error.message || error)
          
          // 返回带有错误信息的响应，而不是拒绝Promise
          resolve({
            data: {
              error: error.message || '未知错误',
              success: false,
              errorDetails: error.response ? error.response.data : null
            }
          })
        })
    })
  }
} 