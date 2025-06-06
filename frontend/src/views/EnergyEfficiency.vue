<template>
  <div class="energy-efficiency-analysis">
    <!-- KPI指标卡片标题 -->
    <div class="section-title">
      <h2>核心性能指标</h2>
      <div class="section-subtitle">30天内充电系统性能概览</div>
    </div>
    
    <!-- KPI指标卡片 -->
    <el-row :gutter="30" class="kpi-container">
      <el-col :xs="12" :sm="8" :md="6" :lg="4" v-for="(kpi, index) in kpiData" :key="index">
        <el-card class="kpi-card" shadow="hover">
          <div class="kpi-title">
            <el-tooltip 
              :content="kpi.title" 
              placement="top"
              effect="light">
              <span class="title-text">{{ kpi.title }}</span>
            </el-tooltip>
            <el-tooltip 
              :content="getKpiDescription(index)" 
              placement="top"
              effect="light">
              <el-icon class="info-icon"><InfoFilled /></el-icon>
            </el-tooltip>
          </div>
          <div class="kpi-value">
            <span class="value-number">{{ kpi.value }}</span><span class="value-unit">{{ kpi.unit }}</span>
          </div>
          <el-tooltip 
            :content="`与上一时段相比${kpi.trend === 'up' ? '增长' : '下降'}了${kpi.change}%`" 
            placement="bottom"
            effect="light">
            <div class="kpi-change" :class="kpi.trend">
              <el-icon v-if="kpi.trend === 'up'"><ArrowUp /></el-icon>
              <el-icon v-else><ArrowDown /></el-icon>
              {{ kpi.change }}%
            </div>
          </el-tooltip>
        </el-card>
      </el-col>
    </el-row>

    <!-- 分析图表区域标题 -->
    <div class="section-title">
      <h2>详细分析图表</h2>
      <div class="section-subtitle">充电系统各维度分析数据</div>
    </div>

    <!-- 分析图表区域 -->
    <el-card class="chart-container" shadow="hover">
      <div class="chart-header">
        <h3>{{ currentChartTitle }}</h3>
        <el-radio-group v-model="currentChart" @change="handleChartChange">
          <el-radio-button :value="'efficiency'">充电效率趋势</el-radio-button>
          <el-radio-button :value="'consumption'">能耗分布</el-radio-button>
          <el-radio-button :value="'utilization'">充电站利用率</el-radio-button>
          <el-radio-button :value="'robot'">机器人充电分析</el-radio-button>
          <el-radio-button :value="'peak'">充电高峰期</el-radio-button>
        </el-radio-group>
      </div>
      <div class="chart-content">
        <!-- 不同图表的容器 -->
        <div v-show="currentChart === 'efficiency'" class="chart-item">
          <div ref="efficiencyChart" class="chart"></div>
        </div>
        <div v-show="currentChart === 'consumption'" class="chart-item">
          <div ref="consumptionChart" class="chart"></div>
        </div>
        <div v-show="currentChart === 'utilization'" class="chart-item">
          <div ref="utilizationChart" class="chart"></div>
        </div>
        <div v-show="currentChart === 'robot'" class="chart-item">
          <div ref="robotChart" class="chart"></div>
        </div>
        <div v-show="currentChart === 'peak'" class="chart-item">
          <div ref="peakChart" class="chart"></div>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script>
import * as echarts from 'echarts';
import energyEfficiencyApi from '@/api/energyEfficiency';
import { formatDateTime, calculateDuration } from '@/utils/dateTime';
import { ArrowUp, ArrowDown, InfoFilled } from '@element-plus/icons-vue';

