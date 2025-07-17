<template>
  <view class="container">
    <Nav :has-nav="false" title="" title-color="#444444"></Nav>
    <view :style="sysHeight.paddingHeight" class="content">
      <view class="card">
        <view class="name">{{ user.nickname }}</view>
        <view class="info">
          <view class="item">
            <text>年龄</text>
            <view class="start">
              <text style="margin-right: 20rpx">{{ user.age }}</text>
              <up-icon color="#444444" name="arrow-right" size="20"></up-icon>
            </view>
          </view>
          <view class="item">
            <text>性别</text>
            <view class="start">
              <text style="margin-right: 20rpx">{{ user.gender }}</text>
              <up-icon color="#444444" name="arrow-right" size="20"></up-icon>
            </view>
          </view>
          <view class="item">
            <text>体重</text>
            <view class="start">
              <text style="margin-right: 20rpx">{{ user.weight }}千克</text>
              <up-icon color="#444444" name="arrow-right" size="20"></up-icon>
            </view>
          </view>
          <view class="item">
            <text>身高</text>
            <view class="start">
              <text style="margin-right: 20rpx">{{ user.height }}厘米</text>
              <up-icon color="#444444" name="arrow-right" size="20"></up-icon>
            </view>
          </view>
          <view class="item">
            <text>偏好</text>
            <view class="start">
              <text style="margin-right: 20rpx">{{ user.preferences }}</text>
              <up-icon color="#444444" name="arrow-right" size="20"></up-icon>
            </view>
          </view>
          <view class="item">
            <text>慢性病</text>
            <view class="start">
              <text style="margin-right: 20rpx">{{ user.diseases }}</text>
              <up-icon color="#444444" name="arrow-right" size="20"></up-icon>
            </view>
          </view>
          <view class="item">
            <text>过敏源</text>
            <view class="start">
              <text style="margin-right: 20rpx">{{ user.allergies }}</text>
              <up-icon color="#444444" name="arrow-right" size="20"></up-icon>
            </view>
          </view>

        </view>
      </view>
    </view>
    <Tab :tab="3"/>
  </view>
</template>

<script setup>
import Nav from "@/components/nav.vue";
import Tab from "@/components/tabbar.vue";
import {onMounted} from "vue";
import {getUser} from "@/utils/store";

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
const user = ref({})

onMounted(() => {
  user.value = getUser()
})
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
  position: relative;
  display: flex;
  flex-direction: column;
  width: 710rpx;
  height: auto;
  margin: 16rpx auto;
  padding: 16rpx 0;
  box-sizing: border-box;
  border-radius: 8rpx;
  background: #FFFFFF;
  margin-top: 116rpx;

  .avatar {
    position: absolute;
    top: -100rpx;
    left: 305rpx;
    width: 100rpx;
    height: 100rpx;

    image {
      width: 100%;
      height: 100%;
      border-radius: 50%;
    }
  }

  .name {
    display: flex;
    justify-content: center;
    align-items: center;
    width: 100%;
    height: 100rpx;
    font-size: 30rpx;
    color: #444444;
    font-weight: 700;
    border-bottom: 1rpx solid #f1f1f1;
  }

  .info {
    display: flex;
    flex-direction: column;
    font-size: 26rpx;
    color: #444444;
    padding-bottom: 100rpx;
    box-sizing: border-box;

    .item {
      display: flex;
      align-items: center;
      justify-content: space-between;
      width: 100%;
      height: 80rpx;
      border-bottom: 1rpx solid #f1f1f1;

      text {
        padding-left: 16rpx;
      }

      :deep(.u-icon) {
        display: flex;
        margin-left: auto;
        padding-right: 16rpx;
      }
    }
  }
}
</style>
