<template>
  <div class="standby-view" @click="goToLogin">
    <img src="/logo.png" alt="Nutrition Scale Logo" class="logo">
    <p class="prompt">点击任意位置开始</p>
  </div>
</template>

<script>
export default {
  methods: {
    goToLogin() {
      this.$router.push('/login')
    }
  }
}
</script>

<style scoped>
.standby-view {
  background-color: #e0ffe1;
  width: 1280pt;
  height: 800pt;
  position: relative; /* 启用绝对定位的参考系 */
  cursor: pointer;
  overflow: hidden; /* 防止内容溢出容器 */
}

.logo {
  position: absolute;
  width: 200pt;
  height: 200pt;
  object-fit: cover;
  left: 380pt;
  top: 200pt;
}

.prompt {
  position: absolute;
  font-size: 2rem;
  color: #388e3c;
  animation: pulse 2s infinite;
  left: 380pt; /* 手动设置水平位置 */
  top: 500pt;  /* 手动设置垂直位置 */
}

@keyframes pulse {
  0% { opacity: 0.6; }
  50% { opacity: 1; }
  100% { opacity: 0.6; }
}
</style>