export default {
  name: 'EnergyEfficiencyAnalysis',
  components: {
    ArrowUp,
    ArrowDown,
    InfoFilled
  },
  data() {
    return {
      // 固定的默认筛选条件（不再显示在UI上）
      dateRange: [new Date(new Date().getTime() - 30 * 24 * 60 * 60 * 1000), new Date()],
      selectedStations: [],
      selectedRobots: [],
      
      // 数据列表
      stations: [],
      robots: [],
      
      // 图表相关
      currentChart: 'efficiency',
      currentChartTitle: '充电效率趋势分析',
      charts: {
        efficiency: null,
        consumption: null,
        utilization: null,
        robot: null,
        peak: null
      },
      
      // KPI数据
      kpiData: [
        { title: '平均充电效率', value: 0, unit: '%', change: 0, trend: 'up' },
        { title: '总能耗', value: 0, unit: 'kWh', change: 0, trend: 'up' },
        { title: '充电器利用率', value: 0, unit: '%', change: 0, trend: 'up' },
        { title: '平均等待时间', value: 0, unit: 'min', change: 0, trend: 'down' },
        { title: '充电成功率', value: 0, unit: '%', change: 0, trend: 'up' },
        { title: '总充电次数', value: 0, unit: '次', change: 0, trend: 'up' }
      ]
    };
  },
  
  mounted() {
    this.initData();
    
    // 添加窗口resize监听器，确保图表大小适应窗口变化
    window.addEventListener('resize', this.handleResize);
    
    // 监听充电站数据变化事件
    try {
      if (this.$root && this.$root.$on) {
        this.$root.$on('station-data-changed', this.handleStationDataChanged);
        // 监听充电站即将删除的事件，提前清理资源
        this.$root.$on('station-pre-delete', this.handleStationPreDelete);
        // 监听强制刷新图表的事件
        this.$root.$on('force-refresh-charts', this.forceRefreshCharts);
      }
    } catch (e) {
      console.error('注册全局事件监听失败:', e);
    }
  },
  
  beforeUnmount() {
    // 先清理所有图表资源
    this.disposeAllCharts();
    
    // 清空所有DOM引用
    try {
      if (this.$refs.efficiencyChart) this.$refs.efficiencyChart.innerHTML = '';
      if (this.$refs.consumptionChart) this.$refs.consumptionChart.innerHTML = '';
      if (this.$refs.utilizationChart) this.$refs.utilizationChart.innerHTML = '';
      if (this.$refs.robotChart) this.$refs.robotChart.innerHTML = '';
      if (this.$refs.peakChart) this.$refs.peakChart.innerHTML = '';
    } catch (error) {
      console.error('清理图表DOM引用失败:', error);
    }
    
    // 移除resize监听器
    window.removeEventListener('resize', this.handleResize);
    
    // 移除充电站数据变化事件监听
    try {
      if (this.$root && this.$root.$off) {
        this.$root.$off('station-data-changed', this.handleStationDataChanged);
        this.$root.$off('station-pre-delete', this.handleStationPreDelete);
        this.$root.$off('force-refresh-charts', this.forceRefreshCharts);
      }
    } catch (e) {
      console.error('移除全局事件监听失败:', e);
    }
  },
  
  methods: {
    // 强制刷新所有图表
    forceRefreshCharts() {
      console.log('接收到强制刷新图表的请求');
      // 先清理所有现有图表
      this.disposeAllCharts();
      
      // 清空DOM内容
      try {
        if (this.$refs.efficiencyChart) this.$refs.efficiencyChart.innerHTML = '';
        if (this.$refs.consumptionChart) this.$refs.consumptionChart.innerHTML = '';
        if (this.$refs.utilizationChart) this.$refs.utilizationChart.innerHTML = '';
        if (this.$refs.robotChart) this.$refs.robotChart.innerHTML = '';
        if (this.$refs.peakChart) this.$refs.peakChart.innerHTML = '';
      } catch (error) {
        console.error('清理图表DOM引用失败:', error);
      }
      
      // 等待DOM更新后重新初始化
      this.$nextTick(() => {
        // 重新获取数据并渲染当前选中的图表
        this.fetchChartData();
      });
    },
    
    // 处理充电站即将删除的事件
    handleStationPreDelete(stationId) {
      console.log(`充电站 ${stationId} 即将被删除，提前清理资源`);
      // 立即清理所有图表实例
      this.disposeAllCharts();
      
      // 清空DOM内容，确保没有悬挂的观察者
      try {
        if (this.$refs.efficiencyChart) this.$refs.efficiencyChart.innerHTML = '';
        if (this.$refs.consumptionChart) this.$refs.consumptionChart.innerHTML = '';
        if (this.$refs.utilizationChart) this.$refs.utilizationChart.innerHTML = '';
        if (this.$refs.robotChart) this.$refs.robotChart.innerHTML = '';
        if (this.$refs.peakChart) this.$refs.peakChart.innerHTML = '';
      } catch (error) {
        console.error('清理图表DOM引用失败:', error);
      }
    },
    
    // 处理充电站数据变化事件
    handleStationDataChanged() {
      console.log('检测到充电站数据变化，刷新图表');
      // 先清理所有图表实例
      this.disposeAllCharts();
      // 然后重新获取数据并渲染
      this.$nextTick(() => {
        this.initData();
      });
    },
    
    // 处理窗口调整大小事件
    handleResize() {
      // 调整所有已创建的图表
      Object.keys(this.charts).forEach(key => {
        if (this.charts[key]) {
          try {
            this.charts[key].resize();
          } catch (error) {
            console.error(`调整图表 ${key} 大小失败:`, error);
            // 如果调整大小失败，尝试销毁图表以避免进一步的错误
            try {
              this.charts[key].dispose();
              this.charts[key] = null;
            } catch (disposeError) {
              console.error(`销毁图表 ${key} 失败:`, disposeError);
            }
          }
        }
      });
    },
    
    // 销毁所有图表实例
    disposeAllCharts() {
      Object.keys(this.charts).forEach(key => {
        if (this.charts[key]) {
          try {
            // 移除所有事件监听器
            this.charts[key].off('click');
            this.charts[key].off('resize');
            // 销毁图表实例
            this.charts[key].dispose();
            this.charts[key] = null;
          } catch (error) {
            console.error(`销毁图表 ${key} 失败:`, error);
          }
        }
      });
      
      // 清理所有的DOM引用
      try {
        // 如果引用存在，则清空相关DOM元素内容
        if (this.$refs.efficiencyChart) this.$refs.efficiencyChart.innerHTML = '';
        if (this.$refs.consumptionChart) this.$refs.consumptionChart.innerHTML = '';
        if (this.$refs.utilizationChart) this.$refs.utilizationChart.innerHTML = '';
        if (this.$refs.robotChart) this.$refs.robotChart.innerHTML = '';
        if (this.$refs.peakChart) this.$refs.peakChart.innerHTML = '';
      } catch (error) {
        console.error('清理图表DOM引用失败:', error);
      }
      
      // 强制执行一次垃圾回收
      try {
        if (window.gc) window.gc();
      } catch (e) {
        // 大多数浏览器不支持直接调用gc，忽略错误
      }
    },
    
    async initData() {
      try {
        // 获取充电站列表
        const stationsResponse = await energyEfficiencyApi.getStations();
        this.stations = stationsResponse.data;
        
        // 获取机器人列表
        const robotsResponse = await energyEfficiencyApi.getRobots();
        this.robots = robotsResponse.data;
        
        // 获取初始数据
        this.fetchKpiData();
        this.fetchChartData();
      } catch (error) {
        console.error('初始化数据失败:', error);
        this.$message.error('加载数据失败，请重试');
      }
    },
    
    // 刷新所有数据
    refreshData() {
      this.fetchKpiData();
      this.fetchChartData();
    },
    
    // 获取KPI数据
    async fetchKpiData() {
      try {
        const params = this.getFilterParams();
        const response = await energyEfficiencyApi.getKpiData(params);
        
        // 格式化能耗值，根据大小选择合适的单位
        const formatEnergy = (value) => {
          if (value < 1) {
            return { value: (value * 1000).toFixed(0), unit: 'Wh' };
          } else if (value >= 1 && value < 1000) {
            return { value: value.toFixed(2), unit: 'kWh' };
          } else {
            return { value: (value / 1000).toFixed(2), unit: 'MWh' };
          }
        };
        
        // 格式化时间，大于60分钟转为小时和分钟
        const formatTime = (minutes) => {
          if (minutes < 60) {
            return { value: minutes.toFixed(0), unit: 'min' };
          } else {
            const hours = Math.floor(minutes / 60);
            const mins = Math.round(minutes % 60);
            return { value: `${hours}h ${mins}`, unit: 'min' };
          }
        };
        
        // 格式化次数，大于1000次使用k单位
        const formatCount = (count) => {
          if (count < 1000) {
            return { value: count, unit: '次' };
          } else {
            return { value: (count / 1000).toFixed(1), unit: 'k次' };
          }
        };
        
        // 格式化变化率，统一显示格式
        const formatChangeRate = (rate) => {
          // 对极端值进行处理
          if (!rate && rate !== 0) return "0.00";
          if (!isFinite(rate)) return "0.00";
          
          // 对变化率进行合理限制，避免极端值
          let limitedRate = rate;
          if (Math.abs(limitedRate) > 1000) {
            limitedRate = (limitedRate > 0) ? 999.99 : -999.99;
          }
          
          // 统一保留2位小数
          return limitedRate.toFixed(2);
        };
        
        // 格式化充电器利用率，确保显示合理
        const formatUtilization = (value) => {
          // 如果利用率异常大，通常是因为计算错误，将其限制在合理范围内
          if (value > 1000) {
            return { value: (value / 100).toFixed(2), unit: '%' };
          } else {
            return { value: value.toFixed(2), unit: '%' };
          }
        };
        
        // 获取能耗值和单位
        const energyData = formatEnergy(response.data.totalEnergy);
        // 获取等待时间值和单位
        const waitTimeData = formatTime(response.data.avgWaitTime);
        // 获取充电次数值和单位
        const ordersData = formatCount(response.data.totalOrders || 0);
        // 获取充电器利用率值和单位
        const utilizationData = formatUtilization(response.data.utilization);
        
        this.kpiData = [
          { 
            title: '平均充电效率', 
            value: response.data.avgEfficiency.toFixed(2), 
            unit: '%', 
            change: formatChangeRate(response.data.efficiencyChange),
            trend: response.data.efficiencyChange >= 0 ? 'up' : 'down' 
          },
          { 
            title: '总能耗', 
            value: energyData.value, 
            unit: energyData.unit, 
            change: formatChangeRate(response.data.energyChange),
            trend: response.data.energyChange >= 0 ? 'up' : 'down' 
          },
          { 
            title: '充电器利用率', 
            value: utilizationData.value, 
            unit: utilizationData.unit, 
            change: formatChangeRate(response.data.utilizationChange),
            trend: response.data.utilizationChange >= 0 ? 'up' : 'down' 
          },
          { 
            title: '平均等待时间', 
            value: waitTimeData.value, 
            unit: waitTimeData.unit, 
            change: formatChangeRate(response.data.waitTimeChange),
            trend: response.data.waitTimeChange >= 0 ? 'up' : 'down' 
          },
          { 
            title: '充电成功率', 
            value: response.data.successRate.toFixed(2), 
            unit: '%', 
            change: formatChangeRate(response.data.successRateChange),
            trend: response.data.successRateChange >= 0 ? 'up' : 'down' 
          },
          { 
            title: '总充电次数', 
            value: ordersData.value, 
            unit: ordersData.unit, 
            change: formatChangeRate(response.data.ordersChange || 0),
            trend: (response.data.ordersChange || 0) >= 0 ? 'up' : 'down' 
          }
        ];
      } catch (error) {
        console.error('获取KPI数据失败:', error);
        this.$message.error('获取KPI数据失败');
      }
    },
    
    // 获取图表数据并渲染
    async fetchChartData() {
      try {
        const params = this.getFilterParams();
        
        // 根据当前选择的图表类型获取数据
        switch (this.currentChart) {
          case 'efficiency':
            await this.renderEfficiencyChart(params);
            break;
          case 'consumption':
            await this.renderConsumptionChart(params);
            break;
          case 'utilization':
            await this.renderUtilizationChart(params);
            break;
          case 'robot':
            await this.renderRobotChart(params);
            break;
          case 'peak':
            await this.renderPeakChart(params);
            break;
        }
      } catch (error) {
        console.error('获取图表数据失败:', error);
        this.$message.error('获取图表数据失败');
        
        // 清理错误的图表实例
        const chartKey = this.currentChart;
        if (this.charts[chartKey]) {
          try {
            this.charts[chartKey].dispose();
            this.charts[chartKey] = null;
          } catch (cleanupError) {
            console.error(`清理图表失败: ${cleanupError}`);
          }
        }
      }
    },
    
    // 充电效率趋势图
    async renderEfficiencyChart(params) {
      try {
        const response = await energyEfficiencyApi.getEfficiencyTrend(params);
        
        // 检查返回的数据
        if (!response.data || !response.data.stations || !response.data.timeline) {
          console.error('效率趋势数据异常:', response.data);
          const chart = await this.safeInitChart('efficiencyChart', 'efficiency');
          if (chart) {
            chart.setOption({
              title: {
                text: '充电效率趋势分析 (暂无数据)',
                left: 'center'
              }
            });
          }
          return;
        }
        
        // 安全创建图表
        const chart = await this.safeInitChart('efficiencyChart', 'efficiency');
        if (!chart) return;
      
        const option = {
          title: {
            text: '充电效率趋势分析',
            left: 'center',
            top: '10px'
          },
          tooltip: {
            trigger: 'axis'
          },
          legend: {
            data: response.data.stations.map(station => station.name),
            selected: response.data.stations.reduce((acc, station) => {
              acc[station.name] = true;
              return acc;
            }, {}),
            top: '40px',
            type: 'scroll',
            orient: 'horizontal',
            selectedMode: false
          },
          grid: {
            left: '3%',
            right: '4%',
            bottom: '3%',
            top: '100px',
            containLabel: true
          },
          xAxis: {
            type: 'category',
            boundaryGap: false,
            data: response.data.timeline
          },
          yAxis: {
            type: 'value',
            name: '充电效率 (%)',
            min: 50,
            max: 100
          },
          series: response.data.stations.map(station => ({
            name: station.name,
            type: 'line',
            data: station.efficiencyData,
            smooth: true
          }))
        };
        
        chart.setOption(option);
        
        // 取消图表的点击事件
        chart.off('click');
      } catch (error) {
        console.error('渲染效率趋势图失败:', error);
        
        // 错误情况下，显示错误信息
        try {
          const chart = await this.safeInitChart('efficiencyChart', 'efficiency');
          if (chart) {
            chart.setOption({
              title: {
                text: '充电效率趋势分析 (加载失败)',
                textStyle: { color: '#ff0000' },
                left: 'center'
              }
            });
          }
        } catch (e) {
          console.error('显示错误信息失败:', e);
        }
      }
    },
    
    // 能耗分布热力图
    async renderConsumptionChart(params) {
      try {
        console.log('获取能耗分布数据，参数:', params);
        const response = await energyEfficiencyApi.getEnergyConsumptionDistribution(params);
        console.log('能耗分布数据响应:', response.data);
        
        // 检查返回的数据
        if (!response.data || !response.data.days || !response.data.data) {
          console.error('能耗分布数据异常:', response.data);
          const chart = await this.safeInitChart('consumptionChart', 'consumption');
          if (chart) {
            chart.setOption({
              title: {
                text: '能耗分布热力图 (暂无数据)',
                left: 'center'
              }
            });
          }
          return;
        }
        
        // 检查数据是否为空数组
        if (response.data.days.length === 0 || response.data.data.length === 0) {
          console.warn('能耗分布数据为空');
          const chart = await this.safeInitChart('consumptionChart', 'consumption');
          if (chart) {
            chart.setOption({
              title: {
                text: '能耗分布热力图 (暂无数据)',
                left: 'center'
              }
            });
          }
          return;
        }
        
        console.log('能耗分布数据:', response.data.data);
        
        // 安全创建图表
        const consumptionChart = await this.safeInitChart('consumptionChart', 'consumption');
        if (!consumptionChart) return;
        
        // 设置容器尺寸
        if (this.$refs.consumptionChart) {
          this.$refs.consumptionChart.style.width = '100%';
          this.$refs.consumptionChart.style.height = '500px';
          
          // 调整图表大小以适应容器
          consumptionChart.resize();
        }
        
        // 直接使用后端返回的日期作为Y轴
        const days = response.data.days;
        
        // 提取所有小时作为X轴（0-23）
        const hours = [];
        for (let i = 0; i < 24; i++) {
          hours.push(i.toString());
        }
        
        // 将API返回的数据转换为ECharts需要的格式 [x索引, y索引, 值]
        const formattedData = [];
        
        // 找出数据中的最小值和最大值，用于设置图例刻度
        let minValue = Infinity;
        let maxValue = 0;
        
        if (Array.isArray(response.data.data)) {
          response.data.data.forEach(item => {
            if (Array.isArray(item) && item.length === 3) {
              const day = item[0];
              const hour = parseInt(item[1]);
              const value = parseFloat(item[2] || 0);
              
              // 更新最小值和最大值
              if (!isNaN(value)) {
                minValue = Math.min(minValue, value);
                maxValue = Math.max(maxValue, value);
              }
              
              // 确保值是有效的数字
              if (!isNaN(value) && hour >= 0 && hour < 24) {
                // 找到日期在Y轴中的索引
                const dayIndex = days.indexOf(day);
                
                // 只有当日期在Y轴中存在时才添加数据点
                if (dayIndex !== -1) {
                  formattedData.push([hour, dayIndex, value]);
                }
              }
            }
          });
        } else {
          console.error('能耗数据不是数组格式');
          // 创建默认数据以避免图表崩溃
          for (let dayIndex = 0; dayIndex < days.length; dayIndex++) {
            for (let hour = 0; hour < 24; hour++) {
              formattedData.push([hour, dayIndex, 0]);
            }
          }
        }
        
        console.log('格式化后的数据点数:', formattedData.length);
        console.log('数据范围:', minValue, '至', maxValue);
        
        // 如果没有有效数据，设置默认值避免图表错误
        if (formattedData.length === 0 || minValue === Infinity) {
          minValue = 0;
          maxValue = 100;
        }
        
        // 使用后端返回的最大值或计算得到的最大值
        const visualMaxValue = response.data.maxValue || Math.ceil(maxValue) || 100;
        
        // 创建均匀分布的刻度值数组
        const pieces = [];
        const stepCount = 10; // 分成10个刻度
        const step = visualMaxValue / stepCount;
        
        for (let i = 0; i < stepCount; i++) {
          const startValue = i * step;
          const endValue = (i + 1) * step;
          pieces.push({
            min: startValue,
            max: endValue,
            label: `${startValue.toFixed(0)}-${endValue.toFixed(0)}`
          });
        }
        
        // 使用简单的配置
        const option = {
          title: {
            text: '能耗分布热力图',
            left: 'center'
          },
          tooltip: {
            position: 'top',
            formatter: function (params) {
              const hour = params.data[0];
              const day = days[params.data[1]];
              const value = params.data[2];
              return `${hour}:00 - ${(parseInt(hour) + 1) % 24}:00<br>日期: ${day}<br>能耗: ${value.toFixed(2)} kWh`;
            }
          },
          grid: {
            height: '70%',
            top: '60px',
            left: '80px',
            right: '30px',
            containLabel: true
          },
          xAxis: {
            type: 'category',
            data: hours,
            axisLabel: {
              formatter: '{value}:00',
              interval: function (index, value) {
                // 每2小时显示一个标签
                return index % 2 === 0;
              }
            }
          },
          yAxis: {
            type: 'category',
            data: days,
            axisLabel: {
              formatter: function (value) {
                const parts = value.split('-');
                return parts[1] + '-' + parts[2]; // 只显示月-日
              }
            }
          },
          visualMap: {
            type: 'continuous',
            min: 0,
            max: visualMaxValue,
            precision: 0,
            calculable: true,
            orient: 'horizontal',
            left: 'center',
            bottom: '5%',
            inRange: {
              color: ['#313695', '#4575b4', '#74add1', '#abd9e9', '#e0f3f8', '#ffffbf', '#fee090', '#fdae61', '#f46d43', '#d73027', '#a50026']
            },
            // 添加具体的数字刻度
            splitNumber: 10, // 分割段数
            formatter: function (value) {
              return value.toFixed(0) + ' kWh';
            },
            textStyle: {
              color: '#333'
            }
          },
          series: [
            {
              name: '能耗 (kWh)',
              type: 'heatmap',
              data: formattedData,
              emphasis: {
                itemStyle: {
                  shadowBlur: 10,
                  shadowColor: 'rgba(0, 0, 0, 0.5)'
                }
              }
            }
          ]
        };
        
        // 应用配置并渲染
        consumptionChart.setOption(option);
        console.log('热力图渲染成功');
        
        // 取消图表的点击事件
        consumptionChart.off('click');
      } catch (error) {
        console.error('渲染能耗分布热力图失败:', error);
        
        // 尝试显示错误信息
        try {
          const chart = await this.safeInitChart('consumptionChart', 'consumption');
          if (chart) {
            chart.setOption({
              title: {
                text: '能耗分布热力图 (加载失败)',
                textStyle: { color: '#ff0000' },
                left: 'center'
              }
            });
          }
        } catch (e) {
          console.error('显示错误信息失败:', e);
        }
      }
    },
    
    // 充电站利用率对比
    async renderUtilizationChart(params) {
      try {
        const response = await energyEfficiencyApi.getStationUtilization(params);
        
        // 确保DOM元素存在
        if (!this.$refs.utilizationChart) {
          console.error('利用率图表DOM元素不存在');
          return;
        }
        
        // 检查返回数据
        if (!response.data || !Array.isArray(response.data) || response.data.length === 0) {
          console.error('充电站利用率数据异常:', response.data);
          // 创建没有数据的图表以避免错误
          if (this.charts.utilization) {
            this.charts.utilization.dispose();
          }
          this.charts.utilization = echarts.init(this.$refs.utilizationChart);
          this.charts.utilization.setOption({
            title: {
              text: '充电站利用率对比 (暂无数据)',
              left: 'center'
            }
          });
          return;
        }
        
        // 销毁旧图表实例
        if (this.charts.utilization) {
          try {
            this.charts.utilization.dispose();
            this.charts.utilization = null;
          } catch (error) {
            console.error('销毁旧利用率图表失败:', error);
          }
        }
        
        // 重新创建图表实例
        this.charts.utilization = echarts.init(this.$refs.utilizationChart);
        
        // 数据处理：确保所有数据都是正数，且单位一致
        const processedData = response.data.map(item => {
          return {
            stationName: item.stationName || '未知充电站',
            busyHours: Math.abs(parseFloat(item.busyHours || 0)),
            idleHours: Math.abs(parseFloat(item.idleHours || 0)),
            maintenanceHours: Math.abs(parseFloat(item.maintenanceHours || 0)),
            errorHours: Math.abs(parseFloat(item.errorHours || 0))
          };
        });
        
        // 验证数据总和是否合理，如果总和异常大，则进行归一化处理
        processedData.forEach(item => {
          const total = item.busyHours + item.idleHours + item.maintenanceHours + item.errorHours;
          // 如果总时间超过48小时（允许一定误差），则认为数据异常，需要归一化
          if (total > 48) {
            const factor = 24 / total;
            item.busyHours *= factor;
            item.idleHours *= factor;
            item.maintenanceHours *= factor;
            item.errorHours *= factor;
          }
        });
        
        console.log('处理后的充电站利用率数据:', processedData);
        
        const option = {
          title: {
            text: '充电站利用率对比',
            left: 'center'
          },
          tooltip: {
            trigger: 'axis',
            axisPointer: {
              type: 'shadow'
            },
            formatter: function(params) {
              let tooltip = params[0].name + '<br/>';
              let total = 0;
              
              params.forEach(param => {
                tooltip += param.seriesName + ': ' + param.value.toFixed(2) + ' 小时<br/>';
                total += param.value;
              });
              
              tooltip += '<br/>总计: ' + total.toFixed(2) + ' 小时';
              return tooltip;
            }
          },
          legend: {
            data: ['忙碌时间', '空闲时间', '维护时间', '故障时间'],
            selectedMode: false,
            top: '30px'
          },
          grid: {
            left: '3%',
            right: '4%',
            bottom: '3%',
            top: '80px',
            containLabel: true
          },
          xAxis: {
            type: 'value',
            name: '小时',
            min: 0,
            max: 24,
            axisLabel: {
              formatter: '{value} h'
            }
          },
          yAxis: {
            type: 'category',
            data: processedData.map(item => item.stationName)
          },
          series: [
            {
              name: '忙碌时间',
              type: 'bar',
              stack: 'total',
              label: {
                show: true,
                formatter: '{c} h'
              },
              emphasis: {
                focus: 'series'
              },
              data: processedData.map(item => parseFloat(item.busyHours.toFixed(2)))
            },
            {
              name: '空闲时间',
              type: 'bar',
              stack: 'total',
              label: {
                show: true,
                formatter: '{c} h'
              },
              emphasis: {
                focus: 'series'
              },
              data: processedData.map(item => parseFloat(item.idleHours.toFixed(2)))
            },
            {
              name: '维护时间',
              type: 'bar',
              stack: 'total',
              label: {
                show: true,
                formatter: '{c} h'
              },
              emphasis: {
                focus: 'series'
              },
              data: processedData.map(item => parseFloat(item.maintenanceHours.toFixed(2)))
            },
            {
              name: '故障时间',
              type: 'bar',
              stack: 'total',
              label: {
                show: true,
                formatter: '{c} h'
              },
              emphasis: {
                focus: 'series'
              },
              data: processedData.map(item => parseFloat(item.errorHours.toFixed(2)))
            }
          ]
        };
        
        this.charts.utilization.setOption(option);
        
        // 取消图表的点击事件
        this.charts.utilization.off('click');
      } catch (error) {
        console.error('渲染充电站利用率图表失败:', error);
        
        // 错误情况下，显示错误信息
        if (this.$refs.utilizationChart) {
          if (this.charts.utilization) {
            this.charts.utilization.dispose();
          }
          this.charts.utilization = echarts.init(this.$refs.utilizationChart);
          this.charts.utilization.setOption({
            title: {
              text: '充电站利用率对比 (加载失败)',
              textStyle: { color: '#ff0000' },
              left: 'center'
            }
          });
        }
      }
    },
    
    // 机器人充电行为分析
    async renderRobotChart(params) {
      try {
        const response = await energyEfficiencyApi.getRobotChargingBehavior(params);
        
        // 确保DOM元素存在
        if (!this.$refs.robotChart) {
          console.error('机器人充电行为图表DOM元素不存在');
          return;
        }
        
        // 检查返回的数据
        if (!response.data || !response.data.robots || !Array.isArray(response.data.robots) || response.data.robots.length === 0) {
          console.error('机器人充电行为数据异常:', response.data);
          // 创建空图表以避免错误
          if (this.charts.robot) {
            this.charts.robot.dispose();
          }
          this.charts.robot = echarts.init(this.$refs.robotChart);
          this.charts.robot.setOption({
            title: {
              text: '机器人充电行为分析 (暂无数据)',
              left: 'center'
            }
          });
          return;
        }
        
        // 销毁旧的图表实例
        if (this.charts.robot) {
          try {
            this.charts.robot.dispose();
            this.charts.robot = null;
          } catch (error) {
            console.error('销毁旧机器人充电行为图表失败:', error);
          }
        }
        
        this.charts.robot = echarts.init(this.$refs.robotChart);
      
        const option = {
          title: {
            text: '机器人充电行为分析'
          },
          tooltip: {
            trigger: 'axis'
          },
          legend: {
            data: ['充电次数', '平均充电时长', '平均等待时间'],
            selectedMode: false
          },
          grid: {
            left: '3%',
            right: '4%',
            bottom: '3%',
            containLabel: true
          },
          xAxis: [
            {
              type: 'category',
              data: response.data.robots.map(robot => robot.name),
              axisPointer: {
                type: 'shadow'
              }
            }
          ],
          yAxis: [
            {
              type: 'value',
              name: '次数',
              min: 0,
              axisLabel: {
                formatter: '{value}'
              }
            },
            {
              type: 'value',
              name: '时间 (分钟)',
              min: 0,
              axisLabel: {
                formatter: '{value} min'
              }
            }
          ],
          series: [
            {
              name: '充电次数',
              type: 'bar',
              data: response.data.robots.map(robot => robot.chargingCount)
            },
            {
              name: '平均充电时长',
              type: 'line',
              yAxisIndex: 1,
              data: response.data.robots.map(robot => robot.avgChargingDuration)
            },
            {
              name: '平均等待时间',
              type: 'line',
              yAxisIndex: 1,
              data: response.data.robots.map(robot => robot.avgWaitingTime)
            }
          ]
        };
        
        this.charts.robot.setOption(option);
        
        // 取消图表的点击事件
        this.charts.robot.off('click');
      } catch (error) {
        console.error('渲染机器人充电行为图表失败:', error);
        
        // 错误情况下，显示错误信息
        if (this.$refs.robotChart) {
          if (this.charts.robot) {
            this.charts.robot.dispose();
          }
          this.charts.robot = echarts.init(this.$refs.robotChart);
          this.charts.robot.setOption({
            title: {
              text: '机器人充电行为分析 (加载失败)',
              textStyle: { color: '#ff0000' },
              left: 'center'
            }
          });
        }
      }
    },
    
    // 充电高峰期分析
    async renderPeakChart(params) {
      try {
        const response = await energyEfficiencyApi.getChargingPeakAnalysis(params);
        
        // 确保DOM元素存在
        if (!this.$refs.peakChart) {
          console.error('充电高峰期图表DOM元素不存在');
          return;
        }
        
        // 检查返回的数据
        if (!response.data || !response.data.timeSlots || !response.data.requestCounts || !response.data.avgWaitingTimes) {
          console.error('充电高峰期数据异常:', response.data);
          // 创建空图表以避免错误
          if (this.charts.peak) {
            this.charts.peak.dispose();
          }
          this.charts.peak = echarts.init(this.$refs.peakChart);
          this.charts.peak.setOption({
            title: {
              text: '充电高峰期分析 (暂无数据)',
              left: 'center'
            }
          });
          return;
        }
        
        // 销毁旧的图表实例
        if (this.charts.peak) {
          try {
            this.charts.peak.dispose();
            this.charts.peak = null;
          } catch (error) {
            console.error('销毁旧充电高峰期图表失败:', error);
          }
        }
        
        this.charts.peak = echarts.init(this.$refs.peakChart);
      
        const option = {
          title: {
            text: '充电高峰期分析'
          },
          tooltip: {
            trigger: 'axis',
            axisPointer: {
              type: 'shadow'
            }
          },
          legend: {
            data: ['充电请求数', '平均等待时间'],
            selectedMode: false
          },
          grid: {
            left: '3%',
            right: '4%',
            bottom: '3%',
            containLabel: true
          },
          xAxis: [
            {
              type: 'category',
              data: response.data.timeSlots,
              axisLabel: {
                formatter: '{value}时'
              }
            }
          ],
          yAxis: [
            {
              type: 'value',
              name: '请求数',
              min: 0,
              axisLabel: {
                formatter: '{value}'
              }
            },
            {
              type: 'value',
              name: '等待时间 (分钟)',
              min: 0,
              axisLabel: {
                formatter: '{value} min'
              }
            }
          ],
          series: [
            {
              name: '充电请求数',
              type: 'bar',
              data: response.data.requestCounts
            },
            {
              name: '平均等待时间',
              type: 'line',
              yAxisIndex: 1,
              data: response.data.avgWaitingTimes
            }
          ]
        };
        
        this.charts.peak.setOption(option);
        
        // 取消图表的点击事件
        this.charts.peak.off('click');
      } catch (error) {
        console.error('渲染充电高峰期图表失败:', error);
        
        // 错误情况下，显示错误信息
        if (this.$refs.peakChart) {
          if (this.charts.peak) {
            this.charts.peak.dispose();
          }
          this.charts.peak = echarts.init(this.$refs.peakChart);
          this.charts.peak.setOption({
            title: {
              text: '充电高峰期分析 (加载失败)',
              textStyle: { color: '#ff0000' },
              left: 'center'
            }
          });
        }
      }
    },
    
    // 获取筛选参数
    getFilterParams() {
      return {
        startDate: this.dateRange[0] ? this.dateRange[0].toISOString() : null,
        endDate: this.dateRange[1] ? this.dateRange[1].toISOString() : null,
        stationIds: this.selectedStations.length > 0 ? this.selectedStations : null,
        robotIds: this.selectedRobots.length > 0 ? this.selectedRobots : null
      };
    },
    
    // 处理图表切换
    handleChartChange(chartType) {
      const titles = {
        efficiency: '充电效率趋势分析',
        consumption: '能耗分布热力图',
        utilization: '充电站利用率对比',
        robot: '机器人充电行为分析',
        peak: '充电高峰期分析'
      };
      
      this.currentChartTitle = titles[chartType];
      
      // 在切换图表前先清理旧图表实例，避免内存泄漏和DOM冲突
      if (this.charts[this.currentChart]) {
        try {
          // 移除所有事件监听器
          this.charts[this.currentChart].off();
          this.charts[this.currentChart].dispose();
          this.charts[this.currentChart] = null;
        } catch (error) {
          console.error(`清理图表失败: ${error}`);
        }
      }
      
      // 使用nextTick确保DOM已更新
      this.$nextTick(() => {
        this.fetchChartData();
      });
    },
    
    // 增强版创建图表函数，包含额外的安全检查
    async safeInitChart(refName, chartKey) {
      // 检查DOM元素是否存在且在文档中
      if (!this.$refs[refName] || !document.body.contains(this.$refs[refName])) {
        console.error(`${refName} DOM元素不存在或已从文档中移除`);
        return null;
      }
      
      // 销毁旧的图表实例
      if (this.charts[chartKey]) {
        try {
          this.charts[chartKey].dispose();
          this.charts[chartKey] = null;
        } catch (error) {
          console.error(`销毁旧 ${chartKey} 图表失败:`, error);
        }
      }
      
      try {
        // 等待DOM更新
        await this.$nextTick();
        
        // 再次检查DOM是否仍然存在
        if (!this.$refs[refName] || !document.body.contains(this.$refs[refName])) {
          console.error(`${refName} DOM元素在DOM更新后已不存在，无法创建图表`);
          return null;
        }
        
        // 创建图表实例
        this.charts[chartKey] = echarts.init(this.$refs[refName]);
        return this.charts[chartKey];
      } catch (error) {
        console.error(`创建 ${chartKey} 图表失败:`, error);
        return null;
      }
    },
    
    // 获取KPI描述
    getKpiDescription(index) {
      // 根据索引返回相应的描述
      const descriptions = [
        `平均充电效率\n\n计算公式：实际充电量/(充电时长*充电站功率)*100%\n\n含义：表示充电过程中能源转换的效率。效率越高，表示充电系统性能越好，能源利用率越高。`,
        
        `总能耗\n\n含义：所有充电站在统计周期内消耗的总电量，单位为千瓦时(kWh)或兆瓦时(MWh)。\n\n用途：通过分析能耗可以评估系统整体电力消耗情况和运行成本。`,
        
        `充电器利用率\n\n计算公式：充电时间总和/(充电站数量*统计周期小时数)*100%\n\n含义：衡量充电设备的使用效率。较高的利用率表示设备投资回报更好。`,
        
        `平均等待时间\n\n计算方式：机器人从发出充电请求到开始充电的平均等待时长。\n\n含义：等待时间短表示充电调度更高效，能提高整体工作效率和降低生产延误。`,
        
        `充电成功率\n\n计算公式：成功完成的充电订单数/总订单数*100%\n\n含义：衡量充电过程的可靠性。高成功率表示系统稳定性好，减少了因充电失败导致的工作中断。`,
        
        `总充电次数\n\n含义：统计周期内完成的充电订单总数，反映系统负载和使用频率。\n\n用途：可用于评估充电需求变化趋势，为扩容或优化提供依据。`
      ];
      return descriptions[index];
    }
  }
};
</script>

