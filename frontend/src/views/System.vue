<template>
  <div class="system-container">
    <h2>系统设置</h2>
    <el-card class="box-card">
      <el-form :model="settings" label-width="120px">
        <el-form-item label="系统名称">
          <el-input v-model="settings.systemName" />
        </el-form-item>
        <el-form-item label="MQTT服务器">
          <el-input v-model="settings.mqttServer" />
        </el-form-item>
        <el-form-item label="MQTT端口">
          <el-input-number v-model="settings.mqttPort" :min="1" :max="65535" />
        </el-form-item>
        <el-form-item label="数据刷新间隔">
          <el-input-number v-model="settings.refreshInterval" :min="1" :max="60" />
          <span class="unit">秒</span>
        </el-form-item>
        <el-form-item label="告警阈值">
          <el-input-number v-model="settings.alertThreshold" :min="0" :max="100" />
          <span class="unit">%</span>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="saveSettings">保存设置</el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script>
export default {
  name: 'System',
  data() {
    return {
      settings: {
        systemName: '货仓机器人激光充电和能效管理云平台',
        mqttServer: 'localhost',
        mqttPort: 1883,
        refreshInterval: 5,
        alertThreshold: 20
      }
    }
  },
  methods: {
    saveSettings() {
      // TODO: 实现保存设置的逻辑
      this.$message.success('设置已保存')
    }
  }
}
</script>

<style scoped>
.system-container {
  padding: 20px;
}
.unit {
  margin-left: 10px;
  color: #666;
}
</style> 