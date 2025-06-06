<template>
  <div class="orders-container">
    <h2>充电订单管理</h2>
    <el-card class="box-card">
      <div v-if="error" class="error-message">
        <el-alert
          title="加载数据出错"
          type="error"
          :description="error"
          show-icon
        />
      </div>
      <el-table 
        v-if="orders && orders.length > 0" 
        :data="paginatedOrders" 
        style="width: 100%" 
        v-loading="loading">
        <el-table-column prop="id" label="订单ID" width="180" />
        <el-table-column prop="robot_id" label="机器人ID" width="180" />
        <el-table-column prop="station_id" label="充电站ID" width="180" />
        <el-table-column prop="start_time" label="开始时间" />
        <el-table-column prop="end_time" label="结束时间" />
        <el-table-column prop="status" label="状态">
          <template #default="scope">
            <el-tag :type="getStatusType(scope.row.status)">
              {{ getStatusText(scope.row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="amount" label="充电量" />
      </el-table>
      <div v-else-if="!loading" class="no-data">
        <el-empty description="暂无数据" />
      </div>
      
      <!-- 分页控件 -->
      <div class="pagination-container" v-if="orders && orders.length > 0">
        <el-pagination
          v-model:current-page="currentPage"
          :page-size="pageSize"
          :total="totalItems"
          layout="total, prev, pager, next, jumper"
          @current-change="handleCurrentChange"
        />
      </div>
    </el-card>
  </div>
</template>

<script>
import { orderApi } from '@/api'
import { ElMessage } from 'element-plus'

export default {
  name: 'Orders',
  data() {
    return {
      orders: [],
      loading: false,
      error: null,
      // 分页相关
      currentPage: 1,
      pageSize: 10
    }
  },
  computed: {
    totalItems() {
      return this.orders.length
    },
    paginatedOrders() {
      const startIndex = (this.currentPage - 1) * this.pageSize
      const endIndex = startIndex + this.pageSize
      return this.orders.slice(startIndex, endIndex)
    }
  },
  created() {
    console.log('Orders组件已创建，准备获取数据')
    
    // 添加这个延迟调用以避免可能的ResizeObserver问题
    setTimeout(() => {
      this.fetchOrders()
    }, 0)
  },
  methods: {
    async fetchOrders() {
      try {
        this.loading = true
        this.error = null
        console.log('开始获取订单数据')
        
        try {
          const response = await orderApi.getAll()
          // 打印原始响应
          console.log('获取到订单数据(原始):', response)
          console.log('获取到订单数据:', response.data)
          console.log('订单数据类型:', typeof response.data, Array.isArray(response.data))
          
          // 确保数据是数组
          if (Array.isArray(response.data)) {
            // 检查每个订单对象的字段
            const validOrders = response.data.filter(order => {
              const isValid = order && 
                            typeof order === 'object' && 
                            'id' in order && 
                            'robot_id' in order && 
                            'station_id' in order && 
                            'start_time' in order && 
                            'status' in order;
              
              // 处理可能的NaN或undefined值
              if (isValid) {
                // 确保amount字段存在且为数字
                if (!('amount' in order) || order.amount === null || isNaN(order.amount)) {
                  order.amount = '-';
                }
                
                // 确保end_time字段存在
                if (!('end_time' in order) || order.end_time === null) {
                  order.end_time = '-';
                }
              } else {
                console.warn('过滤掉无效的订单数据:', order);
              }
              return isValid;
            });
            
            console.log('有效的订单数据:', validOrders);
            this.orders = validOrders;
            // 重置为第一页
            this.currentPage = 1;
            console.log('成功设置订单数据，数量:', this.orders.length)
          } else {
            console.error('API返回的订单数据不是数组:', response.data)
            this.orders = [] // 设置为空数组
            this.error = '订单数据格式错误，请联系管理员'
            ElMessage.error('订单数据格式错误')
          }
        } catch (apiError) {
          console.error('API调用出错:', apiError)
          this.orders = [] // 确保错误时也设置为空数组
          this.error = `API调用出错: ${apiError.message || '未知错误'}`
          ElMessage.error('获取订单数据失败')
        }
      } catch (error) {
        console.error('获取订单列表失败:', error)
        this.orders = [] // 确保错误时也设置为空数组
        this.error = `获取数据失败: ${error.message || '未知错误'}`
        ElMessage.error('获取订单列表失败')
      } finally {
        this.loading = false
      }
    },
    // 分页相关方法
    handleCurrentChange(page) {
      this.currentPage = page
      console.log(`当前页: ${this.currentPage}`)
    },
    getStatusType(status) {
      const types = {
        'charging': 'primary',
        'completed': 'success',
        'failed': 'danger'
      }
      return types[status] || 'info'
    },
    getStatusText(status) {
      const texts = {
        'charging': '充电中',
        'completed': '已完成',
        'failed': '失败'
      }
      return texts[status] || status
    }
  }
}
</script>

<style scoped>
.orders-container {
  padding: 20px;
}
.error-message {
  margin-bottom: 20px;
}
.no-data {
  padding: 20px 0;
}
.pagination-container {
  margin-top: 20px;
  display: flex;
  justify-content: center;
}
</style> 