<style scoped>
.energy-efficiency-analysis {
  padding: 20px;
}

/* 新增部分标题样式 */
.section-title {
  margin-bottom: 15px;
  border-left: 4px solid #409EFF;
  padding-left: 15px;
}

.section-title h2 {
  font-size: 20px;
  margin: 0 0 5px 0;
  font-weight: 600;
  color: #303133;
}

.section-subtitle {
  font-size: 14px;
  color: #909399;
}

.kpi-container {
  margin-bottom: 30px; /* 减小与图表的间距 */
}

.kpi-card {
  text-align: center;
  padding: 12px 10px; /* 减小内边距 */
  height: auto; /* 高度自适应内容 */
  transition: all 0.3s;
  margin-bottom: 15px; /* 减小卡片间距 */
}

.kpi-card:hover {
  transform: translateY(-3px); /* 减小悬停效果 */
  box-shadow: 0 3px 10px rgba(0, 0, 0, 0.1);
}

.kpi-title {
  font-size: 14px;
  color: #606266;
  margin-bottom: 8px; /* 减小间距 */
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 20px; /* 减小最小高度 */
  flex-wrap: wrap; /* 允许文本换行 */
}

.title-text {
  display: inline-block;
  text-align: center;
  cursor: pointer;
  overflow: visible; /* 允许文本完全显示 */
  text-overflow: clip;
  white-space: normal; /* 允许文本换行 */
  word-break: break-word; /* 允许在单词内换行 */
  padding: 0 2px;
  line-height: 1.2;
}

