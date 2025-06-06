<template>
  <div class="dashboard">
    <el-row :gutter="20">
      <el-col :span="6">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>充电桩总数</span>
            </div>
          </template>
          <div class="card-content" v-loading="loading">
            <h2>{{ dashboardData.stationCount || 0 }}</h2>
            <p>在线: {{ dashboardData.onlineStations || 0 }} | 离线: {{ dashboardData.offlineStations || 0 }}</p>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>机器人总数</span>
            </div>
          </template>
          <div class="card-content" v-loading="loading">
            <h2>{{ dashboardData.robotCount || 0 }}</h2>
            <p>充电中: {{ dashboardData.chargingRobots || 0 }} | 待充电: {{ dashboardData.waitingRobots || 0 }}</p>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>今日充电次数</span>
            </div>
          </template>
          <div class="card-content" v-loading="loading">
            <h2>{{ dashboardData.todayOrders || 0 }}</h2>
            <p>较昨日 {{ formatPercentage(dashboardData.orderChangeRate) }}</p>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>系统状态</span>
            </div>
          </template>
          <div class="card-content" v-loading="loading">
            <h2>{{ dashboardData.systemStatus || '加载中...' }}</h2>
            <p>{{ dashboardData.systemMessage || '' }}</p>
            <el-button 
              type="primary" 
              size="small" 
              @click="checkLowBattery" 
              :loading="checkingBattery"
              :disabled="checkingBattery"
              class="mt-10"
            >
              检查低电量机器人
            </el-button>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 自动充电结果提示 -->
    <el-row v-if="chargeResults && chargeResults.length > 0" :gutter="20" class="mt-20">
      <el-col :span="24">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>自动充电结果</span>
              <el-button type="danger" size="small" @click="clearChargeResults">关闭</el-button>
            </div>
          </template>
          <div class="charge-results">
            <el-alert
              v-for="(result, index) in chargeResults"
              :key="index"
              :title="result.message"
              :type="getAlertType(result.action)"
              :closable="false"
              class="mb-10"
              show-icon
            />
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" class="mt-20">
      <el-col :span="12">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>充电效率趋势</span>
            </div>
          </template>
          <div class="chart-container">
            <!-- 使用充电效率趋势图组件 -->
            <charging-efficiency-chart />
          </div>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>系统告警</span>
              <el-button type="primary" size="small" @click="refreshData">刷新</el-button>
            </div>
          </template>
          <div v-loading="alertsLoading">
            <el-table :data="alerts" style="width: 100%">
              <el-table-column prop="created_at" label="时间" width="180">
                <template #default="scope">
                  {{ formatDateTime(scope.row.created_at) }}
                </template>
              </el-table-column>
              <el-table-column prop="type" label="类型" width="120" />
              <el-table-column prop="message" label="告警信息" />
            </el-table>
            
            <!-- 添加分页组件 -->
            <div class="pagination-container">
              <el-pagination
                v-if="pagination.totalPages > 0"
                background
                layout="prev, pager, next"
                :total="pagination.totalItems"
                :page-size="pagination.perPage"
                :current-page="pagination.currentPage"
                @current-change="handlePageChange"
              />
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script>
import dashboardApi from '../api/dashboard';
import ChargingEfficiencyChart from '../components/ChargingEfficiencyChart.vue';

export default {
  name: 'Dashboard',
  components: {
    ChargingEfficiencyChart
  },
  data() {
    return {
      loading: false,
      alertsLoading: false,
      dashboardData: {
        stationCount: 0,
        onlineStations: 0,
        offlineStations: 0,
        robotCount: 0,
        chargingRobots: 0,
        waitingRobots: 0,
        todayOrders: 0,
        orderChangeRate: 0,
        systemStatus: '加载中...',
        systemMessage: '正在获取系统状态...'
      },
      alerts: [],
      pagination: {
        currentPage: 1,
        perPage: 7,
        totalPages: 0,
        totalItems: 0
      },
      refreshInterval: null,
      checkingBattery: false,
      chargeResults: []
    }
  },
  created() {
    this.fetchDashboardData();
    this.fetchAlerts();
    
    // 设置定时刷新 - 每60秒刷新一次数据
    this.refreshInterval = setInterval(() => {
      this.fetchDashboardData();
      this.fetchAlerts();
    }, 60000);
  },
  beforeUnmount() {
    // 组件销毁前清除定时器
    if (this.refreshInterval) {
      clearInterval(this.refreshInterval);
    }
  },
  methods: {
    async fetchDashboardData() {
      this.loading = true;
      try {
        const response = await dashboardApi.getDashboardOverview();
        this.dashboardData = response.data;
      } catch (error) {
        console.error('获取仪表盘数据失败:', error);
        this.$message.error('获取仪表盘数据失败');
      } finally {
        this.loading = false;
      }
    },
    async fetchAlerts(page = 1) {
      this.alertsLoading = true;
      try {
        const response = await dashboardApi.getSystemAlerts(page, this.pagination.perPage);
        
        // 更新告警数据
        this.alerts = response.data.items;
        
        // 更新分页信息
        this.pagination = {
          currentPage: response.data.pagination.current_page,
          perPage: response.data.pagination.per_page,
          totalPages: response.data.pagination.total_pages,
          totalItems: response.data.pagination.total_items
        };
      } catch (error) {
        console.error('获取系统告警失败:', error);
        this.$message.error('获取系统告警数据失败');
      } finally {
        this.alertsLoading = false;
      }
    },
    handlePageChange(page) {
      this.fetchAlerts(page);
    },
    refreshData() {
      this.fetchDashboardData();
      this.fetchAlerts(1); // 刷新时回到第一页
    },
    formatPercentage(value) {
      if (value === null || value === undefined) return '0%';
      const sign = value >= 0 ? '+' : '';
      return `${sign}${value}%`;
    },
    formatDateTime(dateTimeStr) {
      if (!dateTimeStr) return '';
      const date = new Date(dateTimeStr);
      return date.toLocaleString('zh-CN', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit'
      });
    },
    async checkLowBattery() {
      this.checkingBattery = true;
      try {
        const response = await dashboardApi.checkLowBatteryRobots();
        this.chargeResults = response.data;
      } catch (error) {
        console.error('检查低电量机器人失败:', error);
        this.$message.error('检查低电量机器人失败');
      } finally {
        this.checkingBattery = false;
      }
    },
    clearChargeResults() {
      this.chargeResults = [];
    },
    getAlertType(action) {
      // 根据action返回相应的类型
      switch (action) {
        case 'start_charging':
          return 'success';
        case 'assign_and_start_charging':
          return 'success';
        case 'charging_completed':
          return 'info';
        case 'no_idle_station':
          return 'warning';
        default:
          return 'info';
      }
    }
  }
}
</script>

<style scoped>
.dashboard {
  padding: 20px;
}

.mt-20 {
  margin-top: 20px;
}

.mt-10 {
  margin-top: 10px;
}

.mb-10 {
  margin-bottom: 10px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-content {
  text-align: center;
}

.card-content h2 {
  font-size: 24px;
  margin: 10px 0;
}

.card-content p {
  color: #666;
  margin: 0;
}

.chart-container {
  height: 300px;
}

.pagination-container {
  margin-top: 20px;
  display: flex;
  justify-content: center;
}

.charge-results {
  max-height: 300px;
  overflow-y: auto;
}
</style> 