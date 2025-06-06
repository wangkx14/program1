<template>
  <div class="robots-container">
    <h2>机器人管理</h2>
    <el-card class="box-card">
      <div class="toolbar">
        <!-- <el-button type="primary" @click="checkLowBattery" :loading="checkingBattery">
          检查低电量机器人并自动充电
        </el-button> -->
        <el-button type="success" @click="fetchRobots" :loading="loading">
          刷新数据
        </el-button>
      </div>
      
      <div v-if="error" class="error-message">
        <el-alert
          title="加载数据出错"
          type="error"
          :description="error"
          show-icon
        />
      </div>
      
      <div v-if="chargeResults && chargeResults.length > 0" class="charge-results">
        <el-alert
          title="自动充电结果"
          type="success"
          :closable="true"
          show-icon
        >
          <div v-for="(result, index) in chargeResults" :key="index">
            {{ result.message }}
          </div>
        </el-alert>
      </div>
      
      <el-table 
        v-if="robots && robots.length > 0" 
        :data="paginatedRobots" 
        style="width: 100%" 
        v-loading="loading">
        <el-table-column prop="id" label="机器人ID" width="100" />
        <el-table-column prop="name" label="名称" width="150" />
        <el-table-column prop="battery_level" label="电量" width="180">
          <template #default="scope">
            <el-progress 
              :percentage="scope.row.battery_level" 
              :status="getBatteryStatus(scope.row.battery_level)"
            />
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="120">
          <template #default="scope">
            <el-tag :type="getStatusType(scope.row.status)">
              {{ getStatusText(scope.row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="station_id" label="关联充电桩" width="150">
          <template #default="scope">
            <span v-if="scope.row.station_id">
              {{ getStationName(scope.row.station_id) }}
            </span>
            <span v-else class="no-station">未分配</span>
          </template>
        </el-table-column>
        <el-table-column prop="last_charging" label="上次充电时间" />
        <el-table-column label="操作" width="240">
          <template #default="scope">
            <el-button 
              size="small" 
              type="primary" 
              @click="showAssignDialog(scope.row)"
              :disabled="scope.row.status === 'charging'"
              v-if="!scope.row.station_id"
            >
              分配充电桩
            </el-button>
            <el-button 
              size="small" 
              type="danger" 
              @click="releaseStation(scope.row)"
              v-if="scope.row.station_id"
            >
              解除充电桩
            </el-button>
          </template>
        </el-table-column>
      </el-table>
      <div v-else-if="!loading" class="no-data">
        <el-empty description="暂无数据" />
      </div>
      
      <!-- 分页控件 -->
      <div class="pagination-container" v-if="robots && robots.length > 0">
        <el-pagination
          v-model:current-page="currentPage"
          :page-size="pageSize"
          :total="totalItems"
          layout="total, prev, pager, next, jumper"
          @current-change="handleCurrentChange"
        />
      </div>
    </el-card>
    
    <!-- 分配充电桩对话框 -->
    <el-dialog 
      title="分配充电桩" 
      v-model="assignDialogVisible"
      width="500px"
    >
      <div v-if="loadingStations" class="dialog-loading">
        <el-skeleton :rows="3" animated />
      </div>
      <div v-else>
        <p>为机器人 <strong>{{ currentRobot?.name }}</strong> 选择一个充电桩:</p>
        
        <div v-if="availableStations.length === 0" class="no-stations-message">
          <el-alert
            title="没有可用的充电桩"
            type="warning"
            description="所有充电桩都在使用中或处于维护状态"
            show-icon
          />
        </div>
        
        <el-form v-else>
          <el-form-item>
            <el-select v-model="selectedStationId" placeholder="请选择充电桩" style="width: 100%">
              <el-option
                v-for="station in availableStations"
                :key="station.id"
                :label="`${station.name} (${station.location})`"
                :value="station.id"
              />
            </el-select>
          </el-form-item>
        </el-form>
      </div>
      
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="assignDialogVisible = false">取消</el-button>
          <el-button 
            type="primary" 
            @click="assignStation" 
            :disabled="!selectedStationId || assigningStation"
            :loading="assigningStation"
          >
            确定
          </el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script>
import { robotApi, stationApi } from '@/api'
import { ElMessage } from 'element-plus'

export default {
  name: 'Robots',
  data() {
    return {
      robots: [],
      stations: [],
      loading: false,
      error: null,
      // 分页相关
      currentPage: 1,
      pageSize: 10,
      // 分配充电桩相关
      assignDialogVisible: false,
      currentRobot: null,
      selectedStationId: null,
      loadingStations: false,
      assigningStation: false,
      // 低电量检查相关
      checkingBattery: false,
      chargeResults: []
    }
  },
  computed: {
    totalItems() {
      return this.robots.length
    },
    paginatedRobots() {
      const startIndex = (this.currentPage - 1) * this.pageSize
      const endIndex = startIndex + this.pageSize
      return this.robots.slice(startIndex, endIndex)
    },
    availableStations() {
      return this.stations.filter(station => station.status === 'idle')
    }
  },
  created() {
    console.log('Robots组件已创建，准备获取数据')
    
    // 添加这个延迟调用以避免可能的ResizeObserver问题
    setTimeout(() => {
      this.fetchRobots()
      this.fetchStations()
    }, 0)
  },
  methods: {
    async fetchRobots() {
      try {
        this.loading = true
        this.error = null
        console.log('开始获取机器人数据')
        
        try {
          const response = await robotApi.getAll()
          // 打印原始响应
          console.log('获取到机器人数据(原始):', response)
          console.log('获取到机器人数据:', response.data)
          console.log('机器人数据类型:', typeof response.data, Array.isArray(response.data))
          
          // 确保数据是数组
          if (Array.isArray(response.data)) {
            // 检查每个机器人对象的字段
            const validRobots = response.data.filter(robot => {
              const isValid = robot && 
                             typeof robot === 'object' && 
                             'id' in robot && 
                             'name' in robot && 
                             'battery_level' in robot && 
                             'status' in robot;
              if (!isValid) {
                console.warn('过滤掉无效的机器人数据:', robot);
              }
              return isValid;
            });
            
            console.log('有效的机器人数据:', validRobots);
            this.robots = validRobots;
            // 重置为第一页
            this.currentPage = 1;
            console.log('成功设置机器人数据，数量:', this.robots.length)
          } else {
            console.error('API返回的机器人数据不是数组:', response.data)
            this.robots = [] // 设置为空数组
            this.error = '机器人数据格式错误，请联系管理员'
            ElMessage.error('机器人数据格式错误')
          }
        } catch (apiError) {
          console.error('API调用出错:', apiError)
          this.robots = [] // 确保错误时也设置为空数组
          this.error = `API调用出错: ${apiError.message || '未知错误'}`
          ElMessage.error('获取机器人数据失败')
        }
      } catch (error) {
        console.error('获取机器人列表失败:', error)
        this.robots = [] // 确保错误时也设置为空数组
        this.error = `获取数据失败: ${error.message || '未知错误'}`
        ElMessage.error('获取机器人列表失败')
      } finally {
        this.loading = false
      }
    },
    
    async fetchStations() {
      try {
        this.loadingStations = true
        console.log('开始获取充电站数据')
        
        const response = await stationApi.getAll()
        console.log('获取到充电站数据:', response.data)
        
        if (Array.isArray(response.data)) {
          this.stations = response.data
          console.log('成功设置充电站数据，数量:', this.stations.length)
        } else {
          console.error('API返回的充电站数据不是数组')
          this.stations = []
        }
      } catch (error) {
        console.error('获取充电站列表失败:', error)
        this.stations = []
        ElMessage.error('获取充电站数据失败')
      } finally {
        this.loadingStations = false
      }
    },
    
    // 检查低电量机器人并自动充电
    async checkLowBattery() {
      try {
        this.checkingBattery = true
        this.chargeResults = []
        
        console.log('开始检查低电量机器人')
        const response = await robotApi.checkLowBattery()
        console.log('检查结果:', response.data)
        
        if (Array.isArray(response.data) && response.data.length > 0) {
          this.chargeResults = response.data
          ElMessage.success(`检测到 ${response.data.length} 个需要处理的机器人`)
        } else {
          ElMessage.info('没有需要充电的机器人')
        }
        
        // 刷新机器人数据
        await this.fetchRobots()
      } catch (error) {
        console.error('检查低电量机器人失败:', error)
        ElMessage.error('检查低电量机器人失败')
      } finally {
        this.checkingBattery = false
      }
    },
    
    // 显示分配充电桩对话框
    showAssignDialog(robot) {
      this.currentRobot = robot
      this.selectedStationId = robot.station_id || null
      this.assignDialogVisible = true
      
      // 如果充电站数据为空，重新获取
      if (this.stations.length === 0) {
        this.fetchStations()
      }
    },
    
    // 分配充电桩
    async assignStation() {
      if (!this.currentRobot || !this.selectedStationId) {
        ElMessage.warning('请选择充电桩')
        return
      }
      
      try {
        this.assigningStation = true
        console.log(`分配机器人 ${this.currentRobot.id} 到充电桩 ${this.selectedStationId}`)
        
        const response = await robotApi.assignToStation(this.currentRobot.id, this.selectedStationId)
        
        if (response && response.data && response.data.message) {
          ElMessage.success(response.data.message || '成功分配充电桩')
        } else {
          ElMessage.success('成功分配充电桩')
        }
        
        this.assignDialogVisible = false
        
        // 刷新机器人数据
        await this.fetchRobots()
        // 刷新充电站数据
        await this.fetchStations()
      } catch (error) {
        console.error('分配充电桩失败:', error)
        // 提取API返回的具体错误信息
        let errorMsg = '未知错误'
        if (error.response && error.response.data) {
          errorMsg = error.response.data.error || error.response.data.message || error.message || '分配失败'
        } else if (error.message) {
          errorMsg = error.message
        }
        ElMessage.error('分配充电桩失败: ' + errorMsg)
      } finally {
        this.assigningStation = false
      }
    },
    
    // 获取充电桩名称
    getStationName(stationId) {
      const station = this.stations.find(s => s.id === stationId)
      return station ? station.name : `充电桩 ${stationId}`
    },
    
    // 分页相关方法
    handleCurrentChange(page) {
      this.currentPage = page
      console.log(`当前页: ${this.currentPage}`)
    },
    
    // 获取电池状态
    getBatteryStatus(level) {
      if (level < 20) return 'exception'
      if (level < 50) return 'warning'
      return 'success'
    },
    
    getStatusType(status) {
      const types = {
        'idle': 'info',
        'working': 'success',
        'charging': 'primary',
        'error': 'danger'
      }
      return types[status] || 'info'
    },
    
    getStatusText(status) {
      const texts = {
        'idle': '空闲',
        'working': '工作中',
        'charging': '充电中',
        'error': '故障'
      }
      return texts[status] || status
    },
    
    // 解除充电桩
    async releaseStation(robot) {
      try {
        this.assigningStation = true
        console.log(`解除机器人 ${robot.id} 的充电桩`)
        
        const response = await robotApi.releaseFromStation(robot.id)
        
        if (response && response.data && response.data.message) {
          ElMessage.success(response.data.message || '成功解除充电桩')
        } else {
          ElMessage.success('成功解除充电桩')
        }
        
        // 刷新机器人数据
        await this.fetchRobots()
        // 刷新充电站数据
        await this.fetchStations()
      } catch (error) {
        console.error('解除充电桩失败:', error)
        // 提取API返回的具体错误信息
        let errorMsg = '未知错误'
        if (error.response && error.response.data) {
          errorMsg = error.response.data.error || error.response.data.message || error.message || '解除失败'
        } else if (error.message) {
          errorMsg = error.message
        }
        ElMessage.error('解除充电桩失败: ' + errorMsg)
      } finally {
        this.assigningStation = false
      }
    }
  }
}
</script>

<style scoped>
.robots-container {
  padding: 20px;
}
.error-message, .charge-results {
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
.toolbar {
  margin-bottom: 20px;
  display: flex;
  gap: 10px;
}
.no-station {
  color: #909399;
  font-style: italic;
}
.dialog-loading {
  padding: 20px 0;
}
.no-stations-message {
  margin: 20px 0;
}
</style> 