.info-icon {
  color: #909399;
  font-size: 14px; /* 减小图标大小 */
  margin-left: 3px;
  cursor: pointer;
  flex-shrink: 0; /* 防止图标被压缩 */
}

.info-icon:hover {
  color: #409EFF;
}

.kpi-value {
  display: flex;
  justify-content: center;
  align-items: baseline;
  margin-bottom: 8px; /* 减小间距 */
  line-height: 1.1;
}

.value-number {
  font-size: 26px; /* 减小字体大小 */
  font-weight: bold;
  color: #303133;
}

.value-unit {
  font-size: 13px;
  color: #909399;
  margin-left: 2px;
}

.kpi-change {
  font-size: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 2px 6px; /* 减小内边距 */
  border-radius: 10px;
  background-color: rgba(0, 0, 0, 0.03);
  max-width: 80%;
  margin: 0 auto;
  cursor: pointer;
}

.kpi-change.up {
  color: #67c23a;
}

.kpi-change.down {
  color: #f56c6c;
}

.kpi-change .el-icon {
  margin-right: 3px;
  font-size: 12px; /* 减小图标大小 */
}

.chart-container {
  margin-bottom: 30px;
}

.chart-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  flex-wrap: wrap; /* 在小屏幕上允许换行 */
}

.chart-header h3 {
  margin: 0;
  font-size: 18px;
  color: #303133;
  margin-bottom: 10px; /* 在小屏幕换行时提供间距 */
}

.chart-content {
  position: relative;
  min-height: 450px; /* 确保图表有足够的高度 */
}

.chart-item {
  position: relative;
  width: 100%;
  height: 100%;
}

.chart {
  height: 450px;
  width: 100%;
}

/* 自定义Tooltip样式 */
:deep(.el-tooltip__popper) {
  max-width: 300px;
  line-height: 1.5;
  white-space: pre-wrap !important; /* 保留换行 */
}

:deep(.el-tooltip__popper p) {
  margin: 0;
  padding: 0;
}

/* 响应式调整 */
@media (max-width: 768px) {
  .chart-header {
    flex-direction: column;
    align-items: flex-start;
  }
  
  .chart-header h3 {
    margin-bottom: 15px;
  }
  
  .chart {
    height: 350px; /* 在小屏幕上减小图表高度 */
  }
  
  .kpi-card {
    padding: 10px 8px;
  }
  
  .value-number {
    font-size: 22px;
  }
  
  .kpi-title {
    min-height: auto;
  }
}
</style> 