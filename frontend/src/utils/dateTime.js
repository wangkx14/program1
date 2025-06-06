/**
 * 格式化日期时间
 * @param {string} dateStr - 日期字符串
 * @returns {string} 格式化后的日期时间字符串
 */
export function formatDateTime(dateStr) {
  if (!dateStr) return '-';
  
  const date = new Date(dateStr);
  if (isNaN(date.getTime())) return '-';
  
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit'
  });
}

/**
 * 计算两个时间之间的持续时间
 * @param {string} startTime - 开始时间字符串
 * @param {string} endTime - 结束时间字符串
 * @returns {string} 格式化后的持续时间
 */
export function calculateDuration(startTime, endTime) {
  if (!startTime || !endTime) return '-';
  
  const start = new Date(startTime);
  const end = new Date(endTime);
  
  if (isNaN(start.getTime()) || isNaN(end.getTime())) return '-';
  
  // 计算时间差（毫秒）
  const diffMs = end.getTime() - start.getTime();
  if (diffMs < 0) return '-';
  
  // 转换为分钟
  const diffMinutes = Math.floor(diffMs / 60000);
  
  // 格式化为小时和分钟
  const hours = Math.floor(diffMinutes / 60);
  const minutes = diffMinutes % 60;
  
  if (hours > 0) {
    return `${hours}小时${minutes}分钟`;
  } else {
    return `${minutes}分钟`;
  }
}

/**
 * 获取日期范围的天数数组
 * @param {Date} startDate - 开始日期
 * @param {Date} endDate - 结束日期
 * @returns {Array} 日期字符串数组
 */
export function getDateRange(startDate, endDate) {
  const dates = [];
  const currentDate = new Date(startDate);
  
  // 确保当前日期不超过结束日期
  while (currentDate <= endDate) {
    dates.push(currentDate.toISOString().split('T')[0]);
    currentDate.setDate(currentDate.getDate() + 1);
  }
  
  return dates;
}

/**
 * 根据时间戳获取小时
 * @param {string} timestamp - 时间戳字符串
 * @returns {number} 小时数 (0-23)
 */
export function getHourFromTimestamp(timestamp) {
  if (!timestamp) return 0;
  
  const date = new Date(timestamp);
  if (isNaN(date.getTime())) return 0;
  
  return date.getHours();
} 