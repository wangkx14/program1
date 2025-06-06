<template>
  <div class="login-container">
    <el-card class="login-card">
      <div class="login-header">
        <el-icon class="logo-icon"><TrendCharts /></el-icon>
        <h2>货仓机器人激光充电和能效管理云平台</h2>
      </div>
      <el-form :ref="el => loginFormRef = el" :model="loginForm" :rules="loginRules" label-width="0px">
        <el-form-item prop="username">
          <el-input
            v-model="loginForm.username"
            placeholder="用户名"
            clearable
          >
            <template #prefix>
              <el-icon><User /></el-icon>
            </template>
          </el-input>
        </el-form-item>
        <el-form-item prop="password">
          <el-input
            v-model="loginForm.password"
            placeholder="密码"
            show-password
            clearable
            @keyup.enter="handleLogin"
          >
            <template #prefix>
              <el-icon><Lock /></el-icon>
            </template>
          </el-input>
        </el-form-item>
        <el-form-item>
          <el-button
            type="primary"
            :loading="loading"
            class="login-button"
            @click="handleLogin"
          >
            {{ loading ? '登录中...' : '登 录' }}
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script>
import { ref, reactive } from 'vue'
import { useStore } from 'vuex'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { User, Lock, TrendCharts } from '@element-plus/icons-vue'

export default {
  name: 'LoginView',
  components: {
    User,
    Lock,
    TrendCharts
  },
  setup() {
    const store = useStore()
    const router = useRouter()
    const loginForm = reactive({
      username: '',
      password: ''
    })
    const loading = ref(false)
    
    const loginRules = {
      username: [
        { required: true, message: '请输入用户名', trigger: 'blur' }
      ],
      password: [
        { required: true, message: '请输入密码', trigger: 'blur' }
      ]
    }
    
    const loginFormRef = ref(null)
    
    const handleLogin = async () => {
      if (loginFormRef.value) {
        try {
          await loginFormRef.value.validate()
          
          loading.value = true
          try {
            await store.dispatch('login', {
              username: loginForm.username,
              password: loginForm.password
            })
            
            const user = store.getters.currentUser
            ElMessage.success(`欢迎回来，${user.username}`)
            
            // 登录成功后跳转到首页
            router.push('/')
          } catch (error) {
            console.error('登录失败:', error)
            ElMessage.error(error.message || '登录失败，请检查用户名和密码')
          } finally {
            loading.value = false
          }
        } catch (formError) {
          console.log('表单验证失败:', formError)
        }
      }
    }
    
    return {
      loginForm,
      loginRules,
      loading,
      loginFormRef,
      handleLogin
    }
  }
}
</script>

<style scoped>
.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
}

.login-card {
  width: 400px;
  padding: 20px;
}

.login-header {
  text-align: center;
  margin-bottom: 30px;
}

.logo-icon {
  font-size: 40px;
  margin-bottom: 10px;
  color: #409EFF;
}

.login-header h2 {
  font-size: 20px;
  color: #333;
  margin: 10px 0;
}

.login-button {
  width: 100%;
  padding: 12px 0;
}
</style> 