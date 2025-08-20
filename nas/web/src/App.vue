<template>
  <div id="app" :style="{ backgroundColor: bgColor }">
    <router-view />
  </div>
</template>

<script>
export default {
  name: 'App',
  data() {
    return {
      bgColor: '#e0ffe1' // 待机界面背景色
    }
  }
}
</script>

<style>
body {
    /* 允许垂直方向的触摸滚动 */
    touch-action: pan-y; 
    -ms-touch-action: pan-y; /* 兼容旧版 IE */
    
    /* 禁用文本选择，强烈推荐，防止误选 */
    user-select: none !important;   
    -webkit-user-select: none !important; /* 兼容 WebKit 内核的浏览器（如 Chromium） */
    -moz-user-select: none !important;    /* 兼容 Firefox */
}


#app {
  width: 1280px;
  height: 800px;
  margin: 0;
  padding: 0;
  position: fixed;
  top: 0;
  left: 0;
  overflow: hidden;
  font-family: Arial, sans-serif;
}
</style>
