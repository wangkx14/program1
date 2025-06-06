import { api } from './index';

export default {
  /**
   * 获取仪表盘概览数据
   */
  getDashboardOverview() {
    return api.get('/system/dashboard');
  },
  
  /**
   * 获取系统告警数据
   * @param {Number} page 页码，默认为1
   * @param {Number} perPage 每页数量，默认为7
   */
  getSystemAlerts(page = 1, perPage = 7) {
    return api.get('/system/alerts', {
      params: {
        page,
        per_page: perPage
      }
    });
  },

  /**
   * 检查低电量机器人并自动充电
   */
  checkLowBatteryRobots() {
    return api.get('/robots/check-low-battery');
  },

  /**
   * 获取充电效率趋势数据
   */
  getChargingEfficiency() {
    return api.get('/system/charging-efficiency');
  }
}; 