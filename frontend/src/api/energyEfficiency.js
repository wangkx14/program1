import { api } from './index';

export default {
  // 获取充电站列表
  getStations() {
    return api.get('/stations/');
  },
  
  // 获取机器人列表
  getRobots() {
    return api.get('/robots/');
  },
  
  // 获取KPI数据
  getKpiData(params) {
    return api.get('/energy-efficiency/kpi/', { params });
  },
  
  // 获取充电效率趋势
  getEfficiencyTrend(params) {
    return api.get('/energy-efficiency/efficiency-trend/', { params });
  },
  
  // 获取能耗分布
  getEnergyConsumptionDistribution(params) {
    return api.get('/energy-efficiency/energy-distribution/', { params });
  },
  
  // 获取充电站利用率
  getStationUtilization(params) {
    return api.get('/energy-efficiency/station-utilization/', { params });
  },
  
  // 获取机器人充电行为分析
  getRobotChargingBehavior(params) {
    return api.get('/energy-efficiency/robot-charging-behavior/', { params });
  },
  
  // 获取充电高峰期分析
  getChargingPeakAnalysis(params) {
    return api.get('/energy-efficiency/peak-analysis/', { params });
  },
  
  // 获取充电事件列表
  getChargingEvents(params) {
    return api.get('/energy-efficiency/charging-events/', { params });
  },
  
  // 导出数据
  exportData(params) {
    return api.get('/energy-efficiency/export/', { 
      params,
      responseType: 'blob'
    });
  }
}; 