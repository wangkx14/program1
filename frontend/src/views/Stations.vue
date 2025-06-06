<template>
  <div class="stations-container">
    <h2>充电站管理</h2>
    <el-card class="box-card">
      <div class="toolbar">
        <el-button v-if="isAdmin" type="primary" @click="showAddDialog">添加充电站</el-button>
      </div>
      
      <div v-if="error" class="error-message">
        <el-alert
          title="加载数据出错"
          type="error"
          :description="error"
          show-icon
        />
      </div>
      
      <el-table 
        v-if="stations && stations.length > 0" 
        :data="paginatedStations" 
        style="width: 100%" 
        v-loading="loading">
        <el-table-column prop="id" label="充电站ID" width="180" />
        <el-table-column prop="name" label="名称" width="180" />
        <el-table-column prop="location" label="位置" />
        <el-table-column prop="status" label="状态">
          <template #default="scope">
            <el-tag :type="getStatusType(scope.row.status)">
              {{ getStatusText(scope.row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="power_rating" label="输出功率" />
        <el-table-column prop="efficiency" label="充电效率">
          <template #default="scope">
            <el-progress :percentage="scope.row.efficiency" />
          </template>
        </el-table-column>
        <el-table-column label="关联机器人">
          <template #default="scope">
            <div v-if="getAssociatedRobot(scope.row.id)">
              <el-tag type="primary">
                {{ getAssociatedRobot(scope.row.id).name }}
                <span v-if="getAssociatedRobot(scope.row.id).status === 'charging'"> (充电中)</span>
              </el-tag>
            </div>
            <span v-else class="no-robot">无关联机器人</span>
          </template>
        </el-table-column>
        <el-table-column v-if="isAdmin" label="操作" width="200">
          <template #default="scope">
            <el-button size="small" @click="handleEdit(scope.row)">编辑</el-button>
            <el-button size="small" type="danger" @click="handleDelete(scope.row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
      
      <div v-else-if="!loading" class="no-data">
        <el-empty description="暂无数据" />
      </div>
      
      <!-- 分页控件 -->
      <div class="pagination-container" v-if="stations && stations.length > 0">
        <el-pagination
          v-model:current-page="currentPage"
          :page-size="pageSize"
          :total="totalItems"
          layout="total, prev, pager, next, jumper"
          @current-change="handleCurrentChange"
        />
      </div>
    </el-card>

    <!-- 添加/编辑对话框 -->
    <el-dialog 
      :title="dialogTitle" 
      v-model="dialogVisible"
      :close-on-click-modal="false"
      :destroy-on-close="true"
      append-to-body
      :modal-append-to-body="false"
      width="500px"
      :lock-scroll="false"
      @open="handleDialogOpen">
      <div class="dialog-content-wrapper">
        <el-form 
          :model="stationForm" 
          label-width="120px" 
          ref="stationFormRef" 
          :key="`station-form-${dialogVisible}`">
          <el-form-item label="充电站名称">
            <el-input v-model="stationForm.name" />
          </el-form-item>
          <el-form-item label="位置">
            <el-input v-model="stationForm.location" />
          </el-form-item>
          <el-form-item label="输出功率">
            <el-input-number v-model="stationForm.power_rating" :min="0" :controls="false" />
          </el-form-item>
        </el-form>
      </div>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="closeDialog">取消</el-button>
          <el-button type="primary" @click="handleSave">确定</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script>
import { stationApi } from '@/api'
import { ElMessage, ElMessageBox } from 'element-plus'
import { computed } from 'vue'
import { useStore } from 'vuex'
import { robotApi } from '@/api'

export default {
  name: 'Stations',
  setup() {
    const store = useStore()
    const isAdmin = computed(() => store.getters.isAdmin)
    
    return {
      isAdmin
    }
  },
  data() {
    return {
      stations: [],
      robots: [],
      loading: false,
      error: null,
      dialogVisible: false,
      dialogTitle: '添加充电站',
      stationForm: {
        name: '',
        location: '',
        power_rating: 0
      },
      isEdit: false,
      currentId: null,
      // 分页相关
      currentPage: 1,
      pageSize: 10,
      // 防止表单重复提交
      isSaving: false
    }
  },
  computed: {
    totalItems() {
      return this.stations.length
    },
    paginatedStations() {
      const startIndex = (this.currentPage - 1) * this.pageSize
      const endIndex = startIndex + this.pageSize
      return this.stations.slice(startIndex, endIndex)
    }
  },
  created() {
    console.log('Stations组件已创建，准备获取数据')
    this.fetchStations()
    this.fetchRobots()
  },
  methods: {
    async fetchStations() {
      try {
        this.loading = true
        this.error = null
        console.log('开始获取充电站数据')
        
        try {
          const response = await stationApi.getAll()
          // 打印原始响应
          console.log('获取到充电站数据(原始):', response)
          console.log('获取到充电站数据:', response.data)
          console.log('充电站数据类型:', typeof response.data, Array.isArray(response.data))
          
          // 确保数据是数组
          if (Array.isArray(response.data)) {
            // 检查每个充电站对象的字段
            const validStations = response.data.filter(station => {
              const isValid = station && 
                            typeof station === 'object' && 
                            'id' in station && 
                            'name' in station && 
                            'location' in station && 
                            'status' in station;
              
              // 处理可能的NaN或undefined值
              if (isValid) {
                // 确保power_rating字段存在且为数字
                if (!('power_rating' in station) || station.power_rating === null || isNaN(station.power_rating)) {
                  station.power_rating = 0;
                }
                
                // 确保efficiency字段存在且为数字
                if (!('efficiency' in station) || station.efficiency === null || isNaN(station.efficiency)) {
                  station.efficiency = 80; // 默认效率
                }
              } else {
                console.warn('过滤掉无效的充电站数据:', station);
              }
              return isValid;
            });
            
            console.log('有效的充电站数据:', validStations);
            this.stations = validStations;
            // 重置为第一页
            this.currentPage = 1;
            console.log('成功设置充电站数据，数量:', this.stations.length)
          } else {
            console.error('API返回的充电站数据不是数组:', response.data)
            this.stations = [] // 设置为空数组
            this.error = '充电站数据格式错误，请联系管理员'
            ElMessage.error('充电站数据格式错误')
          }
        } catch (apiError) {
          console.error('API调用出错:', apiError)
          this.stations = [] // 确保错误时也设置为空数组
          this.error = `API调用出错: ${apiError.message || '未知错误'}`
          ElMessage.error('获取充电站数据失败')
        }
      } catch (error) {
        console.error('获取充电站列表失败:', error)
        this.stations = [] // 确保错误时也设置为空数组
        this.error = `获取数据失败: ${error.message || '未知错误'}`
        ElMessage.error('获取充电站列表失败')
      } finally {
        this.loading = false
      }
    },
    
    async fetchRobots() {
      try {
        console.log('开始获取机器人数据')
        const response = await robotApi.getAll()
        
        if (Array.isArray(response.data)) {
          this.robots = response.data
          console.log('成功获取机器人数据，数量:', this.robots.length)
        } else {
          console.error('API返回的机器人数据不是数组')
          this.robots = []
        }
      } catch (error) {
        console.error('获取机器人列表失败:', error)
        this.robots = []
      }
    },
    // 分页相关方法
    handleCurrentChange(page) {
      this.currentPage = page
      console.log(`当前页: ${this.currentPage}`)
    },
    getStatusType(status) {
      const types = {
        'idle': 'info',
        'charging': 'primary',
        'maintenance': 'warning',
        'error': 'danger'
      }
      return types[status] || 'info'
    },
    getStatusText(status) {
      const texts = {
        'idle': '空闲',
        'charging': '充电中',
        'maintenance': '维护中',
        'error': '故障'
      }
      return texts[status] || status
    },
    showAddDialog() {
      this.dialogTitle = '添加充电站'
      this.isEdit = false
      this.stationForm = {
        name: '',
        location: '',
        power_rating: 0
      }
      this.isSaving = false
      // 使用nextTick确保DOM更新后再显示对话框
      this.$nextTick(() => {
        this.dialogVisible = true
      })
    },
    handleEdit(row) {
      this.dialogTitle = '编辑充电站'
      this.isEdit = true
      this.currentId = row.id
      this.stationForm = { ...row }
      this.isSaving = false
      // 使用nextTick确保DOM更新后再显示对话框
      this.$nextTick(() => {
        this.dialogVisible = true
      })
    },
    async handleDelete(row) {
      try {
        await ElMessageBox.confirm('确定要删除这个充电站吗？', '提示', {
          type: 'warning'
        })
        
        // 禁用所有可能的ResizeObserver
        try {
          // 尝试临时禁用所有ResizeObserver
          const disableResizeObservers = () => {
            if (window.ResizeObserver) {
              const originalResizeObserver = window.ResizeObserver;
              window.ResizeObserver = class DisabledResizeObserver {
                constructor() {
                  this.observe = () => {};
                  this.unobserve = () => {};
                  this.disconnect = () => {};
                }
              };
              // 5秒后恢复原始ResizeObserver
              setTimeout(() => {
                window.ResizeObserver = originalResizeObserver;
              }, 5000);
            }
          };
          
          // 只在开发环境执行，避免影响生产环境
          if (process.env.NODE_ENV === 'development') {
            disableResizeObservers();
          }
        } catch (e) {
          console.warn('临时禁用ResizeObserver失败:', e);
        }
        
        // 在删除前先通知其他组件准备清理资源
        try {
          if (this.$root && this.$root.$emit) {
            this.$root.$emit('station-pre-delete', row.id);
          }
        } catch (e) {
          console.error('发送预删除事件失败:', e);
        }
        
        // 延迟一小段时间让其他组件有时间做准备
        await new Promise(resolve => setTimeout(resolve, 100));
        
        // 执行删除操作
        await stationApi.delete(row.id);
        ElMessage.success('删除成功');
        
        // 立即清理可能存在的悬空引用
        try {
          // 移除所有能效分析相关的图表DOM元素内容
          const chartElements = document.querySelectorAll('.chart');
          chartElements.forEach(el => {
            if (el && el.parentNode) {
              el.innerHTML = '';
            }
          });
          
          // 强制执行一次浏览器布局重排
          if (document.body) {
            document.body.offsetHeight;
          }
        } catch (e) {
          console.warn('清理DOM失败:', e);
        }
        
        // 延迟刷新数据，让DOM有时间完成清理
        setTimeout(() => {
          this.fetchStations();
          
          // 向父组件或全局事件总线发送刷新通知
          this.$emit('station-deleted', row.id);
          
          // 尝试发送全局事件通知其他组件刷新
          try {
            if (this.$root && this.$root.$emit) {
              this.$root.$emit('station-data-changed', {
                action: 'delete',
                stationId: row.id
              });
            }
          } catch (e) {
            console.error('发送全局事件失败:', e);
          }
          
          // 延迟执行一次全局垃圾回收
          setTimeout(() => {
            try {
              if (window.gc) window.gc();
            } catch (e) {
              // 大多数浏览器不支持直接调用gc，忽略错误
            }
            
            // 强制刷新所有图表
            try {
              if (this.$root && this.$root.$emit) {
                this.$root.$emit('force-refresh-charts');
              }
            } catch (e) {
              console.warn('强制刷新图表失败:', e);
            }
          }, 1000);
        }, 300);
      } catch (error) {
        if (error !== 'cancel') {
          ElMessage.error('删除失败');
          console.error(error);
        }
      }
    },
    handleDialogOpen() {
      // 对话框打开时重置表单状态
      this.isSaving = false
      console.log('对话框已打开')
    },
    closeDialog() {
      // 先隐藏内容，延迟关闭对话框，避免ResizeObserver错误
      const dialogContent = document.querySelector('.dialog-content-wrapper');
      if (dialogContent) {
        dialogContent.style.display = 'none';
      }
      
      // 使用较长的延时确保DOM完全稳定
      setTimeout(() => {
        this.dialogVisible = false
      }, 300)
    },
    async handleSave() {
      // 防止重复提交
      if (this.isSaving) return
      
      try {
        this.isSaving = true
        
        // 先隐藏内容，减少DOM重排
        const dialogContent = document.querySelector('.dialog-content-wrapper');
        if (dialogContent) {
          dialogContent.style.display = 'none';
        }
        
        // 准备提交的数据
        const formData = { ...this.stationForm };
        
        // 确保功率值是数字
        if (formData.power_rating !== undefined) {
          try {
            formData.power_rating = parseFloat(formData.power_rating);
            if (isNaN(formData.power_rating)) {
              formData.power_rating = 0;
            }
          } catch (e) {
            formData.power_rating = 0;
          }
        } else {
          formData.power_rating = 0;
        }
        
        console.log('准备提交的充电站数据:', formData);
        
        // 验证数据
        if (!formData.name || formData.name.trim() === '') {
          throw new Error('充电站名称不能为空');
        }
        
        if (!formData.location || formData.location.trim() === '') {
          throw new Error('充电站位置不能为空');
        }
        
        if (this.isEdit) {
          console.log(`更新充电站: ID=${this.currentId}`);
          try {
            const response = await stationApi.update(this.currentId, formData);
            console.log('更新充电站响应:', response);
            ElMessage.success('更新成功');
          } catch (apiError) {
            console.error('API调用失败:', apiError);
            throw new Error(`更新失败: ${apiError.message || '服务器错误'}`);
          }
        } else {
          console.log('添加新充电站');
          try {
            const response = await stationApi.add(formData);
            console.log('添加充电站响应:', response);
            ElMessage.success('添加成功');
          } catch (apiError) {
            console.error('API调用失败:', apiError);
            throw new Error(`添加失败: ${apiError.message || '服务器错误'}`);
          }
        }
        
        // 延迟关闭对话框，避免ResizeObserver错误
        setTimeout(() => {
          this.dialogVisible = false;
          // 重新加载数据，显示最新的充电站列表
          this.fetchStations();
        }, 300);
      } catch (error) {
        // 出错时也恢复显示内容
        const dialogContent = document.querySelector('.dialog-content-wrapper');
        if (dialogContent) {
          dialogContent.style.display = 'block';
        }
        
        console.error('保存充电站失败:', error);
        ElMessage.error(error.message || (this.isEdit ? '更新失败' : '添加失败'));
        this.isSaving = false;
      }
    },
    getAssociatedRobot(stationId) {
      // 查找关联到此充电桩的机器人
      return this.robots.find(robot => robot.station_id === stationId);
    }
  }
}
</script>

<style scoped>
.stations-container {
  padding: 20px;
}
.toolbar {
  margin-bottom: 20px;
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

/* 添加以下样式以解决对话框调整大小问题 */
:deep(.el-dialog) {
  overflow: hidden;
  max-width: 500px;
  min-width: 400px;
  margin: 0 auto !important;
  display: flex;
  flex-direction: column;
  border-radius: 4px;
  height: auto !important;
  
  /* 禁用对话框的大多数动画和过渡效果 */
  transition: none !important;
  animation: none !important;
  transform: none !important;
}

:deep(.el-dialog__body) {
  padding: 20px;
  overflow: hidden; /* 防止内容溢出导致resize事件 */
  position: relative;
  flex: 1;
  height: auto !important;
}

:deep(.el-input-number) {
  width: 100%;
}

/* 在移动设备上的样式调整 */
@media screen and (max-width: 768px) {
  :deep(.el-dialog) {
    width: 90% !important;
    min-width: 300px;
  }
}

:deep(.el-dialog__headerbtn) {
  transition: none !important;
}

:deep(.el-dialog__wrapper) {
  overflow: hidden !important;
  display: flex !important;
  align-items: center;
  justify-content: center;
}

/* 包装对话框内容，便于隐藏处理 */
.dialog-content-wrapper {
  width: 100%;
  overflow: hidden;
}

/* 全局禁用部分可能导致resize循环的动画 */
:deep(.el-dialog),
:deep(.el-form-item),
:deep(.el-input),
:deep(.el-input-number),
:deep(.el-form) {
  animation: none !important;
}

.no-robot {
  color: #909399;
  font-style: italic;
}
</style> 