<template>
  <el-container>
    <el-header style="height: 80px;" class="app-header">
      <div class="space-between">
        <div class="start">
          <div class="logo">
            <img src="/logo.png" alt="Logo" class="logo">
          </div>
          <div class="title" style="color:#000000; margin-left: 5px;">
            <h1 class="title">Nutrition Analysis</h1>
          </div>
        </div>
        <div class="start">
          <span style="color:#000000;margin-right: 15px;">{{ username }}</span>
          <el-button type="danger" @click="logout">退出登录</el-button>
        </div>
      </div>
    </el-header>
    <el-main>
      <router-view/>
    </el-main>
  </el-container>
</template>

<script setup>
import { useRouter } from 'vue-router'
import axios from 'axios'
import { ref, onMounted } from 'vue'


const router = useRouter()
const username = ref('')

const fetchUserInfo = async () => {
  try {
    const res = await axios.get('/api/current-user') // 假设这个接口返回用户信息
    username.value = res.data.name || '用户'
  } catch (error) {
    console.error('获取用户信息失败', error)
    username.value = '用户'
  }
}

const logout = async () => {
  try {
    await axios.get('/api/logout') // 调用登出接口
  } catch (error) {
    console.error('退出登录失败:', error)
  } finally {
    username.value = ''
    router.push('/') // 跳转到 standby 页面
  }
}

onMounted(() => {
  fetchUserInfo()
})

</script>

<style scoped>
.app-header {
  background-color: #03ca6d;
}
.title {
  font-size: 28px;
  font-weight: bold;
  margin-left: 15px;
  letter-spacing: 1px;
  font-family: "Segoe UI", sans-serif;
}

.logo {
  height: 80px;
  width: auto;
}
</style>