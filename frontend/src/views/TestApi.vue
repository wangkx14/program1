<template>
  <div class="test-api-container">
    <h2>API 测试页面</h2>
    
    <el-card class="box-card" v-loading="loading">
      <template #header>
        <div class="card-header">
          <span>API 连接测试</span>
        </div>
      </template>
      
      <div class="button-group">
        <el-button type="success" @click="testStations">测试充电站API</el-button>
        <el-button type="info" @click="testRobots">测试机器人API</el-button>
        <el-button type="warning" @click="testOrders">测试订单API</el-button>
      </div>
      
      <div v-if="result" class="result-container">
        <h3>测试结果：</h3>
        <pre>{{ JSON.stringify(result, null, 2) }}</pre>
      </div>
      
      <div v-if="error" class="error-container">
        <h3>错误信息：</h3>
        <pre>{{ error }}</pre>
      </div>
    </el-card>
  </div>
</template>

<script>
import { stationApi, robotApi, orderApi } from '@/api'
import { ElMessage } from 'element-plus'

export default {
  name: 'TestApi',
  data() {
    return {
      loading: false,
      result: null,
      error: null
    }
  },
  methods: {
    async testStations() {
      try {
        this.loading = true
        this.result = null
        this.error = null
        
        console.log('测试充电站API')
        const response = await stationApi.getAll()
        this.result = response.data
        ElMessage.success('充电站API测试成功')
      } catch (error) {
        this.error = error.message || '未知错误'
        ElMessage.error('充电站API测试失败')
        console.error('测试充电站API出错:', error)
      } finally {
        this.loading = false
      }
    },
    
    async testRobots() {
      try {
        this.loading = true
        this.result = null
        this.error = null
        
        console.log('测试机器人API')
        const response = await robotApi.getAll()
        this.result = response.data
        ElMessage.success('机器人API测试成功')
      } catch (error) {
        this.error = error.message || '未知错误'
        ElMessage.error('机器人API测试失败')
        console.error('测试机器人API出错:', error)
      } finally {
        this.loading = false
      }
    },
    
    async testOrders() {
      try {
        this.loading = true
        this.result = null
        this.error = null
        
        console.log('测试订单API')
        const response = await orderApi.getAll()
        this.result = response.data
        ElMessage.success('订单API测试成功')
      } catch (error) {
        this.error = error.message || '未知错误'
        ElMessage.error('订单API测试失败')
        console.error('测试订单API出错:', error)
      } finally {
        this.loading = false
      }
    }
  }
}
</script>

<style scoped>
.test-api-container {
  padding: 20px;
}

.button-group {
  margin-bottom: 20px;
}

.button-group .el-button {
  margin-right: 10px;
  margin-bottom: 10px;
}

.result-container, .error-container {
  margin-top: 20px;
  padding: 10px;
  border-radius: 4px;
}

.result-container {
  background-color: #f0f9eb;
}

.error-container {
  background-color: #fef0f0;
}

pre {
  white-space: pre-wrap;
  word-wrap: break-word;
  background-color: #f5f5f5;
  padding: 10px;
  border-radius: 4px;
  max-height: 400px;
  overflow-y: auto;
}
</style> 