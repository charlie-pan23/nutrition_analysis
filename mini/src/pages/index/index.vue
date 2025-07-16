<template>
  <view class="container">
    <Nav :has-nav="false" title="" title-color="#444444"></Nav>
    <view :style="sysHeight.paddingHeight" class="content">
      <view class="card c1">
        <view class="card-title">实时画面</view>
        <view class="camera-container">
          <img :src="videoUrl" alt="实时摄像头" class="camera-feed"/>
        </view>
      </view>
      <view class="card c2">
        <view class="title">实时分析</view>
        <!-- 表格容器 -->
        <view class="table-container">
          <!-- 滚动区域 + 数据行 -->
          <scroll-view scroll-x="true" @scroll="scroll">
            <view class="table-header">
              <view class="table-cell">食物名称</view>
              <view class="table-cell">重量/g</view>
              <view class="table-cell">热量/kcal</view>
              <view class="table-cell">蛋白质/g</view>
              <view class="table-cell">脂肪/g</view>
              <view class="table-cell">碳水化合物/g</view>
            </view>
            <block v-for="(item, index) in foodData" :key="index">
              <view class="table-row">
                <view class="table-cell">{{ item.name }}</view>
                <view class="table-cell">{{ item.weight }}</view>
                <view class="table-cell">{{ item.calories }}</view>
                <view class="table-cell">{{ item.protein }}</view>
                <view class="table-cell">{{ item.fat }}</view>
                <view class="table-cell">{{ item.carbohydrates }}</view>
              </view>
            </block>

            <!-- 空状态 -->
            <view v-if="foodData.length === 0" class="empty-result">
              暂无检测结果
            </view>
          </scroll-view>
        </view>
      </view>
      <view class="control">
        <view class="item btn">分析</view>
        <view class="item circle">讲话</view>
        <view class="item btn">记录</view>
      </view>
    </view>
    <Tab :tab="2"/>
  </view>
</template>

<script setup>
import Nav from "@/components/nav.vue";
import Tab from "@/components/tabbar.vue";

import {ref, onMounted} from 'vue';
import http from "@/utils/http";

const loading = ref(false)
const sysHeight = computed(() => {
  const info = uni.getStorageSync('systemInfo')
  let statusBarHeight = info.statusBarHeight * info.proportion
  let navigationBarHeight = info.navigationBarHeight * info.proportion
  return {
    headerHeight: 'height: ' + (statusBarHeight + navigationBarHeight + 144) + 'rpx',
    topHeight: 'top: ' + info.custom.top + 'px',
    btnHeight: 'height: ' + (info.custom.height * info.proportion) + 'rpx',
    paddingHeight: 'padding-top: ' + (statusBarHeight + navigationBarHeight + 20) + 'rpx'
  }
})

const videoUrl = ref("");
const refreshVideoStream = () => {
  const timestamp = new Date().getTime();
  videoUrl.value = `http://172.20.10.11:5000/video_feed?_=${timestamp}`;
};

const foodData = ref([]);

const fetchDetections = async () => {
  try {
    const response = await http.post('http://172.20.10.3:5000/get_detections_json');
    console.log(response)
    foodData.value = response
    // 如果为空，则保留原数据不变
  } catch (error) {
    console.error('获取检测数据失败:', error);
    // 请求失败也保持原数据不变
  }
};

onMounted(() => {
  uni.login({
    success(res) {
      if (res.code) {
        console.log('code:', res.code)
        //发起网络请求
        http.get('http://172.20.10.3:6200/wx_login/' + res.code).then(res => {
          uni.setStorageSync('user', res)
        })
      } else {
        console.log('登录失败！' + res.errMsg)
      }
    }
  })

  refreshVideoStream();
  setInterval(fetchDetections, 1000);
});

</script>

<style lang="scss" scoped>
.container {
  width: 100vw;
  height: auto;
  min-height: 100vh;
  background: linear-gradient(180deg, #03ca6d 0%, #F6F6F6 100%);
}

.header {
  position: fixed;
  top: 0;
  width: 100vw;
  background: linear-gradient(180deg, #03ca6d 0%, #F6F6F6 100%);
}

.content {
  position: relative;
  width: 710rpx;
  height: auto;
  margin: 0 20rpx;
  z-index: 2;
}

.card {
  display: flex;
  flex-direction: column;
  width: 710rpx;
  height: auto;
  margin: 16rpx auto;
  padding: 16rpx;
  box-sizing: border-box;
  border-radius: 8rpx;
  background: #FFFFFF;

  .title {
    display: flex;
    justify-content: center;
    align-items: center;
    width: 100%;
    height: 80rpx;
  }
}

.c1 {
  height: 30vh;
}

.c2 {
  height: 25vh;
}

.control {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
  margin: 32rpx 0;

  .item {
    display: flex;
    color: #444444;
    font-size: 26rpx;
    border: 1rpx solid #03ca6d;
  }

  .btn {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 200rpx;
    height: 60rpx;
    letter-spacing: 8rpx;
    border-radius: 8rpx;
  }

  .circle {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 130rpx;
    height: 130rpx;
    border-radius: 50%;
  }
}

.card-title {
  text-align: center;
  font-size: 32rpx;
  font-weight: bold;
  color: #333;
  margin: 16rpx 0 8rpx 16rpx;
}

.camera-container {
  width: 100%;
  height: 100%;
  display: flex;
  justify-content: center;
  align-items: center;
}

.camera-feed {
  width: 100%;
  height: 100%;
  object-fit: contain;
}

.table-container {
  padding: 16rpx;
}

.table-header,
.table-row {
  display: flex;
  justify-content: space-between;
  border-bottom: 1rpx solid #eee;
  font-size: 24rpx;
  color: #666;
}

.table-header {
  font-weight: bold;
  color: #333;
  background-color: #f9f9f9;
}

.table-cell {
  flex: 1;
  text-align: center;
  padding: 12rpx 0;
  min-width: 150rpx;
}

.empty-result {
  text-align: center;
  padding: 40rpx;
  color: #999;
}

.loading-text {
  text-align: center;
  padding: 20rpx;
  color: #999;
}

</style>
