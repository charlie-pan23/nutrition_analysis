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
