<template>
  <div class="chart-container" v-loading="loading">
    <div ref="chartRef" class="chart"></div>
  </div>
</template>

<script>
import * as echarts from 'echarts';
import dashboardApi from '@/api/dashboard';

export default {
  name: 'ChargingEfficiencyChart',
  data() {
    return {
      loading: false,
      chart: null,
      efficiencyData: []
    };
  },
  mounted() {
    this.initChart();
    this.fetchData();
    
    // 设置自动刷新（每60秒刷新一次）
    this.refreshInterval = setInterval(() => {
      this.fetchData();
    }, 60000);
  },
  beforeUnmount() {
    // 组件销毁前清除定时器和图表实例
    if (this.refreshInterval) {
      clearInterval(this.refreshInterval);
    }
    if (this.chart) {
      this.chart.dispose();
      this.chart = null;
    }
  },
  methods: {
    initChart() {
      // 确保DOM元素已渲染
      if (!this.$refs.chartRef) return;
      
      // 初始化图表
      this.chart = echarts.init(this.$refs.chartRef);
      
      // 设置基础配置
      const option = {
        title: {
          text: '充电效率趋势',
          left: 'center',
          textStyle: {
            fontSize: 14
          }
        },
        tooltip: {
          trigger: 'axis',
          formatter: '{b}: {c}%'
        },
        grid: {
          left: '3%',
          right: '4%',
          bottom: '3%',
          containLabel: true
        },
        xAxis: {
          type: 'category',
          data: [],
          axisLabel: {
            interval: 0,
            rotate: 30
          }
        },
        yAxis: {
          type: 'value',
          name: '充电效率 (%)',
          min: 50,
          max: 100
        },
        series: [
          {
            type: 'bar',
            data: [],
            itemStyle: {
              color: function(params) {
                // 根据效率值设置不同颜色
                const value = params.value;
                if (value >= 90) return '#67C23A'; // 高效率 - 绿色
                if (value >= 80) return '#E6A23C'; // 中等效率 - 黄色
                return '#F56C6C'; // 低效率 - 红色
              }
            },
            label: {
              show: true,
              position: 'top',
              formatter: '{c}%'
            }
          }
        ]
      };
      
      this.chart.setOption(option);
      
      // 添加窗口大小变化时自动调整图表大小的监听器
      window.addEventListener('resize', this.resizeChart);
    },
    resizeChart() {
      if (this.chart) {
        this.chart.resize();
      }
    },
    async fetchData() {
      this.loading = true;
      try {
        const response = await dashboardApi.getChargingEfficiency();
        this.efficiencyData = response.data;
        this.updateChart();
      } catch (error) {
        console.error('获取充电效率数据失败:', error);
        this.$message.error('获取充电效率数据失败');
      } finally {
        this.loading = false;
      }
    },
    updateChart() {
      if (!this.chart || !this.efficiencyData.length) return;
      
      // 提取充电站名称和效率数据
      const stationNames = this.efficiencyData.map(item => item.name);
      const efficiencyValues = this.efficiencyData.map(item => parseFloat(item.efficiency).toFixed(2));
      
      // 更新图表数据
      this.chart.setOption({
        xAxis: {
          data: stationNames
        },
        series: [
          {
            data: efficiencyValues
          }
        ]
      });
    }
  }
};
</script>

<style scoped>
.chart-container {
  width: 100%;
  height: 100%;
  min-height: 300px;
}

.chart {
  width: 100%;
  height: 100%;
  min-height: 300px;
}
</style> 